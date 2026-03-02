// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title UNCASEAuditAnchor
 * @notice Anchors Merkle roots of UNCASE quality certification batches on-chain.
 * @dev Each batch ID can only be anchored once. The owner (UNCASE API backend)
 *      submits the root; anyone can verify.
 */
contract UNCASEAuditAnchor is Ownable {
    struct Anchor {
        bytes32 root;
        uint256 timestamp;
    }

    /// @notice Mapping from batch ID to its anchor data.
    mapping(uint256 => Anchor) private _anchors;

    /// @notice Emitted when a Merkle root is anchored for a batch.
    event RootAnchored(uint256 indexed batchId, bytes32 root, uint256 timestamp);

    constructor() Ownable(msg.sender) {}

    /**
     * @notice Anchor a Merkle root for the given batch ID.
     * @param batchId Sequential batch number from the UNCASE API.
     * @param root    SHA-256 Merkle root (32 bytes).
     */
    function anchorRoot(uint256 batchId, bytes32 root) external onlyOwner {
        require(_anchors[batchId].timestamp == 0, "Batch already anchored");
        require(root != bytes32(0), "Root cannot be zero");

        _anchors[batchId] = Anchor({root: root, timestamp: block.timestamp});

        emit RootAnchored(batchId, root, block.timestamp);
    }

    /**
     * @notice Retrieve the anchored root for a batch.
     * @param batchId The batch ID to look up.
     * @return The Merkle root (bytes32(0) if not anchored).
     */
    function verifyRoot(uint256 batchId) external view returns (bytes32) {
        return _anchors[batchId].root;
    }

    /**
     * @notice Retrieve the anchor timestamp for a batch.
     * @param batchId The batch ID to look up.
     * @return The Unix timestamp when the root was anchored (0 if not anchored).
     */
    function getTimestamp(uint256 batchId) external view returns (uint256) {
        return _anchors[batchId].timestamp;
    }
}
