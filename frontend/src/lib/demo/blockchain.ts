import type { BlockchainStats, MerkleBatch, VerificationResponse } from '@/types/api'

function daysAgo(n: number, hours = 12): string {
  const d = new Date()

  d.setDate(d.getDate() - n)
  d.setHours(hours, 0, 0, 0)

  return d.toISOString()
}

// ─── Shared constants ───
const CHAIN_ID = 80002 // Polygon Amoy Testnet
const CONTRACT_ADDRESS = '0x7a3B1f5cD9eE4a8b2c6D0f1E3A9d5C7b4F2e8A6d'
const EXPLORER_BASE = 'https://amoy.polygonscan.com'

// ─── Demo Stats ───
export const DEMO_BLOCKCHAIN_STATS: BlockchainStats = {
  total_hashed: 22,
  total_batched: 20,
  total_unbatched: 2,
  total_batches: 4,
  total_anchored: 3,
  total_pending_anchor: 1,
  total_failed_anchor: 0
}

// ─── Demo Batches ───
export const DEMO_BATCHES: MerkleBatch[] = [
  {
    id: 'demo-batch-001',
    batch_number: 1,
    leaf_count: 6,
    tree_depth: 3,
    merkle_root: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
    tx_hash: '0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6',
    block_number: 15847293,
    chain_id: CHAIN_ID,
    contract_address: CONTRACT_ADDRESS,
    anchored: true,
    anchor_error: null,
    organization_id: null,
    created_at: daysAgo(9, 14)
  },
  {
    id: 'demo-batch-002',
    batch_number: 2,
    leaf_count: 6,
    tree_depth: 3,
    merkle_root: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3',
    tx_hash: '0x9a5f3e2d1b4c6a8d0f2e4c7b9a1d3e5f7c0b2a4d6e8f1a3c5b7d9e0f2a4c6b8',
    block_number: 15923841,
    chain_id: CHAIN_ID,
    contract_address: CONTRACT_ADDRESS,
    anchored: true,
    anchor_error: null,
    organization_id: null,
    created_at: daysAgo(6, 10)
  },
  {
    id: 'demo-batch-003',
    batch_number: 3,
    leaf_count: 8,
    tree_depth: 4,
    merkle_root: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4',
    tx_hash: '0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8',
    block_number: 16012457,
    chain_id: CHAIN_ID,
    contract_address: CONTRACT_ADDRESS,
    anchored: true,
    anchor_error: null,
    organization_id: null,
    created_at: daysAgo(3, 16)
  },
  {
    id: 'demo-batch-004',
    batch_number: 4,
    leaf_count: 2,
    tree_depth: 1,
    merkle_root: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5',
    tx_hash: null,
    block_number: null,
    chain_id: null,
    contract_address: null,
    anchored: false,
    anchor_error: null,
    organization_id: null,
    created_at: daysAgo(1, 9)
  }
]

// ─── Demo Verification Responses ───
// Maps evaluation report IDs (conversation_id used as proxy) to verification data

