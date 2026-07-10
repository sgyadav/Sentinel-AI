"""Password hashing utilities.

Uses PBKDF2-HMAC-SHA256 from the Python standard library and keeps
backward-compatible verification for older sha256 hashes already in local DBs.
"""

import hashlib
import hmac
import logging
import os

logger = logging.getLogger(__name__)

PBKDF2_ITERATIONS = 260000


def hash_password(password: str) -> str:
    """Hash a password with PBKDF2-HMAC-SHA256."""
    password = _normalize_password(password)
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )

    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}$"
        f"{salt.hex()}${digest.hex()}"
    )


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        plain_password = _normalize_password(plain_password)

        if hashed_password.startswith("pbkdf2_sha256$"):
            _, iterations, salt_hex, digest_hex = hashed_password.split("$", 3)
            expected = hashlib.pbkdf2_hmac(
                "sha256",
                plain_password.encode("utf-8"),
                bytes.fromhex(salt_hex),
                int(iterations),
            ).hex()

            return hmac.compare_digest(expected, digest_hex)

        if hashed_password.startswith("sha256:"):
            expected_hash = hashlib.sha256(
                plain_password.encode("utf-8")
            ).hexdigest()
            return hmac.compare_digest(
                hashed_password,
                f"sha256:{expected_hash}",
            )

        return False

    except Exception as exc:
        logger.error("Password verification error: %s", exc)
        return False


def _normalize_password(password: str) -> str:
    if len(password) > 128:
        logger.warning("Password longer than 128 characters was rejected")
        raise ValueError("Password must be 128 characters or fewer")

    return password
