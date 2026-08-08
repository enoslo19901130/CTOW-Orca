"""Runtime profile compilation and fail-closed bootstrap verification.

CTOW owns the policy contract, while Orca owns the process and terminal
lifecycle.  This module is deliberately limited to translating a CTOW agent
profile into Codex arguments and validating machine-readable launch receipts.
It does not spawn processes, create terminals, or maintain execution state.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


DEFAULT_SAFE_SANDBOX = "workspace-write"
DEFAULT_SAFE_APPROVAL = "on-request"
FULL_ACCESS_SANDBOX = "danger-full-access"
AUTO_APPROVAL = "never"

_REQUIRED_PROFILE_FIELDS = (
    "model",
    "reasoning_effort",
    "fast_mode",
    "full_access",
    "auto_approve",
)


class RuntimePolicyError(RuntimeError):
    """Base class for typed, fail-closed runtime policy failures."""

    code = "runtime_policy_error"

    def __init__(
        self,
        message: str,
        *,
        role: str | None = None,
        field: str | None = None,
        details: Mapping[str, Any] | None = None,
    ) -> None:
        self.role = role
        self.field = field
        self.details = dict(details or {})
        if role is not None:
            self.details.setdefault("role", role)
        if field is not None:
            self.details.setdefault("field", field)
        super().__init__(message)

    def as_dict(self) -> dict[str, Any]:
        return {
            "error_type": type(self).__name__,
            "code": self.code,
            "message": str(self),
            "details": dict(self.details),
        }


class ProfileCompilationError(RuntimePolicyError):
    """The requested profile cannot be expressed as a safe Codex launch."""

    code = "profile_compilation_failed"


class EffectivePolicyVerificationError(RuntimePolicyError):
    """A runtime receipt cannot prove the requested policy took effect."""

    code = "effective_policy_verification_failed"


class MissingEffectivePolicyError(EffectivePolicyVerificationError):
    """A required effective-policy field is absent from a launch receipt."""

    code = "effective_policy_missing"


class PolicyMismatchError(EffectivePolicyVerificationError):
    """A receipt reports an effective value different from the request."""

    code = "effective_policy_mismatch"


class BootstrapVerificationError(EffectivePolicyVerificationError):
    """Orca did not provide a verifiable bootstrap receipt."""

    code = "bootstrap_verification_failed"


# Kept as explicit aliases for callers that prefer shorter names.  The
# canonical class names above are used in error receipts and documentation.
PolicyVerificationError = EffectivePolicyVerificationError
RuntimeBootstrapError = BootstrapVerificationError


@dataclass(frozen=True)
class RuntimePolicy:
    """Canonical requested/effective Codex policy values.

    ``sandbox`` and ``approval`` are the concrete Codex policy values rather
    than CTOW booleans.  Keeping both forms in a receipt makes a false profile
    auditable and prevents a false value from being treated as an omitted
    (therefore potentially elevated) value.
    """

    role: str
    model: str
    reasoning_effort: str
    fast_mode: bool
    full_access: bool
    auto_approve: bool
    sandbox: str
    approval: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "role": self.role,
            "model": self.model,
            "reasoning_effort": self.reasoning_effort,
            "fast_mode": self.fast_mode,
            "full_access": self.full_access,
            "auto_approve": self.auto_approve,
            "sandbox": self.sandbox,
            "approval": self.approval,
        }


class CodexLaunch(dict[str, Any]):
    """Mapping returned by :func:`compile_codex_launch`.

    It is a mapping for JSON receipts and also exposes attributes for Python
    callers.  ``argv`` always includes the executable as its first item.
    """

    def __init__(
        self,
        *,
        argv: list[str],
        requested_policy: dict[str, Any],
        expected_effective_policy: dict[str, Any],
    ) -> None:
        super().__init__(
            argv=list(argv),
            requested_policy=requested_policy,
            expected_effective_policy=expected_effective_policy,
        )

    @property
    def argv(self) -> list[str]:
        return self["argv"]

    @property
    def requested_policy(self) -> dict[str, Any]:
        return self["requested_policy"]

    @property
    def expected_effective_policy(self) -> dict[str, Any]:
        return self["expected_effective_policy"]

    @property
    def policy(self) -> dict[str, Any]:
        """Backward-friendly alias for the requested policy."""

        return self.requested_policy

    @property
    def expected_policy(self) -> dict[str, Any]:
        """Short alias for the expected effective policy."""

        return self.expected_effective_policy

    @property
    def requested(self) -> dict[str, Any]:
        """Short alias used by Orca-style launch receipt consumers."""

        return self.requested_policy

    @property
    def effective(self) -> dict[str, Any]:
        """Expected effective values before a runtime receipt is verified."""

        return self.expected_effective_policy


def _required_value(profile: Mapping[str, Any], field: str, role: str) -> Any:
    if field not in profile:
        raise ProfileCompilationError(
            f"{role} profile is missing required field {field!r}",
            role=role,
            field=field,
        )
    return profile[field]


def _required_text(profile: Mapping[str, Any], field: str, role: str) -> str:
    value = _required_value(profile, field, role)
    if not isinstance(value, str) or not value.strip():
        raise ProfileCompilationError(
            f"{role} profile field {field!r} must be a non-empty string",
            role=role,
            field=field,
        )
    return value.strip()


def _required_bool(profile: Mapping[str, Any], field: str, role: str) -> bool:
    value = _required_value(profile, field, role)
    # bool is intentionally checked exactly: accepting 0/1 or a string here
    # could turn malformed policy into an accidental permission escalation.
    if type(value) is not bool:
        raise ProfileCompilationError(
            f"{role} profile field {field!r} must be a boolean",
            role=role,
            field=field,
        )
    return value


def _role_name(profile: Mapping[str, Any], role: str | None) -> str:
    if role:
        return role
    for key in ("profile_name", "name", "id", "role"):
        value = profile.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    # A profile can be compiled before it is assigned to a role.  The role is
    # metadata only; all security-relevant fields remain required below.
    return "unknown"


def _concrete_policy(
    profile: Mapping[str, Any],
    *,
    role: str | None = None,
) -> RuntimePolicy:
    resolved_role = _role_name(profile, role)
    for field in _REQUIRED_PROFILE_FIELDS:
        # Validate presence in one place so a profile cannot silently fall
        # back to Codex defaults for a required CTOW permission field.
        _required_value(profile, field, resolved_role)
    model = _required_text(profile, "model", resolved_role)
    effort = _required_text(profile, "reasoning_effort", resolved_role).lower()
    fast_mode = _required_bool(profile, "fast_mode", resolved_role)
    if fast_mode is not False:
        raise ProfileCompilationError(
            f"{resolved_role} profile requires Fast OFF (fast_mode=false)",
            role=resolved_role,
            field="fast_mode",
        )
    full_access = _required_bool(profile, "full_access", resolved_role)
    auto_approve = _required_bool(profile, "auto_approve", resolved_role)

    sandbox = profile.get("sandbox")
    if sandbox is None:
        sandbox = FULL_ACCESS_SANDBOX if full_access else DEFAULT_SAFE_SANDBOX
    if not isinstance(sandbox, str) or not sandbox.strip():
        raise ProfileCompilationError(
            f"{resolved_role} profile sandbox must be a non-empty string",
            role=resolved_role,
            field="sandbox",
        )
    sandbox = sandbox.strip()

    approval = profile.get("approval")
    if approval is None:
        approval = AUTO_APPROVAL if auto_approve else DEFAULT_SAFE_APPROVAL
    if not isinstance(approval, str) or not approval.strip():
        raise ProfileCompilationError(
            f"{resolved_role} profile approval must be a non-empty string",
            role=resolved_role,
            field="approval",
        )
    approval = approval.strip()

    # A profile's booleans must agree with explicitly supplied concrete
    # policies.  This prevents a hand-edited config from saying false while
    # still requesting an elevated Codex value.
    if full_access != (sandbox == FULL_ACCESS_SANDBOX):
        raise ProfileCompilationError(
            f"{resolved_role} full_access does not match sandbox policy {sandbox!r}",
            role=resolved_role,
            field="sandbox",
            details={"full_access": full_access, "sandbox": sandbox},
        )
    if auto_approve != (approval == AUTO_APPROVAL):
        raise ProfileCompilationError(
            f"{resolved_role} auto_approve does not match approval policy {approval!r}",
            role=resolved_role,
            field="approval",
            details={"auto_approve": auto_approve, "approval": approval},
        )
    if not full_access and sandbox == FULL_ACCESS_SANDBOX:
        raise ProfileCompilationError(
            f"{resolved_role} false full_access cannot request danger-full-access",
            role=resolved_role,
            field="sandbox",
        )
    if not auto_approve and approval == AUTO_APPROVAL:
        raise ProfileCompilationError(
            f"{resolved_role} false auto_approve cannot request approval never",
            role=resolved_role,
            field="approval",
        )

    return RuntimePolicy(
        role=resolved_role,
        model=model,
        reasoning_effort=effort,
        fast_mode=fast_mode,
        full_access=full_access,
        auto_approve=auto_approve,
        sandbox=sandbox,
        approval=approval,
    )


def compile_codex_launch(
    profile: Mapping[str, Any],
    role: str | None = None,
) -> CodexLaunch:
    """Compile a CTOW profile into explicit Codex argv and policy expectations.

    The compiler is pure.  It never launches Codex and never asks a parent
    process to elevate a false profile.  Safe concrete values are emitted for
    false permissions as well, so the runtime cannot silently choose a newer
    or different default.
    """

    requested = _concrete_policy(profile, role=role)
    argv = [
        "codex",
        "--model",
        requested.model,
        "-c",
        f"model_reasoning_effort={requested.reasoning_effort}",
        "--sandbox",
        requested.sandbox,
        "--ask-for-approval",
        requested.approval,
    ]
    requested_dict = requested.as_dict()
    return CodexLaunch(
        argv=argv,
        requested_policy=requested_dict,
        expected_effective_policy=dict(requested_dict),
    )


def compile_codex_argv(
    profile: Mapping[str, Any],
    role: str | None = None,
) -> list[str]:
    """Return only the compiled argv for integrations that need a list."""

    return list(compile_codex_launch(profile, role=role).argv)


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _find_effective_policy_subtree(
    receipt: Mapping[str, Any],
) -> tuple[Mapping[str, Any], str] | None:
    """Find one explicit effective-policy subtree without merging envelopes.

    Orca receipts may wrap the launch result in ``result``, ``bootstrap``, or
    ``launch`` objects.  The effective values must still come from one
    explicitly named ``effective``/``effective_policy`` mapping.  Requested
    siblings and unrelated top-level fields are never candidates.
    """

    effective_keys = (
        "effective_policy",
        "effective_runtime_policy",
        "effective_receipt",
        "effective",
    )
    wrapper_keys = (
        "result",
        "response",
        "data",
        "bootstrap",
        "terra_bootstrap",
        "launch",
        "receipt",
        "runtime",
        "runtime_policy",
        "policy",
    )
    seen: set[int] = set()

    def visit(mapping: Mapping[str, Any], path: str) -> tuple[Mapping[str, Any], str] | None:
        identity = id(mapping)
        if identity in seen:
            return None
        seen.add(identity)
        for key in effective_keys:
            candidate = _as_mapping(mapping.get(key))
            if candidate is not None:
                return candidate, f"{path}.{key}"
        for key in wrapper_keys:
            nested = _as_mapping(mapping.get(key))
            if nested is not None:
                found = visit(nested, f"{path}.{key}")
                if found is not None:
                    return found
        return None

    return visit(receipt, "receipt")


def _effective_value(
    subtree: Mapping[str, Any],
    keys: tuple[str, ...],
) -> Any:
    """Read a field from one effective subtree or its local permissions map."""

    for key in keys:
        if key in subtree:
            return subtree[key]
    permissions = _as_mapping(subtree.get("permissions"))
    if permissions is not None:
        for key in keys:
            if key in permissions:
                return permissions[key]
    return None


def _normalise_effective_policy(
    receipt: Mapping[str, Any],
    *,
    role: str,
) -> dict[str, Any]:
    found = _find_effective_policy_subtree(receipt)
    if found is None:
        return {"role": role}
    subtree, subtree_path = found
    model = _effective_value(subtree, ("model", "model_id"))
    effort = _effective_value(
        subtree,
        ("reasoning_effort", "effort", "model_reasoning_effort"),
    )
    sandbox = _effective_value(
        subtree,
        ("sandbox", "sandbox_policy", "sandbox_mode"),
    )
    approval = _effective_value(
        subtree,
        (
            "approval",
            "approval_policy",
            "ask_for_approval",
        ),
    )
    fast_mode = _effective_value(subtree, ("fast_mode", "fast"))
    full_access = _effective_value(subtree, ("full_access",))
    auto_approve = _effective_value(subtree, ("auto_approve",))
    permissions = subtree.get("permissions")

    # ``YOLO mode`` is a useful compatibility receipt for current Codex TUI
    # output, but structured sandbox/approval fields always take precedence.
    if isinstance(permissions, str) and permissions.casefold() in {
        "yolo",
        "yolo mode",
    }:
        if sandbox is None:
            sandbox = FULL_ACCESS_SANDBOX
        if approval is None:
            approval = AUTO_APPROVAL

    effective: dict[str, Any] = {"role": role, "receipt_subtree": subtree_path}
    if model is not None:
        effective["model"] = model.strip() if isinstance(model, str) else model
    if effort is not None:
        if isinstance(effort, str):
            cleaned_effort = effort.strip().strip('"').strip("'")
            if "=" in cleaned_effort:
                cleaned_effort = cleaned_effort.rsplit("=", 1)[-1]
            effective["reasoning_effort"] = cleaned_effort.strip().strip('"').strip("'").lower()
        else:
            effective["reasoning_effort"] = effort
    if fast_mode is not None:
        effective["fast_mode"] = fast_mode
    if sandbox is not None:
        effective["sandbox"] = sandbox.strip() if isinstance(sandbox, str) else sandbox
    if approval is not None:
        effective["approval"] = approval.strip() if isinstance(approval, str) else approval
    if full_access is not None:
        effective["full_access"] = full_access
    elif isinstance(sandbox, str):
        effective["full_access"] = sandbox == FULL_ACCESS_SANDBOX
    if auto_approve is not None:
        effective["auto_approve"] = auto_approve
    elif isinstance(approval, str):
        effective["auto_approve"] = approval == AUTO_APPROVAL
    return effective


def _requested_from_value(
    requested: Mapping[str, Any] | RuntimePolicy | CodexLaunch,
    *,
    role: str | None = None,
) -> dict[str, Any]:
    if isinstance(requested, RuntimePolicy):
        return requested.as_dict()
    if isinstance(requested, CodexLaunch):
        requested = requested.requested_policy
    if not isinstance(requested, Mapping):
        raise ProfileCompilationError("requested policy must be a profile or policy mapping")
    if isinstance(requested.get("requested_policy"), Mapping):
        requested = requested["requested_policy"]
    # A raw profile needs compilation.  A compiled requested-policy mapping
    # already has concrete sandbox/approval fields and can be verified as-is.
    if all(field in requested for field in ("model", "reasoning_effort", "fast_mode", "sandbox", "approval")):
        resolved_role = _role_name(requested, role)
        result = dict(requested)
        result["role"] = resolved_role
        result["reasoning_effort"] = str(result["reasoning_effort"]).lower()
        if "full_access" not in result:
            result["full_access"] = result["sandbox"] == FULL_ACCESS_SANDBOX
        if "auto_approve" not in result:
            result["auto_approve"] = result["approval"] == AUTO_APPROVAL
        return result
    return compile_codex_launch(requested, role=role).requested_policy


def verify_effective_policy(
    requested: Mapping[str, Any] | RuntimePolicy | CodexLaunch,
    receipt: Mapping[str, Any],
    *,
    role: str | None = None,
    runtime_verification: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Verify the complete effective runtime policy fail-closed.

    ``receipt`` must be machine-readable.  If a required field is missing, or
    a field differs from the requested policy, a typed error is raised instead
    of returning a downgraded success.  The returned mapping is safe to place
    in a CTOW launch receipt.
    """

    if not isinstance(receipt, Mapping):
        raise MissingEffectivePolicyError(
            "runtime launch receipt must be a mapping",
            role=role,
            details={"missing_fields": ["receipt"]},
        )
    requested_policy = _requested_from_value(requested, role=role)
    resolved_role = str(requested_policy.get("role") or role or "unknown")
    effective = _normalise_effective_policy(receipt, role=resolved_role)
    requirements = dict(runtime_verification or {})
    required_fields = {
        "model": requirements.get("require_effective_model_receipt", True),
        "reasoning_effort": requirements.get("require_effective_effort_receipt", True),
        "fast_mode": requirements.get("require_effective_fast_mode_receipt", True),
        "sandbox": requirements.get("require_effective_sandbox_receipt", True),
        "approval": requirements.get("require_effective_approval_receipt", True),
    }
    missing = [field for field, required in required_fields.items() if required and field not in effective]
    if missing:
        raise MissingEffectivePolicyError(
            f"{resolved_role} bootstrap receipt is missing effective policy fields: {', '.join(missing)}",
            role=resolved_role,
            details={
                "missing_fields": missing,
                "requested_policy": requested_policy,
                "effective_policy": effective,
            },
        )

    mismatches: dict[str, dict[str, Any]] = {}
    for field, required in required_fields.items():
        if not required or field not in effective:
            continue
        expected = requested_policy.get(field)
        actual = effective[field]
        if field == "reasoning_effort" and isinstance(actual, str):
            actual = actual.lower()
            effective[field] = actual
        if field in {"model", "reasoning_effort", "fast_mode", "sandbox", "approval"} and expected != actual:
            mismatches[field] = {"requested": expected, "effective": actual}

    # If a receipt carries booleans, check them too.  If it only carries
    # concrete sandbox/approval values the canonical booleans were derived
    # above, so false permissions cannot be accidentally elevated.
    for field in ("full_access", "auto_approve"):
        if field in effective and field in requested_policy and effective[field] != requested_policy[field]:
            mismatches[field] = {
                "requested": requested_policy[field],
                "effective": effective[field],
            }
    if "fast_mode" in effective and effective["fast_mode"] != requested_policy.get("fast_mode", False):
        mismatches["fast_mode"] = {
            "requested": requested_policy.get("fast_mode", False),
            "effective": effective["fast_mode"],
        }

    if mismatches:
        raise PolicyMismatchError(
            f"{resolved_role} effective runtime policy does not match the requested policy",
            role=resolved_role,
            details={
                "mismatches": mismatches,
                "requested_policy": requested_policy,
                "effective_policy": effective,
            },
        )

    return {
        "verified": True,
        "requested_policy": requested_policy,
        "effective_policy": effective,
        "verification": {
            "required_fields": [field for field, required in required_fields.items() if required],
            "checked_fields": [field for field in required_fields if field in effective],
            "fail_on_profile_downgrade": requirements.get("fail_on_profile_downgrade", True),
        },
    }


