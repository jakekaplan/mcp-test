import hashlib
import hmac
import os
from typing import Literal

from fastmcp import FastMCP

_secret = os.environ.get("E2E_CHALLENGE_SECRET")
if not _secret:
    raise RuntimeError("E2E_CHALLENGE_SECRET must be set and nonempty")
_secret = _secret.encode("utf-8")

mcp = FastMCP(name="Agent Runtime E2E")


def _challenge(run_id: str, phase: Literal["initial", "follow-up"]) -> str:
    return hmac.new(
        _secret, f"{run_id}:{phase}".encode("utf-8"), hashlib.sha256
    ).hexdigest()[:24]


@mcp.tool
def get_challenge(
    run_id: str, phase: Literal["initial", "follow-up"]
) -> dict[str, str]:
    """Get the deterministic challenge for a run and phase."""
    return {
        "run_id": run_id,
        "phase": phase,
        "challenge": _challenge(run_id, phase),
    }


@mcp.tool
def verify_artifact(
    run_id: str,
    phase: Literal["initial", "follow-up"],
    content: str,
    sha256: str,
) -> dict[str, str | bool]:
    """Verify exact artifact content and its SHA-256, including the trailing newline."""
    expected_content = f"challenge={_challenge(run_id, phase)}\nphase={phase}\n"
    expected_sha256 = hashlib.sha256(expected_content.encode("utf-8")).hexdigest()
    return {
        "valid": content == expected_content and sha256 == expected_sha256,
        "expected_content": expected_content,
        "expected_sha256": expected_sha256,
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http", stateless_http=True)
