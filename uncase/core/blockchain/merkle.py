"""Binary Merkle tree with proof generation and verification."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


def _hash_pair(left: str, right: str) -> str:
    """Hash two hex-encoded digests together (sorted for determinism)."""
    combined = min(left, right) + max(left, right)
    return hashlib.sha256(combined.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class MerkleProof:
    """Inclusion proof for a single leaf in a Merkle tree."""

    leaf_hash: str
    leaf_index: int
    siblings: list[str] = field(default_factory=list)
    directions: list[str] = field(default_factory=list)
    root: str = ""

    def verify(self) -> bool:
        """Recompute the root from the leaf and siblings, return True if it matches."""
        current = self.leaf_hash
        for sibling, direction in zip(self.siblings, self.directions, strict=True):
            current = _hash_pair(sibling, current) if direction == "left" else _hash_pair(current, sibling)
        return current == self.root


class MerkleTree:
    """Binary Merkle tree built from a list of hex-encoded leaf hashes.

    Odd leaf count is handled by duplicating the last leaf (standard padding).
    """

    def __init__(self, leaves: list[str]) -> None:
        if not leaves:
            msg = "Cannot build a Merkle tree with zero leaves"
            raise ValueError(msg)
        self._original_leaves = list(leaves)
        self._levels: list[list[str]] = []
        self._root = self._build()

    def _build(self) -> str:
        """Build the tree bottom-up and return the root hash."""
        level = list(self._original_leaves)

        # Pad to even count if necessary
        if len(level) > 1 and len(level) % 2 != 0:
            level.append(level[-1])

        self._levels.append(level)

        while len(level) > 1:
            next_level: list[str] = []
            for i in range(0, len(level), 2):
                next_level.append(_hash_pair(level[i], level[i + 1]))

            if len(next_level) > 1 and len(next_level) % 2 != 0:
                next_level.append(next_level[-1])

            self._levels.append(next_level)
            level = next_level

        return level[0]

    @property
    def root(self) -> str:
        """Return the Merkle root hex digest."""
        return self._root

    @property
    def depth(self) -> int:
        """Return the depth of the tree (number of levels - 1)."""
        return len(self._levels) - 1

    @property
    def leaf_count(self) -> int:
        """Return the original leaf count (before padding)."""
        return len(self._original_leaves)

    def get_proof(self, leaf_index: int) -> MerkleProof:
        """Generate an inclusion proof for the leaf at *leaf_index*."""
        if leaf_index < 0 or leaf_index >= len(self._original_leaves):
            msg = f"leaf_index {leaf_index} out of range [0, {len(self._original_leaves)})"
            raise IndexError(msg)

        siblings: list[str] = []
        directions: list[str] = []
        idx = leaf_index

        for level in self._levels[:-1]:  # skip the root level
            if idx % 2 == 0:
                sibling_idx = idx + 1
                directions.append("right")
            else:
                sibling_idx = idx - 1
                directions.append("left")

            if sibling_idx < len(level):
                siblings.append(level[sibling_idx])
            else:
                siblings.append(level[idx])
                directions[-1] = "right"

            idx //= 2

        return MerkleProof(
            leaf_hash=self._original_leaves[leaf_index],
            leaf_index=leaf_index,
            siblings=siblings,
            directions=directions,
            root=self._root,
        )

    def get_all_proofs(self) -> list[MerkleProof]:
        """Generate proofs for every original leaf."""
        return [self.get_proof(i) for i in range(len(self._original_leaves))]

    def get_all_nodes(self) -> list[tuple[int, int, str]]:
        """Return all nodes as ``(level, index, hash)`` tuples."""
        nodes: list[tuple[int, int, str]] = []
        for level_idx, level in enumerate(self._levels):
            for node_idx, node_hash in enumerate(level):
                nodes.append((level_idx, node_idx, node_hash))
        return nodes
