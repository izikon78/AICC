"""Scoped reusable bindings for an in-process AICC research host.

This module checks declared compatibility and host-managed state. It is not an
authentication service, effect sandbox, signature verifier, or security boundary.
"""
from dataclasses import dataclass, replace
import hashlib
import json
import marshal
import math
import platform
import sys
import time
import types


class CapabilityError(Exception):
    """Base class for explicit reuse decisions."""


class PermissionDenied(CapabilityError):
    pass


class StaleBinding(CapabilityError):
    pass


class IncompatibleCapability(CapabilityError):
    pass


class ReuseUnknown(CapabilityError):
    pass


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _digest(value):
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _normalized_code(code):
    constants = tuple(_normalized_code(c) if isinstance(c, types.CodeType) else c for c in code.co_consts)
    return code.replace(co_filename="", co_firstlineno=1, co_linetable=b"", co_consts=constants,
                        co_qualname=code.co_name)


def _defaults(function):
    values = tuple(function.__defaults__ or ())
    keywords = tuple(sorted((function.__kwdefaults__ or {}).items()))
    def immutable(value):
        if isinstance(value, tuple):
            return all(immutable(v) for v in value)
        return value is None or isinstance(value, (str, int, bool)) or (
            isinstance(value, float) and math.isfinite(value))
    if not all(immutable(v) for v in values) or not all(immutable(v) for _, v in keywords):
        raise ValueError("mutable or non-finite function defaults are unsupported")
    return values, keywords


def artifact_digest(function, dependencies=None, precondition=None):
    """Hash loaded function code/defaults plus explicitly declared dependencies.

    Declarations must cover transitive helpers/data; arbitrary global mutations
    are not automatically discovered. Interpreter identity belongs to environment.
    """
    if not isinstance(function, types.FunctionType) or function.__closure__:
        raise TypeError("capabilities must be plain Python functions without closures")
    code = marshal.dumps(_normalized_code(function.__code__))
    manifest = _canonical({"defaults": _defaults(function), "dependencies": dependencies or {}})
    guard = b"" if precondition is None else artifact_digest(precondition).encode("ascii")
    return hashlib.sha256(code + b"\0" + manifest.encode("utf-8") + (b"\0guard:" + guard if guard else b"")).hexdigest()


@dataclass(frozen=True)
class Capability:
    capability_id: str
    function: object
    contract_version: str
    contract_digest: str
    artifact_digest: str
    obligations: frozenset
    properties_json: str
    effects: frozenset
    scope: str
    dependencies_json: str
    revision: int
    code: object
    defaults: tuple
    precondition: object = None
    precondition_code: object = None
    precondition_defaults: tuple = ()


@dataclass(frozen=True)
class _Grant:
    scopes: frozenset
    effects: frozenset
    revision: int


class Binding:
    def __init__(self, runtime, capability, principal, scopes, effects, obligations, requirements, expires):
        self._runtime, self._capability = runtime, capability
        self._principal, self._scopes, self._effects = principal, scopes, effects
        self._obligations, self._requirements = obligations, _canonical(requirements)
        self._expires = expires
        self._grant_revision = runtime._grants[principal].revision
        self._environment_revision = runtime._environment_revision

    @property
    def capability_id(self):
        return self._capability.capability_id

    def _check(self):
        runtime, cap = self._runtime, self._capability
        if runtime._clock() >= self._expires:
            raise StaleBinding("binding expired")
        if cap.capability_id in runtime._revoked:
            raise StaleBinding("capability revoked")
        if runtime._caps.get(cap.capability_id) is not cap:
            raise StaleBinding("capability or declared dependencies changed")
        if runtime._environment_revision != self._environment_revision:
            raise StaleBinding("environment changed")
        if runtime._grants.get(self._principal, None) is None or runtime._grants[self._principal].revision != self._grant_revision:
            raise StaleBinding("principal policy changed")
        try:
            defaults_changed = _defaults(cap.function) != cap.defaults
        except (TypeError, ValueError):
            defaults_changed = True
        if cap.function.__code__ is not cap.code or defaults_changed:
            raise StaleBinding("loaded function changed outside registry")
        if cap.precondition is not None:
            try:
                guard_changed = _defaults(cap.precondition) != cap.precondition_defaults
            except (TypeError, ValueError):
                guard_changed = True
            if cap.precondition.__code__ is not cap.precondition_code or guard_changed:
                raise StaleBinding("call precondition changed outside registry")

    def __call__(self, *args, **kwargs):
        self._check()
        if self._capability.precondition is not None:
            verdict = self._capability.precondition(*args, **kwargs)
            if verdict is None:
                raise ReuseUnknown("call precondition could not be established")
            if verdict is not True:
                raise IncompatibleCapability("call precondition failed")
        return self._capability.function(*args, **kwargs)

    def export_record(self):
        """Export evidence identity only; never serialize a function or credential."""
        self._check()
        cap = self._capability
        return {"record_version": 1, "capability_id": cap.capability_id,
                "contract_digest": cap.contract_digest, "artifact_digest": cap.artifact_digest,
                "environment_digest": _digest(self._runtime._environment),
                "obligations": sorted(self._obligations), "requirements": json.loads(self._requirements),
                "required_scope": cap.scope, "required_effects": sorted(cap.effects)}


