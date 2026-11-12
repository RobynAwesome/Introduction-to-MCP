"""Dependency-free RFC 8032 Ed25519 implementation using Python stdlib only.

Used by capability_lease.py and agent_failure_training.py so zero-trust CI
lanes without third-party wheels can strictly separate private signing authority
from public verification keys.
"""

from __future__ import annotations

import hashlib
import secrets

_P = 2**255 - 19
_L = 2**252 + 27742317777372353535851937790883648493


def _inv(x: int) -> int:
    return pow(x, _P - 2, _P)


_D = (-121665 * _inv(121666)) % _P
_I = pow(2, (_P - 1) // 4, _P)


def _xrecover(y: int) -> int | None:
    xx = (y * y - 1) * _inv(_D * y * y + 1) % _P
    if xx == 0:
        return 0
    x = pow(xx, (_P + 3) // 8, _P)
    if (x * x - xx) % _P != 0:
        x = (x * _I) % _P
    if (x * x - xx) % _P != 0:
        return None
    if x & 1:
        x = _P - x
    return x


_BY = (4 * _inv(5)) % _P
_BX = _xrecover(_BY)
assert _BX is not None
_B = (_BX, _BY, 1, (_BX * _BY) % _P)
_ID = (0, 1, 1, 0)


def _point_add(
    p: tuple[int, int, int, int],
    q: tuple[int, int, int, int],
) -> tuple[int, int, int, int]:
    x1, y1, z1, t1 = p
    x2, y2, z2, t2 = q
    a = (y1 - x1) * (y2 - x2) % _P
    b = (y1 + x1) * (y2 + x2) % _P
    c = 2 * _D * t1 * t2 % _P
    d = 2 * z1 * z2 % _P
    e = (b - a) % _P
    f = (d - c) % _P
    g = (d + c) % _P
    h = (b + a) % _P
    return (
        e * f % _P,
        g * h % _P,
        f * g % _P,
        e * h % _P,
    )


def _point_mul(s: int, p: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    q = _ID
    while s > 0:
        if s & 1:
            q = _point_add(q, p)
        p = _point_add(p, p)
        s >>= 1
    return q


def _point_equal(p: tuple[int, int, int, int], q: tuple[int, int, int, int]) -> bool:
    x1, y1, z1, _ = p
    x2, y2, z2, _ = q
    return ((x1 * z2 - x2 * z1) % _P == 0) and ((y1 * z2 - y2 * z1) % _P == 0)


def _point_compress(p: tuple[int, int, int, int]) -> bytes:
    x, y, z, _ = p
    zi = _inv(z)
    xp = (x * zi) % _P
    yp = (y * zi) % _P
    raw = bytearray(yp.to_bytes(32, "little"))
    raw[31] |= (xp & 1) << 7
    return bytes(raw)


def _point_decompress(data: bytes) -> tuple[int, int, int, int] | None:
    if len(data) != 32:
        return None
    y = int.from_bytes(data, "little") & ((1 << 255) - 1)
    if y >= _P:
        return None
    x = _xrecover(y)
    if x is None:
        return None
    sign_bit = (data[31] >> 7) & 1
    if x == 0 and sign_bit:
        return None
    if (x & 1) != sign_bit:
        x = _P - x
    return (x, y, 1, (x * y) % _P)


def _expand_seed(seed: bytes) -> tuple[int, bytes, bytes]:
    if not isinstance(seed, (bytes, bytearray)) or len(seed) != 32:
        raise ValueError("Ed25519 private seed must be exactly 32 bytes")
    digest = hashlib.sha512(bytes(seed)).digest()
    scalar_bytes = bytearray(digest[:32])
    scalar_bytes[0] &= 248
    scalar_bytes[31] &= 127
    scalar_bytes[31] |= 64
    scalar = int.from_bytes(scalar_bytes, "little")
    pub = _point_compress(_point_mul(scalar, _B))
    return scalar, digest[32:], pub


def generate_keypair() -> tuple[bytes, bytes]:
    """Return (private_seed_32b, public_key_32b)."""
    seed = secrets.token_bytes(32)
    _, _, pub = _expand_seed(seed)
    return seed, pub


def public_key_from_seed(seed: bytes) -> bytes:
    """Derive the 32-byte Ed25519 public key from a 32-byte private seed."""
    _, _, pub = _expand_seed(seed)
    return pub


def sign(seed: bytes, message: bytes) -> bytes:
    """Sign message using 32-byte Ed25519 private seed (RFC 8032)."""
    scalar, prefix, pub = _expand_seed(seed)
    r = int.from_bytes(hashlib.sha512(prefix + message).digest(), "little") % _L
    r_bytes = _point_compress(_point_mul(r, _B))
    k = int.from_bytes(hashlib.sha512(r_bytes + pub + message).digest(), "little") % _L
    s = (r + k * scalar) % _L
    return r_bytes + s.to_bytes(32, "little")


def verify(public_key: bytes, message: bytes, signature: bytes) -> bool:
    """Verify 64-byte Ed25519 signature against 32-byte public key."""
    if not isinstance(public_key, (bytes, bytearray)) or len(public_key) != 32:
        return False
    if not isinstance(signature, (bytes, bytearray)) or len(signature) != 64:
        return False
    pub_bytes = bytes(public_key)
    sig_bytes = bytes(signature)
    a_pt = _point_decompress(pub_bytes)
    r_pt = _point_decompress(sig_bytes[:32])
    if a_pt is None or r_pt is None:
        return False
    s = int.from_bytes(sig_bytes[32:], "little")
    if s >= _L:
        return False
    k = int.from_bytes(hashlib.sha512(sig_bytes[:32] + pub_bytes + message).digest(), "little") % _L
    lhs = _point_mul(s, _B)
    rhs = _point_add(r_pt, _point_mul(k, a_pt))
    return _point_equal(lhs, rhs)
