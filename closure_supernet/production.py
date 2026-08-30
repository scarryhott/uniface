from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections import defaultdict, deque
from dataclasses import dataclass
from http.cookies import SimpleCookie
from typing import Any

import jwt
from jwt import PyJWKClient
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send


ROLE_LEVEL = {"anonymous": 0, "member": 1, "operator": 2}
WRITE_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
AUTHOR_FIELDS = {
    "author_id",
    "authored_by",
    "created_by",
    "decided_by",
    "generated_by",
    "actor_id",
    "recorded_by",
}
PUBLIC_PREFIXES = (
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/livez",
    "/readyz",
    "/production",
    "/auth/login",
    "/auth/logout",
    "/auth/session",
)
OPERATOR_PREFIXES = (
    "/runtime",
    "/bootstrap",
    "/rules",
    "/integrations",
    "/admin",
)


@dataclass(frozen=True, slots=True)
class Principal:
    subject: str
    role: str
    participant_id: str | None = None
    scopes: tuple[str, ...] = ()
    source: str = "anonymous"
    authenticated: bool = False

    @property
    def level(self) -> int:
        return ROLE_LEVEL.get(self.role, 0)

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "role": self.role,
            "participant_id": self.participant_id,
            "scopes": list(self.scopes),
            "source": self.source,
            "authenticated": self.authenticated,
        }