def verify_bootstrap_receipt(
    launch: Mapping[str, Any] | CodexLaunch,
    receipt: object | None,
    *,
    runtime_verification: Mapping[str, Any] | None = None,
    role: str | None = None,
) -> dict[str, Any]:
    """Verify a launch receipt and require an explicit bootstrap success.

    Orca may wrap terminal receipts differently across versions. CTOW accepts
    wrapper shapes only when they contain one explicit effective-policy
    subtree, but never treats a bare successful process/run-create response as
    proof of bootstrap.
    """

    if receipt is None or not isinstance(receipt, Mapping):
        raise BootstrapVerificationError(
            "Orca did not return a structured bootstrap receipt",
            role=role,
            details={"execution_started": False, "receipt": receipt},
        )
    if receipt.get("ok") is False or receipt.get("success") is False:
        raise BootstrapVerificationError(
            "Orca reported Terra bootstrap failure",
            role=role,
            details={"execution_started": False, "receipt": dict(receipt)},
        )
    if _find_effective_policy_subtree(receipt) is None:
        raise BootstrapVerificationError(
            "Orca did not return an explicit effective bootstrap policy",
            role=role,
            details={
                "execution_started": False,
                "missing_fields": ["effective_policy"],
                "receipt": dict(receipt),
            },
        )
    result = verify_effective_policy(
        launch,
        receipt,
        role=role,
        runtime_verification=runtime_verification,
    )
    if receipt.get("bootstrap_verified") is False or receipt.get("verified") is False:
        raise BootstrapVerificationError(
            "Orca reported an unverified Terra bootstrap",
            role=role,
            details={"execution_started": False, "receipt": dict(receipt)},
        )
    result["bootstrap_verified"] = True
    return result
