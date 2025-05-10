"""
Tests for the Solana wallet service
"""
import pytest
import os
import base58
from unittest.mock import MagicMock, patch
from app.services.solana_wallet import SolanaWallet, initialize_wallet, get_wallet

# Sample test data
TEST_PRIVATE_KEY = "4xQDeV6gJWXxDeze9FLDpVBJ9Sgn7S4XiWpwmDG6qDQvG9Fmo4NaUUbKsUNt6uQS3WRMHMgibLXzNRAfyoUdnwYH"
TEST_PUBLIC_KEY = "DRKgF2S4XWScdP8rr1vFLKMJJbTKBcX8FXMvrK9uYEsc"
TEST_RPC_URL = "https://api.devnet.solana.com"


@pytest.fixture
def mock_solana_client():
    """Create a mock Solana client"""
    with patch('app.services.solana_wallet.Client') as mock_client:
        # Setup mock responses
        mock_instance = MagicMock()
        mock_instance.get_version.return_value = {
            'result': {'solana-core': '1.14.10'}
        }
        mock_instance.get_balance.return_value = {
            'result': {'value': 1500000000}  # 1.5 SOL in lamports
        }
        mock_instance.get_signatures_for_address.return_value = {
            'result': [
                {
                    'signature': 'test_signature',
                    'slot': 123456789,
                    'err': None,
                    'blockTime': 1632152400
                }
            ]
        }
        mock_client.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_keypair():
    """Create a mock Solana keypair"""
    with patch('app.services.solana_wallet.Keypair') as mock_keypair:
        # Setup mock keypair
        keypair_instance = MagicMock()
        keypair_instance.public_key = TEST_PUBLIC_KEY
        mock_keypair.from_secret_key.return_value = keypair_instance
        yield keypair_instance


def test_wallet_initialization(mock_solana_client, mock_keypair):
    """Test wallet initialization"""
    wallet = SolanaWallet(TEST_PRIVATE_KEY, TEST_RPC_URL)
    
    assert wallet.public_key == TEST_PUBLIC_KEY
    assert wallet.network == "devnet"
    assert wallet.network_version['result']['solana-core'] == '1.14.10'
    mock_solana_client.get_version.assert_called_once()


def test_get_balance(mock_solana_client, mock_keypair):
    """Test getting wallet balance"""
    wallet = SolanaWallet(TEST_PRIVATE_KEY, TEST_RPC_URL)
    balance = wallet.get_balance()
    
    assert balance == 1.5  # 1.5 SOL
    mock_solana_client.get_balance.assert_called_once()


def test_get_recent_transactions(mock_solana_client, mock_keypair):
    """Test getting recent transactions"""
    wallet = SolanaWallet(TEST_PRIVATE_KEY, TEST_RPC_URL)
    transactions = wallet.get_recent_transactions(limit=1)
    
    assert len(transactions) == 1
    assert transactions[0]['signature'] == 'test_signature'
    assert transactions[0]['slot'] == 123456789
    mock_solana_client.get_signatures_for_address.assert_called_once()


def test_transfer_sol(mock_solana_client, mock_keypair):
    """Test SOL transfer functionality"""
    # Setup mock send_transaction response
    mock_solana_client.send_transaction.return_value = {
        'result': 'transaction_signature'
    }
    
    # Create wallet and transfer SOL
    wallet = SolanaWallet(TEST_PRIVATE_KEY, TEST_RPC_URL)
    recipient = "BVEgXEiMhGfusNB7jrVJfgKNqsvEQj5LpxsAVpvPzxZQ"
    amount = 0.1
    
    signature = wallet.transfer_sol(recipient, amount)
    
    assert signature == 'transaction_signature'
    assert mock_solana_client.send_transaction.called
    
    # Check transaction was cached
    assert 'transaction_signature' in wallet.tx_history
    assert wallet.tx_history['transaction_signature']['amount'] == 0.1
    assert wallet.tx_history['transaction_signature']['recipient'] == recipient


def test_initialize_and_get_wallet(mock_solana_client, mock_keypair):
    """Test global wallet initialization and retrieval"""
    # Reset global wallet instance
    import app.services.solana_wallet
    app.services.solana_wallet._wallet_instance = None
    
    # Initialize wallet
    wallet = initialize_wallet(TEST_PRIVATE_KEY, TEST_RPC_URL)
    assert wallet.public_key == TEST_PUBLIC_KEY
    
    # Get wallet
    retrieved_wallet = get_wallet()
    assert retrieved_wallet is wallet  # Should be the same instance 