class Authenticator:
    def __init__(self, config: Any):
        self.config = config
        self.mode = str(config.auth_mode).strip().lower()
        if self.mode not in {"open", "api_key", "jwt", "hybrid"}:
            raise ValueError("CLOSURE_AUTH_MODE must be open, api_key, jwt, or hybrid")
        self.api_keys = self._parse_api_keys(config.auth_api_keys_json)
        self._jwk_client = PyJWKClient(config.auth_jwks_url) if config.auth_jwks_url else None

    @staticmethod
    def _parse_api_keys(raw: str) -> dict[str, Principal]:
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("CLOSURE_AUTH_API_KEYS_JSON must be a JSON object")
        result: dict[str, Principal] = {}
        for key, claims in parsed.items():
            if not isinstance(key, str) or not key:
                raise ValueError("API key entries must have non-empty string keys")
            if isinstance(claims, str):
                claims = {"subject": claims, "role": "member"}
            if not isinstance(claims, dict):
                raise ValueError("API key claims must be objects")
            role = str(claims.get("role", "member"))
            if role not in ROLE_LEVEL:
                raise ValueError(f"Unsupported API key role: {role}")
            scopes = claims.get("scopes", [])
            if not isinstance(scopes, list):
                raise ValueError("API key scopes must be a list")
            result[key] = Principal(
                subject=str(claims.get("subject", "member")),
                role=role,
                participant_id=(
                    None
                    if claims.get("participant_id") in (None, "")
                    else str(claims["participant_id"])
                ),
                scopes=tuple(str(item) for item in scopes),
                source="api_key",
                authenticated=True,
            )
        return result

    def authenticate(self, scope: Scope) -> Principal:
        if self.mode == "open":
            return Principal(
                subject="development-open",
                role="operator",
                source="open",
                authenticated=False,
            )
        headers = {
            key.decode("latin-1").lower(): value.decode("latin-1")
            for key, value in scope.get("headers", [])
        }
        cookie_token = self._cookie_token(headers.get("cookie"))
        if cookie_token:
            principal = self._decode_session(cookie_token)
            if principal is not None:
                return principal
        auth_header = headers.get("authorization", "")
        if auth_header.lower().startswith("bearer "):
            token = auth_header[7:].strip()
            principal = self._decode_external_jwt(token)
            if principal is not None:
                return principal
        api_key = headers.get("x-closure-api-key")
        if api_key and self.mode in {"api_key", "hybrid"}:
            principal = self._match_api_key(api_key)
            if principal is not None:
                return principal
        return Principal(subject="anonymous", role="anonymous")

    def authenticate_api_key(self, api_key: str) -> Principal | None:
        if self.mode not in {"api_key", "hybrid"}:
            return None
        return self._match_api_key(api_key)

    def _match_api_key(self, candidate: str) -> Principal | None:
        candidate_bytes = candidate.encode("utf-8")
        for configured, principal in self.api_keys.items():
            if hmac.compare_digest(candidate_bytes, configured.encode("utf-8")):
                return principal
        return None

    @staticmethod
    def _cookie_token(cookie_header: str | None) -> str | None:
        if not cookie_header:
            return None
        cookie = SimpleCookie()
        try:
            cookie.load(cookie_header)
        except Exception:
            return None
        item = cookie.get("closure_session")
        return None if item is None else item.value

    def issue_session(self, principal: Principal) -> str:
        if not self.config.session_secret:
            raise RuntimeError("CLOSURE_SESSION_SECRET is required to issue sessions")
        now = int(time.time())
        payload = {
            "sub": principal.subject,
            "role": principal.role,
            "participant_id": principal.participant_id,
            "scopes": list(principal.scopes),
            "iss": "closure-supernet",
            "aud": "closure-supernet-session",
            "iat": now,
            "exp": now + int(self.config.session_ttl_seconds),
        }
        return jwt.encode(payload, self.config.session_secret, algorithm="HS256")

    def _decode_session(self, token: str) -> Principal | None:
        if not self.config.session_secret:
            return None
        try:
            claims = jwt.decode(
                token,
                self.config.session_secret,
                algorithms=["HS256"],
                issuer="closure-supernet",
                audience="closure-supernet-session",
            )
        except jwt.PyJWTError:
            return None
        return self._principal_from_claims(claims, "session")

    def _decode_external_jwt(self, token: str) -> Principal | None:
        if self.mode not in {"jwt", "hybrid"}:
            return None
        try:
            if self._jwk_client is not None:
                signing_key = self._jwk_client.get_signing_key_from_jwt(token).key
                claims = jwt.decode(
                    token,
                    signing_key,
                    algorithms=list(self.config.auth_jwt_algorithms),
                    issuer=self.config.auth_issuer or None,
                    audience=self.config.auth_audience or None,
                    options={"verify_aud": bool(self.config.auth_audience)},
                )
            elif self.config.auth_jwt_secret:
                claims = jwt.decode(
                    token,
                    self.config.auth_jwt_secret,
                    algorithms=list(self.config.auth_jwt_algorithms),
                    issuer=self.config.auth_issuer or None,
                    audience=self.config.auth_audience or None,
                    options={"verify_aud": bool(self.config.auth_audience)},
                )
            else:
                return None
        except (jwt.PyJWTError, ValueError):
            return None
        return self._principal_from_claims(claims, "jwt")

    @staticmethod
    def _principal_from_claims(claims: dict[str, Any], source: str) -> Principal | None:
        subject = claims.get("sub")
        if not subject:
            return None
        role = str(claims.get("role", claims.get("app_role", "member")))
        if role not in ROLE_LEVEL:
            role = "member"
        scopes = claims.get("scopes", claims.get("scope", []))
        if isinstance(scopes, str):
            scopes = scopes.split()
        if not isinstance(scopes, list):
            scopes = []
        participant_id = claims.get("participant_id")
        return Principal(
            subject=str(subject),
            role=role,
            participant_id=None if participant_id in (None, "") else str(participant_id),
            scopes=tuple(str(item) for item in scopes),
            source=source,
            authenticated=True,
        )

    def readiness(self) -> tuple[bool, list[str]]:
        problems: list[str] = []
        if self.mode == "api_key" and not self.api_keys:
            problems.append("no API keys configured")
        if self.mode == "jwt" and not self._jwk_client and not self.config.auth_jwt_secret:
            problems.append("no JWT verification key configured")
        if self.mode != "open" and not self.config.session_secret:
            problems.append("no session secret configured")
        return not problems, problems


