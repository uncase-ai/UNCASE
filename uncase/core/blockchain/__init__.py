"""Blockchain-anchored quality certification for UNCASE.

This package provides tamper-proof, independently verifiable quality
certifications by anchoring cryptographic proofs on Polygon PoS.
"""

from __future__ import annotations

from uncase.core.blockchain.anchor import AnchorClient, get_explorer_url
from uncase.core.blockchain.hasher import canonicalize_report, hash_report
from uncase.core.blockchain.merkle import MerkleProof, MerkleTree

__all__ = [
    "AnchorClient",
    "MerkleProof",
    "MerkleTree",
    "canonicalize_report",
    "get_explorer_url",
    "hash_report",
]