const DEMO_VERIFICATIONS: Record<string, VerificationResponse> = {
  // Batch 1 — anchored (automotive seeds, days 5-4)
  'demo-conv-001': {
    evaluation_report_id: 'demo-conv-001',
    report_hash: 'e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6',
    hashed_at: daysAgo(5, 10),
    batch_id: 'demo-batch-001',
    batch_number: 1,
    tx_hash: '0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6',
    block_number: 15847293,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6`,
    proof: {
      siblings: [
        'f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7',
        'a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9',
        'c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1'
      ],
      directions: ['left', 'right', 'left'],
      leaf_hash: 'e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6',
      leaf_index: 0,
      merkle_root: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
    }
  },
  'demo-conv-002': {
    evaluation_report_id: 'demo-conv-002',
    report_hash: 'a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0',
    hashed_at: daysAgo(5, 11),
    batch_id: 'demo-batch-001',
    batch_number: 1,
    tx_hash: '0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6',
    block_number: 15847293,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6`,
    proof: {
      siblings: [
        'd2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3',
        'a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9',
        'c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1'
      ],
      directions: ['right', 'right', 'left'],
      leaf_hash: 'a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0',
      leaf_index: 1,
      merkle_root: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
    }
  },
  'demo-conv-003': {
    evaluation_report_id: 'demo-conv-003',
    report_hash: 'b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2',
    hashed_at: daysAgo(4, 12),
    batch_id: 'demo-batch-001',
    batch_number: 1,
    tx_hash: '0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6',
    block_number: 15847293,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0x8f4e2d1a3c5b7e9f0a2d4c6b8e1f3a5d7c9b0e2f4a6d8c1b3e5f7a9d0c2b4e6`,
    proof: {
      siblings: [
        'e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5',
        'f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7',
        'c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1'
      ],
      directions: ['left', 'left', 'left'],
      leaf_hash: 'b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2',
      leaf_index: 2,
      merkle_root: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2'
    }
  },

  // Batch 2 — anchored (automotive seeds, days 3-2)
  'demo-conv-005': {
    evaluation_report_id: 'demo-conv-005',
    report_hash: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4',
    hashed_at: daysAgo(3, 11),
    batch_id: 'demo-batch-002',
    batch_number: 2,
    tx_hash: '0x9a5f3e2d1b4c6a8d0f2e4c7b9a1d3e5f7c0b2a4d6e8f1a3c5b7d9e0f2a4c6b8',
    block_number: 15923841,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0x9a5f3e2d1b4c6a8d0f2e4c7b9a1d3e5f7c0b2a4d6e8f1a3c5b7d9e0f2a4c6b8`,
    proof: {
      siblings: [
        'd5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6',
        'e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8',
        'f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0'
      ],
      directions: ['right', 'left', 'right'],
      leaf_hash: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4',
      leaf_index: 0,
      merkle_root: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3'
    }
  },
  'demo-conv-007': {
    evaluation_report_id: 'demo-conv-007',
    report_hash: 'e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6',
    hashed_at: daysAgo(2, 16),
    batch_id: 'demo-batch-002',
    batch_number: 2,
    tx_hash: '0x9a5f3e2d1b4c6a8d0f2e4c7b9a1d3e5f7c0b2a4d6e8f1a3c5b7d9e0f2a4c6b8',
    block_number: 15923841,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0x9a5f3e2d1b4c6a8d0f2e4c7b9a1d3e5f7c0b2a4d6e8f1a3c5b7d9e0f2a4c6b8`,
    proof: {
      siblings: [
        'f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8',
        'e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8',
        'f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0'
      ],
      directions: ['left', 'left', 'right'],
      leaf_hash: 'e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6',
      leaf_index: 2,
      merkle_root: 'b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3'
    }
  },

  // Batch 3 — anchored (medical seeds, days 10-4)
  'demo-conv-011': {
    evaluation_report_id: 'demo-conv-011',
    report_hash: 'a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
    hashed_at: daysAgo(10, 10),
    batch_id: 'demo-batch-003',
    batch_number: 3,
    tx_hash: '0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8',
    block_number: 16012457,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8`,
    proof: {
      siblings: [
        'b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5',
        'c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7',
        'd8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9',
        'e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1'
      ],
      directions: ['right', 'left', 'right', 'left'],
      leaf_hash: 'a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3',
      leaf_index: 0,
      merkle_root: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4'
    }
  },
  'demo-conv-015': {
    evaluation_report_id: 'demo-conv-015',
    report_hash: 'f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
    hashed_at: daysAgo(7, 12),
    batch_id: 'demo-batch-003',
    batch_number: 3,
    tx_hash: '0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8',
    block_number: 16012457,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8`,
    proof: {
      siblings: [
        'a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4',
        'c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7',
        'b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9',
        'e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1'
      ],
      directions: ['left', 'left', 'left', 'left'],
      leaf_hash: 'f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2',
      leaf_index: 4,
      merkle_root: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4'
    }
  },
  'demo-conv-019': {
    evaluation_report_id: 'demo-conv-019',
    report_hash: 'b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
    hashed_at: daysAgo(4, 10),
    batch_id: 'demo-batch-003',
    batch_number: 3,
    tx_hash: '0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8',
    block_number: 16012457,
    chain_id: CHAIN_ID,
    anchored: true,
    explorer_url: `${EXPLORER_BASE}/tx/0xd7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8`,
    proof: {
      siblings: [
        'd5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6',
        'e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8',
        'b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9',
        'e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1'
      ],
      directions: ['right', 'right', 'left', 'left'],
      leaf_hash: 'b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4',
      leaf_index: 7,
      merkle_root: 'c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4'
    }
  },

  // Batch 4 — pending (recent evaluations)
  'demo-conv-009': {
    evaluation_report_id: 'demo-conv-009',
    report_hash: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5',
    hashed_at: daysAgo(1, 16),
    batch_id: 'demo-batch-004',
    batch_number: 4,
    tx_hash: null,
    block_number: null,
    chain_id: null,
    anchored: false,
    explorer_url: null,
    proof: {
      siblings: [
        'e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7'
      ],
      directions: ['right'],
      leaf_hash: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5',
      leaf_index: 0,
      merkle_root: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5'
    }
  },
  'demo-conv-010': {
    evaluation_report_id: 'demo-conv-010',
    report_hash: 'e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7',
    hashed_at: daysAgo(1, 17),
    batch_id: 'demo-batch-004',
    batch_number: 4,
    tx_hash: null,
    block_number: null,
    chain_id: null,
    anchored: false,
    explorer_url: null,
    proof: {
      siblings: [
        'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5'
      ],
      directions: ['left'],
      leaf_hash: 'e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7',
      leaf_index: 1,
      merkle_root: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5'
    }
  }
}

export function getDemoVerification(reportId: string): VerificationResponse | null {
  return DEMO_VERIFICATIONS[reportId] ?? null
}
