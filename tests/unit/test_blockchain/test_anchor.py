"""Unit tests for the AnchorClient (mocked web3)."""

from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from uncase.core.blockchain.anchor import get_explorer_url
from uncase.exceptions import BlockchainAnchorError


class TestGetExplorerUrl:
    def test_polygon_mainnet(self) -> None:
        url = get_explorer_url(137, "0xabc123")
        assert url == "https://polygonscan.com/tx/0xabc123"

    def test_amoy_testnet(self) -> None:
        url = get_explorer_url(80002, "0xdef456")
        assert url == "https://amoy.polygonscan.com/tx/0xdef456"

    def test_unknown_chain(self) -> None:
        url = get_explorer_url(999, "0x123")
        assert "0x123" in url


class TestAnchorClientInit:
    def test_missing_web3_raises(self) -> None:
        """Importing without web3 installed should raise BlockchainAnchorError."""
        with patch.dict("sys.modules", {"web3": None}):
            from uncase.core.blockchain.anchor import AnchorClient

            with pytest.raises((BlockchainAnchorError, ImportError)):
                AnchorClient(
                    rpc_url="https://rpc.example.com",
                    private_key="0x" + "ab" * 32,
                    contract_address="0x" + "cd" * 20,
                )


class TestAnchorClientMocked:
    """Tests with web3 fully mocked via fake module injection."""

    @pytest.fixture()
    def mock_web3_module(self) -> tuple[MagicMock, MagicMock]:
        """Create mock web3 and eth_account modules."""
        mock_w3_instance = MagicMock()
        mock_w3_instance.to_checksum_address = lambda x: x
        mock_w3_instance.eth.get_transaction_count = AsyncMock(return_value=42)
        mock_w3_instance.eth.send_raw_transaction = AsyncMock(return_value=b"\xab" * 32)
        mock_w3_instance.eth.wait_for_transaction_receipt = AsyncMock(
            return_value={
                "transactionHash": MagicMock(hex=lambda: "0x" + "ab" * 32),
                "blockNumber": 12345,
            }
        )

        mock_contract = MagicMock()
        mock_build_tx = AsyncMock(return_value={"from": "0x1", "nonce": 42, "chainId": 80002})
        mock_contract.functions.anchorRoot.return_value.build_transaction = mock_build_tx

        mock_verify = AsyncMock(return_value=b"\xab" * 32)
        mock_contract.functions.verifyRoot.return_value.call = mock_verify

        mock_get_ts = AsyncMock(return_value=1700000000)
        mock_contract.functions.getTimestamp.return_value.call = mock_get_ts

        mock_w3_instance.eth.contract.return_value = mock_contract

        # Build fake web3 module
        web3_mod = ModuleType("web3")
        web3_mod.AsyncWeb3 = MagicMock(return_value=mock_w3_instance)  # type: ignore[attr-defined]
        web3_mod.AsyncHTTPProvider = MagicMock()  # type: ignore[attr-defined]

        # Build fake eth_account module
        eth_account_mod = ModuleType("eth_account")
        mock_account = MagicMock()
        mock_account.from_key.return_value.address = "0x" + "ef" * 20
        mock_account.from_key.return_value.sign_transaction.return_value.raw_transaction = b"\x00"
        eth_account_mod.Account = mock_account  # type: ignore[attr-defined]

        return web3_mod, eth_account_mod  # type: ignore[return-value]

    @pytest.fixture()
    def client(self, mock_web3_module: tuple[MagicMock, MagicMock]) -> MagicMock:
        web3_mod, eth_account_mod = mock_web3_module
        with patch.dict(sys.modules, {"web3": web3_mod, "eth_account": eth_account_mod}):
            # Re-import to pick up mocked modules
            from uncase.core.blockchain.anchor import AnchorClient

            return AnchorClient(
                rpc_url="https://rpc.example.com",
                private_key="0x" + "ab" * 32,
                contract_address="0x" + "cd" * 20,
                chain_id=80002,
            )

    @pytest.mark.asyncio()
    async def test_anchor_root_returns_tx_hash(
        self,
        client: MagicMock,
        mock_web3_module: tuple[MagicMock, MagicMock],
    ) -> None:
        _, eth_account_mod = mock_web3_module
        with patch.dict(sys.modules, {"eth_account": eth_account_mod}):
            tx = await client.anchor_root(1, "ab" * 32)
            assert tx.startswith("0x")

    @pytest.mark.asyncio()
    async def test_verify_root_returns_hex(self, client: MagicMock) -> None:
        result = await client.verify_root(1)
        assert result is not None
        assert len(result) == 64

    @pytest.mark.asyncio()
    async def test_verify_root_empty_returns_none(
        self,
        client: MagicMock,
        mock_web3_module: tuple[MagicMock, MagicMock],
    ) -> None:
        web3_mod, _ = mock_web3_module
        # Override the verify call to return zero bytes
        w3_instance = web3_mod.AsyncWeb3.return_value
        w3_instance.eth.contract.return_value.functions.verifyRoot.return_value.call = AsyncMock(
            return_value=b"\x00" * 32
        )
        result = await client.verify_root(99)
        assert result is None
