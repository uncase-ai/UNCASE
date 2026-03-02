"""Polygon PoS on-chain anchoring via web3.py (optional dependency)."""

from __future__ import annotations

from typing import Any

import structlog

from uncase.exceptions import BlockchainAnchorError

logger = structlog.get_logger(__name__)

# Minimal ABI for the UNCASEAuditAnchor contract.
_CONTRACT_ABI: list[dict[str, Any]] = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "batchId", "type": "uint256"},
            {"internalType": "bytes32", "name": "root", "type": "bytes32"},
        ],
        "name": "anchorRoot",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "batchId", "type": "uint256"}],
        "name": "verifyRoot",
        "outputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "inputs": [{"internalType": "uint256", "name": "batchId", "type": "uint256"}],
        "name": "getTimestamp",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function",
    },
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "uint256", "name": "batchId", "type": "uint256"},
            {"indexed": False, "internalType": "bytes32", "name": "root", "type": "bytes32"},
            {"indexed": False, "internalType": "uint256", "name": "timestamp", "type": "uint256"},
        ],
        "name": "RootAnchored",
        "type": "event",
    },
]

# Explorer base URLs per chain
_EXPLORER_URLS: dict[int, str] = {
    137: "https://polygonscan.com/tx/",
    80002: "https://amoy.polygonscan.com/tx/",
}


def get_explorer_url(chain_id: int, tx_hash: str) -> str:
    """Return a Polygonscan URL for the given transaction."""
    base = _EXPLORER_URLS.get(chain_id, "https://polygonscan.com/tx/")
    return f"{base}{tx_hash}"


class AnchorClient:
    """Async client for anchoring Merkle roots on Polygon PoS.

    Requires ``web3`` and ``eth-account`` (install with ``pip install 'uncase[blockchain]'``).
    """

    def __init__(
        self,
        *,
        rpc_url: str,
        private_key: str,
        contract_address: str,
        chain_id: int = 80002,
    ) -> None:
        try:
            from web3 import AsyncHTTPProvider, AsyncWeb3
        except ImportError as exc:
            msg = "web3 is required for blockchain anchoring. Install with: pip install 'uncase[blockchain]'"
            raise BlockchainAnchorError(msg) from exc

        self._w3 = AsyncWeb3(AsyncHTTPProvider(rpc_url))
        self._chain_id = chain_id
        self._contract_address = self._w3.to_checksum_address(contract_address)
        self._private_key = private_key
        self._contract = self._w3.eth.contract(
            address=self._contract_address,
            abi=_CONTRACT_ABI,
        )

    async def anchor_root(self, batch_id: int, root_hex: str) -> str:
        """Anchor a Merkle root on-chain and return the transaction hash.

        Args:
            batch_id: Sequential batch number.
            root_hex: 64-char hex-encoded SHA-256 Merkle root.

        Returns:
            Transaction hash (``0x``-prefixed, 66 chars).

        Raises:
            BlockchainAnchorError: On any web3 / RPC failure.
        """
        try:
            from eth_account import Account

            root_bytes = bytes.fromhex(root_hex)
            account = Account.from_key(self._private_key)

            tx = await self._contract.functions.anchorRoot(batch_id, root_bytes).build_transaction(
                {
                    "from": account.address,
                    "nonce": await self._w3.eth.get_transaction_count(account.address),
                    "chainId": self._chain_id,
                }
            )

            signed = account.sign_transaction(tx)
            tx_hash = await self._w3.eth.send_raw_transaction(signed.raw_transaction)
            receipt = await self._w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

            hex_hash: str = str(receipt["transactionHash"].hex())
            if not hex_hash.startswith("0x"):
                hex_hash = f"0x{hex_hash}"

            logger.info(
                "merkle_root_anchored",
                batch_id=batch_id,
                tx_hash=hex_hash,
                block_number=receipt["blockNumber"],
                chain_id=self._chain_id,
            )

            return hex_hash

        except BlockchainAnchorError:
            raise
        except Exception as exc:
            logger.error("anchor_root_failed", batch_id=batch_id, error=str(exc))
            raise BlockchainAnchorError(f"Failed to anchor root on-chain: {exc}") from exc

    async def verify_root(self, batch_id: int) -> str | None:
        """Query the on-chain root for *batch_id*.

        Returns the hex-encoded root or ``None`` if not found.
        """
        try:
            root_bytes: bytes = await self._contract.functions.verifyRoot(batch_id).call()
            if root_bytes == b"\x00" * 32:
                return None
            return root_bytes.hex()
        except Exception as exc:
            logger.warning("verify_root_failed", batch_id=batch_id, error=str(exc))
            return None

    async def get_timestamp(self, batch_id: int) -> int | None:
        """Query the on-chain anchor timestamp for *batch_id*."""
        try:
            ts: int = await self._contract.functions.getTimestamp(batch_id).call()
            return ts if ts > 0 else None
        except Exception:
            return None