class SlidingWindowLimiter:
    def __init__(self, limit: int, window_seconds: int = 60):
        self.limit = max(1, int(limit))
        self.window_seconds = max(1, int(window_seconds))
        self._entries: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> tuple[bool, int]:
        now = time.monotonic()
        queue = self._entries[key]
        boundary = now - self.window_seconds
        while queue and queue[0] <= boundary:
            queue.popleft()
        if len(queue) >= self.limit:
            retry = max(1, int(self.window_seconds - (now - queue[0])))
            return False, retry
        queue.append(now)
        return True, 0


class ProductionSecurityMiddleware:
    def __init__(
        self,
        app: ASGIApp,
        config: Any,
        event_store: Any,
        authenticator: Authenticator | None = None,
    ):
        self.app = app
        self.config = config
        self.event_store = event_store
        self.authenticator = authenticator or Authenticator(config)
        self.read_limiter = SlidingWindowLimiter(config.rate_limit_read_per_minute)
        self.write_limiter = SlidingWindowLimiter(config.rate_limit_write_per_minute)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return
        request_id = self._header(scope, "x-request-id") or str(uuid.uuid4())
        scope.setdefault("state", {})["request_id"] = request_id
        principal = self.authenticator.authenticate(scope)
        scope["state"]["principal"] = principal.to_public_dict()
        path = scope.get("path", "")
        method = scope.get("method", "GET").upper()
        required_role = self._required_role(path, method, scope["type"])
        if principal.level < ROLE_LEVEL[required_role]:
            await self._reject(
                scope,
                receive,
                send,
                401 if not principal.authenticated else 403,
                "authentication required" if not principal.authenticated else "insufficient role",
            )
            return

        client = scope.get("client")
        client_host = "unknown" if not client else str(client[0])
        limiter_key = f"{principal.subject}:{client_host}:{'write' if method in WRITE_METHODS else 'read'}"
        limiter = self.write_limiter if method in WRITE_METHODS else self.read_limiter
        allowed, retry = limiter.allow(limiter_key)
        if not allowed:
            await self._reject(
                scope,
                receive,
                send,
                429,
                "rate limit exceeded",
                {"Retry-After": str(retry)},
            )
            return

        replay_receive = receive
        if scope["type"] == "http" and method in WRITE_METHODS:
            try:
                body = await self._read_body(receive)
            except ValueError as exc:
                await self._reject(scope, receive, send, 413, str(exc))
                return
            binding_error = self._binding_error(
                path, principal, body, self._header(scope, "content-type")
            )
            if binding_error:
                await self._reject(scope, receive, send, 403, binding_error)
                return
            replay_receive = self._replay(body)

        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                self._set_header(headers, b"x-request-id", request_id.encode())
                self._set_header(headers, b"x-content-type-options", b"nosniff")
                self._set_header(headers, b"referrer-policy", b"same-origin")
                self._set_header(
                    headers,
                    b"permissions-policy",
                    b"camera=(), microphone=(), geolocation=()",
                )
                self._set_header(
                    headers,
                    b"content-security-policy",
                    self.config.content_security_policy.encode(),
                )
                if self.config.environment == "production":
                    self._set_header(
                        headers,
                        b"strict-transport-security",
                        b"max-age=31536000; includeSubDomains",
                    )
                message["headers"] = headers
            await send(message)

        await self.app(
            scope,
            replay_receive,
            send_wrapper if scope["type"] == "http" else send,
        )
        if scope["type"] == "http" and method in WRITE_METHODS:
            try:
                self.event_store.append_event(
                    "PRODUCTION_REQUEST",
                    "request",
                    request_id,
                    {
                        "method": method,
                        "path": path,
                        "status": status_code,
                        "subject": principal.subject,
                        "role": principal.role,
                        "participant_id": principal.participant_id,
                    },
                )
            except Exception:
                pass

    def _required_role(self, path: str, method: str, scope_type: str) -> str:
        if self.config.auth_mode == "open":
            return "anonymous"
        if path.startswith("/integrations/") and path.endswith("/webhook"):
            return "anonymous"
        if any(path == prefix or path.startswith(prefix + "/") for prefix in PUBLIC_PREFIXES):
            return "anonymous"
        if path == "/" or path in {"/translation", "/resources", "/reopening", "/equality"}:
            return "anonymous" if self.config.allow_anonymous_read else "member"
        if any(path == prefix or path.startswith(prefix + "/") for prefix in OPERATOR_PREFIXES):
            return "operator"
        if scope_type == "websocket":
            return "member"
        if method in {"GET", "HEAD", "OPTIONS"}:
            return "anonymous" if self.config.allow_anonymous_read else "member"
        if path == "/network/participants" and method == "POST" and self.config.allow_self_registration:
            return "anonymous"
        if method in WRITE_METHODS and self.config.allow_anonymous_write:
            return "anonymous"
        return "member"

    def _binding_error(
        self,
        path: str,
        principal: Principal,
        body: bytes,
        content_type: str | None,
    ) -> str | None:
        if (
            principal.role == "operator"
            or principal.participant_id is None
            or not body
        ):
            return None
        if not content_type or "application/json" not in content_type.lower():
            return None
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            return None
        if self.config.public_only_mode and isinstance(parsed, dict):
            visibility = parsed.get("visibility")
            if visibility not in (None, "PUBLIC", "PSEUDONYMOUS_PUBLIC"):
                return "non-public visibility is disabled until production ACL storage is enabled"
        values = self._author_values(parsed)
        if path == "/network/perspectives" and isinstance(parsed, dict):
            value = parsed.get("participant_id")
            if isinstance(value, str):
                values.append(("participant_id", value))
        for field, value in values:
            if value != principal.participant_id:
                return f"{field} must match the authenticated participant"
        return None

    @classmethod
    def _author_values(cls, value: Any) -> list[tuple[str, str]]:
        result: list[tuple[str, str]] = []
        if isinstance(value, dict):
            for key, item in value.items():
                if key in AUTHOR_FIELDS and isinstance(item, str):
                    result.append((key, item))
                else:
                    result.extend(cls._author_values(item))
        elif isinstance(value, list):
            for item in value:
                result.extend(cls._author_values(item))
        return result

    async def _read_body(self, receive: Receive) -> bytes:
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] != "http.request":
                continue
            body.extend(message.get("body", b""))
            if len(body) > self.config.max_request_bytes:
                raise ValueError("request body exceeds production limit")
            if not message.get("more_body", False):
                break
        return bytes(body)

    @staticmethod
    def _replay(body: bytes) -> Receive:
        sent = False

        async def receive() -> Message:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        return receive

    @staticmethod
    def _header(scope: Scope, name: str) -> str | None:
        target = name.lower().encode("latin-1")
        for key, value in scope.get("headers", []):
            if key.lower() == target:
                return value.decode("latin-1")
        return None

    @staticmethod
    def _set_header(headers: list[tuple[bytes, bytes]], name: bytes, value: bytes) -> None:
        lowered = name.lower()
        headers[:] = [(key, val) for key, val in headers if key.lower() != lowered]
        headers.append((name, value))

    async def _reject(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        status: int,
        detail: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        if scope["type"] == "websocket":
            await send({"type": "websocket.close", "code": 4401 if status == 401 else 4403})
            return
        merged = dict(headers or {})
        request_id = scope.get("state", {}).get("request_id")
        if request_id:
            merged.setdefault("X-Request-ID", str(request_id))
        merged.setdefault("X-Content-Type-Options", "nosniff")
        response = JSONResponse({"detail": detail}, status_code=status, headers=merged)
        await response(scope, receive, send)