class Runtime:
    def __init__(self, environment=None, clock=time.monotonic):
        self._clock = clock
        self._environment = _canonical(environment if environment is not None else {
            "python": platform.python_version(), "implementation": platform.python_implementation(), "platform": sys.platform})
        self._environment_revision = 0
        self._caps, self._revoked = {}, set()
        self._grants = {"anonymous": _Grant(frozenset(), frozenset(), 0)}
        self.full_validations = 0
        self.validation_cache_hits = 0
        self._validated = set()

    def authorize(self, principal, *, scopes=(), allowed_effects=()):
        """Trusted host action; changing one principal invalidates only its bindings."""
        scopes, effects = frozenset(scopes), frozenset(allowed_effects)
        old = self._grants.get(principal)
        if old and old.scopes == scopes and old.effects == effects:
            return
        self._grants[principal] = _Grant(scopes, effects, 0 if old is None else old.revision + 1)

    def set_environment(self, environment):
        encoded = _canonical(environment)
        if encoded != self._environment:
            self._environment, self._environment_revision = encoded, self._environment_revision + 1

    def register(self, capability_id, function, *, contract_version="1", contract_digest=None,
                 obligations=(), properties=None, effects=(), scope="public", dependencies=None,
                 expected_artifact_digest=None, precondition=None):
        if not isinstance(capability_id, str) or not capability_id:
            raise ValueError("capability_id must be nonempty")
        obligations, effects = frozenset(obligations), frozenset(effects)
        properties_json, dependencies_json = _canonical(properties or {}), _canonical(dependencies or {})
        identity = artifact_digest(function, json.loads(dependencies_json), precondition)
        if expected_artifact_digest is not None and identity != expected_artifact_digest:
            raise IncompatibleCapability("loaded artifact does not match expected identity")
        contract = contract_digest or _digest(_canonical({"version": contract_version, "obligations": sorted(obligations),
                    "properties": json.loads(properties_json), "effects": sorted(effects), "scope": scope}))
        previous = self._caps.get(capability_id)
        cap = Capability(capability_id, function, str(contract_version), contract, identity, obligations,
                         properties_json, effects, scope, dependencies_json, 1 if previous is None else previous.revision + 1,
                         function.__code__, _defaults(function), precondition,
                         None if precondition is None else precondition.__code__,
                         () if precondition is None else _defaults(precondition))
        self._caps[capability_id] = cap
        return cap

    def update_dependencies(self, capability_id, dependencies):
        old = self._caps[capability_id]
        encoded = _canonical(dependencies)
        if encoded != old.dependencies_json:
            self._caps[capability_id] = replace(old, dependencies_json=encoded,
                artifact_digest=artifact_digest(old.function, dependencies, old.precondition), revision=old.revision + 1)
        return self._caps[capability_id]

    def get_capability(self, capability_id):
        return self._caps[capability_id]

    def revoke(self, capability_id):
        if capability_id not in self._caps:
            raise KeyError(capability_id)
        self._revoked.add(capability_id)

    def unrevoke(self, capability_id):
        self._revoked.discard(capability_id)
        cap = self._caps[capability_id]
        self._caps[capability_id] = replace(cap, revision=cap.revision + 1)

    def bind(self, capability_id, *, principal="anonymous", scopes=(), allowed_effects=(), obligations=(),
             requirements=None, ttl_seconds=600, expected_contract_digest=None, expected_artifact_digest=None):
        if isinstance(ttl_seconds, bool) or not isinstance(ttl_seconds, (int, float)) or not math.isfinite(ttl_seconds) or ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive and finite")
        cap = self._caps.get(capability_id)
        if cap is None:
            raise ReuseUnknown("capability is not registered")
        if capability_id in self._revoked:
            raise PermissionDenied("capability revoked")
        scopes, effects, obligations = frozenset(scopes), frozenset(allowed_effects), frozenset(obligations)
        grant = self._grants.get(principal)
        if grant is None or not scopes.issubset(grant.scopes) or not effects.issubset(grant.effects):
            raise PermissionDenied("requested authority exceeds host grant")
        if cap.scope != "public" and cap.scope not in scopes:
            raise PermissionDenied("required scope not requested")
        if not cap.effects.issubset(effects):
            raise PermissionDenied("required effects not permitted")
        requirements = dict(requirements or {})
        if expected_contract_digest is not None and cap.contract_digest != expected_contract_digest:
            raise IncompatibleCapability("contract identity differs")
        actual = artifact_digest(cap.function, json.loads(cap.dependencies_json), cap.precondition)
        if actual != cap.artifact_digest or (expected_artifact_digest is not None and actual != expected_artifact_digest):
            raise IncompatibleCapability("loaded artifact identity differs")
        key = (capability_id, cap.revision, cap.contract_digest, actual, self._environment_revision,
               principal, grant.revision, tuple(sorted(scopes)), tuple(sorted(effects)),
               tuple(sorted(obligations)), _canonical(requirements))
        if key in self._validated:
            self.validation_cache_hits += 1
        else:
            properties = json.loads(cap.properties_json)
            if not obligations.issubset(cap.obligations):
                raise ReuseUnknown("requested obligations lack declared evidence")
            if any(name not in properties for name in requirements):
                raise ReuseUnknown("requested property is unspecified")
            if any(_canonical(properties[name]) != _canonical(value) for name, value in requirements.items()):
                raise IncompatibleCapability("requested property differs")
            self.full_validations += 1
            if len(self._validated) >= 1024:
                self._validated.clear()
            self._validated.add(key)
        return Binding(self, cap, principal, scopes, effects, obligations, requirements, self._clock() + ttl_seconds)

    def restore(self, record, *, principal, scopes=(), allowed_effects=(), ttl_seconds=600,
                requirements=None, obligations=None):
        """Revalidate record hints plus trusted receiving-task requirements.

        Omitted receiver requirements preserve record-only compatibility, not a
        claim that an unspecified receiving task is satisfied.
        """
        if record.get("record_version") != 1:
            raise ReuseUnknown("unsupported record version")
        if record.get("environment_digest") != _digest(self._environment):
            raise IncompatibleCapability("handoff environment differs")
        merged_requirements = dict(record.get("requirements", {}))
        for name, value in dict(requirements or {}).items():
            if name in merged_requirements and _canonical(merged_requirements[name]) != _canonical(value):
                raise IncompatibleCapability("handoff requirements conflict with receiving task")
            merged_requirements[name] = value
        merged_obligations = set(record.get("obligations", ())) | set(obligations or ())
        binding = self.bind(record["capability_id"], principal=principal, scopes=scopes,
            allowed_effects=allowed_effects, obligations=merged_obligations,
            requirements=merged_requirements, ttl_seconds=ttl_seconds,
            expected_contract_digest=record["contract_digest"], expected_artifact_digest=record["artifact_digest"])
        cap = binding._capability
        if record.get("required_scope") != cap.scope or set(record.get("required_effects", ())) != set(cap.effects):
            raise IncompatibleCapability("handoff policy metadata differs")
        return binding
