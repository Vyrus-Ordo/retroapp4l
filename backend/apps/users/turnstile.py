import json
import urllib.parse
import urllib.request

from django.conf import settings


def verify_turnstile(token: str, ip: str | None = None) -> bool:
    """Verify a Cloudflare Turnstile token against the siteverify API.

    Returns True automatically when CLOUDFLARE_TURNSTILE_SECRET_KEY is empty,
    allowing development and test environments to bypass the check.
    """
    secret_key: str = getattr(settings, "CLOUDFLARE_TURNSTILE_SECRET_KEY", "")
    if not secret_key:
        return True

    payload: dict[str, str] = {"secret": secret_key, "response": token}
    if ip:
        payload["remoteip"] = ip

    data = urllib.parse.urlencode(payload).encode()
    req = urllib.request.Request(
        "https://challenges.cloudflare.com/turnstile/v0/siteverify",
        data=data,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:  # noqa: S310
            result = json.loads(resp.read().decode())
            return bool(result.get("success"))
    except Exception:
        return False
