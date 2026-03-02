"""Unit tests for the binary Merkle tree and proof verification."""

from __future__ import annotations

import hashlib

import pytest

from uncase.core.blockchain.merkle import MerkleTree, _hash_pair


def _sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


class TestHashPair:
    def test_deterministic(self) -> None:
        a, b = _sha256("a"), _sha256("b")
        assert _hash_pair(a, b) == _hash_pair(a, b)

    def test_order_independent(self) -> None:
        """_hash_pair sorts inputs, so order doesn't matter."""
        a, b = _sha256("a"), _sha256("b")
        assert _hash_pair(a, b) == _hash_pair(b, a)


class TestMerkleTree:
    def test_single_leaf(self) -> None:
        """A single-leaf tree has the leaf as its root."""
        leaf = _sha256("only")
        tree = MerkleTree([leaf])
        assert tree.root == leaf
        assert tree.leaf_count == 1
        assert tree.depth == 0

    def test_two_leaves(self) -> None:
        leaves = [_sha256("a"), _sha256("b")]
        tree = MerkleTree(leaves)
        expected_root = _hash_pair(leaves[0], leaves[1])
        assert tree.root == expected_root
        assert tree.leaf_count == 2
        assert tree.depth == 1

    def test_four_leaves(self) -> None:
        leaves = [_sha256(str(i)) for i in range(4)]
        tree = MerkleTree(leaves)
        h01 = _hash_pair(leaves[0], leaves[1])
        h23 = _hash_pair(leaves[2], leaves[3])
        expected_root = _hash_pair(h01, h23)
        assert tree.root == expected_root
        assert tree.leaf_count == 4
        assert tree.depth == 2

    def test_odd_leaf_count_pads(self) -> None:
        """Odd leaf count duplicates the last leaf."""
        leaves = [_sha256(str(i)) for i in range(3)]
        tree = MerkleTree(leaves)
        # Tree pads to 4 leaves: [l0, l1, l2, l2]
        h01 = _hash_pair(leaves[0], leaves[1])
        h22 = _hash_pair(leaves[2], leaves[2])
        expected_root = _hash_pair(h01, h22)
        assert tree.root == expected_root
        assert tree.leaf_count == 3

    def test_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="zero leaves"):
            MerkleTree([])

    def test_get_all_nodes_count(self) -> None:
        leaves = [_sha256(str(i)) for i in range(4)]
        tree = MerkleTree(leaves)
        nodes = tree.get_all_nodes()
        # 4 leaves + 2 intermediate + 1 root = 7
        assert len(nodes) == 7


class TestMerkleProof:
    def test_proof_verifies_all_leaves(self) -> None:
        """Every leaf's proof should verify against the root."""
        leaves = [_sha256(str(i)) for i in range(8)]
        tree = MerkleTree(leaves)
        for i in range(len(leaves)):
            proof = tree.get_proof(i)
            assert proof.verify(), f"Proof for leaf {i} failed"
            assert proof.root == tree.root
            assert proof.leaf_hash == leaves[i]
            assert proof.leaf_index == i

    def test_proof_fails_with_wrong_leaf(self) -> None:
        """Tampering with the leaf hash breaks the proof."""
        leaves = [_sha256(str(i)) for i in range(4)]
        tree = MerkleTree(leaves)
        proof = tree.get_proof(0)
        # Create a tampered proof with a different leaf
        from uncase.core.blockchain.merkle import MerkleProof

        tampered = MerkleProof(
            leaf_hash=_sha256("tampered"),
            leaf_index=proof.leaf_index,
            siblings=proof.siblings,
            directions=proof.directions,
            root=proof.root,
        )
        assert not tampered.verify()

    def test_proof_index_out_of_range(self) -> None:
        leaves = [_sha256(str(i)) for i in range(4)]
        tree = MerkleTree(leaves)
        with pytest.raises(IndexError):
            tree.get_proof(4)
        with pytest.raises(IndexError):
            tree.get_proof(-1)

    def test_get_all_proofs(self) -> None:
        leaves = [_sha256(str(i)) for i in range(5)]
        tree = MerkleTree(leaves)
        proofs = tree.get_all_proofs()
        assert len(proofs) == 5
        for proof in proofs:
            assert proof.verify()

    def test_single_leaf_proof(self) -> None:
        """Single leaf proof has no siblings."""
        leaf = _sha256("solo")
        tree = MerkleTree([leaf])
        proof = tree.get_proof(0)
        assert proof.siblings == []
        assert proof.directions == []
        assert proof.verify()

    @pytest.mark.parametrize("n_leaves", [2, 3, 7, 15, 16, 31, 32, 100])
    def test_various_sizes(self, n_leaves: int) -> None:
        """Proofs verify for trees of various sizes."""
        leaves = [_sha256(str(i)) for i in range(n_leaves)]
        tree = MerkleTree(leaves)
        for i in range(n_leaves):
            assert tree.get_proof(i).verify()
