# Polygon Blockchain Setup Guide

Complete guide to configuring UNCASE's blockchain certification layer with Polygon PoS. This enables immutable, on-chain quality verification for every synthetic dataset you produce.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Prerequisites](#2-prerequisites)
3. [Create a Wallet with MetaMask](#3-create-a-wallet-with-metamask)
4. [Add the Polygon Network](#4-add-the-polygon-network)
5. [Get POL Tokens (Gas Fees)](#5-get-pol-tokens-gas-fees)
6. [Deploy the Smart Contract](#6-deploy-the-smart-contract)
7. [Configure UNCASE Environment](#7-configure-uncase-environment)
8. [Test the Integration](#8-test-the-integration)
9. [View Transactions on PolygonScan](#9-view-transactions-on-polygonscan)
10. [Production Checklist](#10-production-checklist)
11. [Troubleshooting](#11-troubleshooting)
12. [Security Best Practices](#12-security-best-practices)

---

## 1. Overview

### What is Polygon PoS?

Polygon PoS (Proof of Stake) is an Ethereum sidechain that offers fast, low-cost transactions while inheriting Ethereum's security. UNCASE uses Polygon to anchor Merkle roots of quality evaluation reports, creating a permanent, tamper-proof audit trail.

### How UNCASE Uses Blockchain

```
Evaluation Report --> SHA-256 Hash --> Merkle Tree --> Anchor Root On-Chain
```

1. **Hash**: Each quality evaluation report is serialized to canonical JSON and hashed with SHA-256.
2. **Batch**: Multiple hashes are grouped into a binary Merkle tree.
3. **Anchor**: The Merkle root is submitted to a smart contract on Polygon.
4. **Verify**: Anyone can independently verify a report by recomputing its hash, walking the Merkle proof, and checking the root against the on-chain record.

### Why Polygon?

| Feature | Polygon PoS |
|---------|-------------|
| Transaction cost | ~$0.001-0.01 USD per tx |
| Confirmation time | ~2 seconds |
| Security | Inherits Ethereum's validator set |
| Block explorer | PolygonScan (full transparency) |
| Token | POL (formerly MATIC) |

---

## 2. Prerequisites

Before starting, make sure you have:

- A web browser (Chrome, Firefox, or Brave recommended)
- The UNCASE backend running (`uv run uvicorn uncase.api.main:app --reload`)
- Python 3.11+ with the `[blockchain]` extra installed:
  ```bash
  pip install "uncase[blockchain]"
  # or with uv:
  uv sync --extra blockchain
  ```
- Node.js 18+ (for contract deployment, if deploying from source)

---

## 3. Create a Wallet with MetaMask

MetaMask is a browser extension that acts as your Ethereum/Polygon wallet.

### Step 1: Install MetaMask

1. Go to [metamask.io](https://metamask.io/download/)
2. Click **Download** for your browser
3. Click **Add to Chrome** (or your browser)
4. Pin the MetaMask extension to your toolbar

### Step 2: Create a New Wallet

1. Click the MetaMask icon in your toolbar
2. Click **Create a new wallet**
3. Set a strong password (this is your local unlock password)
4. **CRITICAL**: Write down your 12-word Secret Recovery Phrase on paper
   - Store it in a safe, offline location
   - Never share it with anyone
   - Never store it digitally (no screenshots, no cloud storage)
5. Confirm the recovery phrase by selecting words in order
6. Your wallet is now ready

### Step 3: Export Your Private Key

UNCASE needs the private key of the wallet that will sign anchoring transactions.

1. Click the three dots (menu) next to your account name
2. Select **Account details**
3. Click **Show private key**
4. Enter your MetaMask password
5. Copy the private key (starts with `0x`)
6. You'll use this in the `.env` file (Step 7)

> **IMPORTANT**: The private key gives full control over this wallet. For production, use a dedicated wallet with minimal funds (only enough for gas fees). Never use your personal wallet.

---

## 4. Add the Polygon Network

### Amoy Testnet (Recommended for Testing)

1. Open MetaMask
2. Click the network dropdown (top left, says "Ethereum Mainnet")
3. Click **Add network** > **Add a network manually**
4. Enter:
   - **Network Name**: Polygon Amoy Testnet
   - **RPC URL**: `https://rpc-amoy.polygon.technology`
   - **Chain ID**: `80002`
   - **Currency Symbol**: `POL`
   - **Block Explorer**: `https://amoy.polygonscan.com`
5. Click **Save**

### Polygon Mainnet (For Production)

1. Same steps as above, but enter:
   - **Network Name**: Polygon Mainnet
   - **RPC URL**: `https://polygon-rpc.com`
   - **Chain ID**: `137`
   - **Currency Symbol**: `POL`
   - **Block Explorer**: `https://polygonscan.com`
2. Click **Save**

### Alternative: Use Chainlist

1. Go to [chainlist.org](https://chainlist.org)
2. Search for "Polygon" or "Amoy"
3. Click **Add to MetaMask** on the desired network

---

## 5. Get POL Tokens (Gas Fees)

### Testnet (Amoy) - Free Faucet

For testing, you can get free testnet POL:

1. Go to the [Polygon Faucet](https://faucet.polygon.technology/)
2. Select **Amoy** network
3. Paste your wallet address (copy from MetaMask)
4. Complete the verification
5. Click **Submit**
6. You'll receive 0.5 POL within a few seconds

Alternative faucets:
- [Alchemy Amoy Faucet](https://www.alchemy.com/faucets/polygon-amoy)
- [QuickNode Polygon Faucet](https://faucet.quicknode.com/polygon/amoy)

### Mainnet - Purchase POL

For production, you need real POL tokens:

**Option A: Buy directly in MetaMask**
1. Open MetaMask on Polygon Mainnet
2. Click **Buy**
3. Choose a payment method (credit card, bank transfer)
4. Purchase POL tokens

**Option B: Buy on an exchange and transfer**
1. Buy POL on an exchange (Coinbase, Binance, Kraken, etc.)
2. Withdraw to your MetaMask wallet address
3. Make sure to select the **Polygon** network for withdrawal (not Ethereum)

**Option C: Bridge from Ethereum**
1. If you have ETH, use the [Polygon Bridge](https://portal.polygon.technology/bridge)
2. Connect your MetaMask
3. Bridge ETH to Polygon (converts to WETH on Polygon)
4. Swap WETH for POL on a DEX like [QuickSwap](https://quickswap.exchange)

> **How much POL do I need?** Each anchor transaction costs approximately 0.001-0.01 POL (~$0.001-0.01 USD). For moderate usage (100 batches/month), 1 POL is more than sufficient.

---

## 6. Deploy the Smart Contract

UNCASE uses a minimal `UNCASEAuditAnchor` contract. You can deploy it using Remix IDE or Hardhat.

### Smart Contract Code

Create a file named `UNCASEAuditAnchor.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/// @title UNCASEAuditAnchor
/// @notice Stores Merkle roots for UNCASE quality evaluation batches
contract UNCASEAuditAnchor {
    address public owner;

    struct AnchorRecord {
        bytes32 root;
        uint256 timestamp;
    }

    mapping(uint256 => AnchorRecord) public anchors;

    event RootAnchored(uint256 indexed batchId, bytes32 root, uint256 timestamp);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    /// @notice Anchor a Merkle root for a batch
    /// @param batchId Sequential batch identifier
    /// @param root SHA-256 Merkle root (32 bytes)
    function anchorRoot(uint256 batchId, bytes32 root) external onlyOwner {
        require(anchors[batchId].timestamp == 0, "Batch already anchored");
        anchors[batchId] = AnchorRecord(root, block.timestamp);
        emit RootAnchored(batchId, root, block.timestamp);
    }

    /// @notice Verify the stored root for a batch
    /// @param batchId The batch to query
    /// @return The stored Merkle root (bytes32(0) if not found)
    function verifyRoot(uint256 batchId) external view returns (bytes32) {
        return anchors[batchId].root;
    }

    /// @notice Get the anchor timestamp for a batch
    /// @param batchId The batch to query
    /// @return The block timestamp when the batch was anchored (0 if not found)
    function getTimestamp(uint256 batchId) external view returns (uint256) {
        return anchors[batchId].timestamp;
    }

    /// @notice Transfer ownership
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Zero address");
        owner = newOwner;
    }
}
```

### Deploy with Remix IDE (Easiest)

1. Go to [Remix IDE](https://remix.ethereum.org)
2. Create a new file `UNCASEAuditAnchor.sol` and paste the contract code
3. Go to the **Solidity Compiler** tab (left sidebar)
   - Select compiler version `0.8.20` or later
   - Click **Compile**
4. Go to the **Deploy & Run** tab
   - Environment: **Injected Provider - MetaMask**
   - MetaMask will ask to connect - approve it
   - Make sure MetaMask is on the correct network (Amoy for testing)
5. Click **Deploy**
6. MetaMask will pop up asking to confirm the transaction
   - Review the gas fee
   - Click **Confirm**
7. Wait for deployment (~2 seconds on Polygon)
8. Copy the deployed contract address (shown under "Deployed Contracts")
9. You'll use this address in the `.env` file (Step 7)

### Deploy with Hardhat (Advanced)

```bash
# Initialize project
mkdir uncase-contract && cd uncase-contract
npm init -y
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox

# Initialize Hardhat
npx hardhat init
# Select "Create a TypeScript project"

# Copy the contract to contracts/UNCASEAuditAnchor.sol

# Create deploy script (scripts/deploy.ts):
cat > scripts/deploy.ts << 'SCRIPT'
import { ethers } from "hardhat";

async function main() {
  const Contract = await ethers.getContractFactory("UNCASEAuditAnchor");
  const contract = await Contract.deploy();
  await contract.waitForDeployment();
  console.log("UNCASEAuditAnchor deployed to:", await contract.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
SCRIPT

# Configure hardhat.config.ts with Polygon network
# Add to networks section:
# amoy: {
#   url: "https://rpc-amoy.polygon.technology",
#   accounts: [process.env.PRIVATE_KEY]
# }

# Deploy
npx hardhat run scripts/deploy.ts --network amoy
```

---

## 7. Configure UNCASE Environment

Add the following variables to your `.env` file in the UNCASE project root:

```env
# ─── Blockchain Configuration ───
BLOCKCHAIN_ENABLED=true

# Polygon RPC URL
# Testnet (Amoy):
POLYGON_RPC_URL=https://rpc-amoy.polygon.technology
# Mainnet:
# POLYGON_RPC_URL=https://polygon-rpc.com

# Private key of the wallet that signs transactions
# IMPORTANT: Use a dedicated wallet, never your personal one
POLYGON_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

# Address of the deployed UNCASEAuditAnchor contract
POLYGON_CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS_HERE

# Chain ID (80002 = Amoy testnet, 137 = Mainnet)
POLYGON_CHAIN_ID=80002
```

### Using a Premium RPC Provider (Recommended for Production)

Free public RPCs can be slow or rate-limited. For production, use a dedicated provider:

| Provider | Free Tier | URL Format |
|----------|-----------|------------|
| [Alchemy](https://www.alchemy.com/) | 300M compute units/mo | `https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY` |
| [Infura](https://www.infura.io/) | 100K requests/day | `https://polygon-amoy.infura.io/v3/YOUR_KEY` |
| [QuickNode](https://www.quicknode.com/) | 10M API credits/mo | Custom endpoint URL |
| [Ankr](https://www.ankr.com/) | Rate-limited free tier | `https://rpc.ankr.com/polygon_amoy` |

Example with Alchemy:
```env
POLYGON_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/abc123yourkey
```

---

## 8. Test the Integration

### Verify Configuration

Start the UNCASE API and check the blockchain settings:

```bash
# Start the API
uv run uvicorn uncase.api.main:app --reload --port 8000

# Check blockchain stats (should return zeros)
curl http://localhost:8000/api/v1/blockchain/stats
```

Expected response:
```json
{
  "total_hashed": 0,
  "total_batched": 0,
  "total_unbatched": 0,
  "total_batches": 0,
  "total_anchored": 0,
  "total_pending_anchor": 0,
  "total_failed_anchor": 0
}
```

### Run an Evaluation and Verify

1. Run a quality evaluation through the pipeline (or via the dashboard)
2. The evaluation report will be automatically hashed
3. Go to **Dashboard > Blockchain** and click **Build Batch**
4. The batch will be created and anchored on Polygon
5. Use the **Verify** tab to look up the evaluation report ID

### Manual Test with curl

```bash
# Build a batch from unbatched hashes
curl -X POST http://localhost:8000/api/v1/blockchain/batch \
  -H "Content-Type: application/json" \
  -d '{}'

# Verify a specific evaluation
curl http://localhost:8000/api/v1/blockchain/verify/{evaluation_report_id}

# List all batches
curl "http://localhost:8000/api/v1/blockchain/batches?limit=10"
```

---

## 9. View Transactions on PolygonScan

### Finding Your Transactions

**Via the UNCASE Dashboard:**
1. Go to **Dashboard > Blockchain**
2. In the **Batch Ledger** tab, click any transaction hash
3. This opens PolygonScan directly

**Via PolygonScan:**
1. Go to [amoy.polygonscan.com](https://amoy.polygonscan.com) (testnet) or [polygonscan.com](https://polygonscan.com) (mainnet)
2. Paste your wallet address or transaction hash in the search bar

### Understanding the Transaction

When you view a transaction on PolygonScan, you'll see:

- **Status**: Success / Failed
- **Block**: The block number where the transaction was included
- **Timestamp**: When the block was mined
- **From**: Your wallet address (the signer)
- **To**: The UNCASEAuditAnchor contract address
- **Value**: 0 POL (it's a data transaction, not a transfer)
- **Transaction Fee**: The gas cost in POL
- **Input Data**: The encoded `anchorRoot(batchId, root)` call

### Reading the Event Log

Click the **Logs** tab on the transaction page to see:

```
Event: RootAnchored(uint256 batchId, bytes32 root, uint256 timestamp)
- batchId: 1 (the batch number)
- root: 0x7a8b... (the Merkle root hash)
- timestamp: 1709312400 (Unix timestamp)
```

### Monitoring Your Contract

1. Go to your contract address on PolygonScan
2. Click the **Events** tab to see all anchoring events
3. Click **Read Contract** to query `verifyRoot(batchId)` directly
4. Click **Internal Txns** to see all interactions

### Setting Up Alerts (Optional)

PolygonScan offers email alerts:
1. Create an account on PolygonScan
2. Go to your contract page
3. Click **Watch** (eye icon)
4. Configure email alerts for new transactions

---

## 10. Production Checklist

Before going to production, verify:

- [ ] Switch from Amoy testnet to Polygon Mainnet (`POLYGON_CHAIN_ID=137`)
- [ ] Use a premium RPC provider (Alchemy, Infura, etc.)
- [ ] Deploy the contract on Mainnet
- [ ] Fund the wallet with sufficient POL (~1 POL for months of usage)
- [ ] Use a dedicated wallet (not personal)
- [ ] Store the private key securely (use a secrets manager, not plain `.env`)
- [ ] Verify the contract on PolygonScan (for public verification)
- [ ] Set up monitoring alerts on PolygonScan
- [ ] Test the full flow: evaluate > hash > batch > anchor > verify
- [ ] Back up the wallet's recovery phrase securely

---

## 11. Troubleshooting

### "web3 is required for blockchain anchoring"

Install the blockchain dependencies:
```bash
pip install "uncase[blockchain]"
```

### "Failed to anchor root on-chain"

Common causes:
- **Insufficient funds**: Check your wallet balance on PolygonScan
- **Wrong network**: Verify `POLYGON_CHAIN_ID` matches your wallet's network
- **RPC issue**: Try a different RPC URL or provider
- **Nonce mismatch**: If transactions are stuck, check pending transactions in MetaMask

### "Batch already anchored"

The same batch ID can only be anchored once. This is by design - it prevents tampering. If you need to re-anchor, a new batch must be created.

### Transaction is stuck / pending

1. Check the transaction on PolygonScan
2. If it shows "Pending", the gas price may be too low
3. In MetaMask, you can speed up or cancel the transaction
4. For the UNCASE API, retry with `POST /api/v1/blockchain/retry-anchor`

### "Network error" or connection timeout

1. Verify the RPC URL is correct and accessible
2. Try pinging the RPC: `curl https://rpc-amoy.polygon.technology -X POST -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_blockNumber","params":[],"id":1}'`
3. Switch to a different RPC provider

---

## 12. Security Best Practices

### Wallet Security

- **Use a dedicated wallet** exclusively for UNCASE anchoring
- **Minimal funds**: Only keep enough POL for gas fees (~1 POL)
- **Backup**: Store the recovery phrase offline in a secure location
- **Hardware wallet**: For high-value deployments, use a Ledger or Trezor

### Private Key Management

- **Never commit** the private key to version control
- **Use environment variables** or a secrets manager (AWS Secrets Manager, HashiCorp Vault)
- **Rotate keys** periodically by transferring contract ownership
- **Restrict access**: Only the deployment server should have the private key

### Contract Security

- **Verify on PolygonScan**: Publish the contract source code for transparency
- **Owner-only writes**: The contract restricts `anchorRoot` to the owner address
- **Immutable records**: Once anchored, records cannot be modified or deleted
- **Transfer ownership**: Use `transferOwnership()` if the signing wallet needs to change

### Monitoring

- Set up PolygonScan email alerts for your contract
- Monitor wallet balance to ensure sufficient gas funds
- Check the UNCASE dashboard for failed anchoring attempts
- Review the API logs for `anchor_root_failed` events

---

## Quick Reference

| Item | Value |
|------|-------|
| Polygon Mainnet Chain ID | `137` |
| Polygon Amoy Testnet Chain ID | `80002` |
| Mainnet RPC | `https://polygon-rpc.com` |
| Amoy RPC | `https://rpc-amoy.polygon.technology` |
| Mainnet Explorer | [polygonscan.com](https://polygonscan.com) |
| Amoy Explorer | [amoy.polygonscan.com](https://amoy.polygonscan.com) |
| Token | POL (formerly MATIC) |
| Avg. Transaction Cost | ~$0.001-0.01 USD |
| Confirmation Time | ~2 seconds |
| UNCASE Blockchain Endpoint | `GET /api/v1/blockchain/stats` |
| UNCASE Verify Endpoint | `GET /api/v1/blockchain/verify/{id}` |
