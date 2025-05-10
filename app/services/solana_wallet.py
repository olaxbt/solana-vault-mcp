"""
Solana Wallet Service
"""
import base58
import datetime
from typing import Optional, Dict, Any, List
from solana.rpc.api import Client
from solana.publickey import PublicKey
from solana.keypair import Keypair
from solana.rpc.types import TxOpts
from solana.transaction import Transaction
from solana.system_program import TransferParams, transfer
from solana.rpc.commitment import Confirmed
from solana.exceptions import SolanaRpcException
from app.utils.logger import get_component_logger

logger = get_component_logger("SolanaWallet")

# Global wallet instance
_wallet_instance = None

def initialize_wallet(private_key: str, rpc_url: str) -> 'SolanaWallet':
    """Initialize the global wallet instance"""
    global _wallet_instance
    if _wallet_instance is None:
        try:
            _wallet_instance = SolanaWallet(private_key, rpc_url)
            logger.info(f"Wallet initialized with address: {_wallet_instance.public_key}")
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {str(e)}")
            raise
    return _wallet_instance

def get_wallet() -> 'SolanaWallet':
    """Get the global wallet instance"""
    if _wallet_instance is None:
        raise ValueError("Wallet not initialized. Call initialize_wallet first.")
    return _wallet_instance


class SolanaWallet:
    """SolanaWallet provides an interface to interact with the Solana blockchain"""
    
    def __init__(self, private_key: str, rpc_url: str):
        """Initialize a Solana wallet with a private key and RPC URL"""
        try:
            # Decode private key and create keypair
            decoded_key = base58.b58decode(private_key)
            self.keypair = Keypair.from_secret_key(bytes(decoded_key))
            self.public_key = str(self.keypair.public_key)
            
            # Initialize Solana client
            self.client = Client(rpc_url)
            
            # Test connection and get version
            version_response = self.client.get_version()
            if "result" not in version_response:
                raise ValueError(f"Failed to connect to Solana RPC: {version_response}")
                
            self.network_version = version_response
            self.network = self._get_network_name(rpc_url)
            
            # Transaction history cache
            self.tx_history = {}
            
            logger.info(f"Wallet connected to {self.network} network, version: {self.network_version['result']['solana-core']}")
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {str(e)}")
            raise ValueError(f"Failed to initialize Solana wallet: {str(e)}")
    
    def get_balance(self) -> float:
        """Get SOL balance of the wallet"""
        try:
            resp = self.client.get_balance(self.keypair.public_key)
            if "result" not in resp:
                raise ValueError(f"Failed to get balance: {resp}")
                
            balance_lamports = resp['result']['value']
            # Convert lamports to SOL (1 SOL = 1e9 lamports)
            balance_sol = balance_lamports / 1_000_000_000
            return balance_sol
        except Exception as e:
            logger.error(f"Failed to get balance: {str(e)}")
            raise ValueError(f"Failed to get SOL balance: {str(e)}")
    
    def transfer_sol(self, recipient: str, amount: float) -> str:
        """Transfer SOL to another wallet"""
        try:
            # Convert recipient to PublicKey
            recipient_pubkey = PublicKey(recipient)
            
            # Convert SOL to lamports
            lamports = int(amount * 1_000_000_000)
            
            # Check if we have enough balance
            balance_resp = self.client.get_balance(self.keypair.public_key)
            if "result" not in balance_resp:
                raise ValueError(f"Failed to get balance: {balance_resp}")
                
            current_balance = balance_resp['result']['value']
            if current_balance < lamports:
                raise ValueError(f"Insufficient balance. Available: {current_balance/1e9} SOL, Requested: {amount} SOL")
            
            # Create transfer instruction
            transfer_instruction = transfer(
                TransferParams(
                    from_pubkey=self.keypair.public_key,
                    to_pubkey=recipient_pubkey,
                    lamports=lamports
                )
            )
            
            # Create and sign transaction
            transaction = Transaction().add(transfer_instruction)
            
            # Send transaction
            opts = TxOpts(skip_preflight=False, preflight_commitment=Confirmed)
            response = self.client.send_transaction(
                transaction, 
                self.keypair, 
                opts=opts
            )
            
            # Check for errors
            if "error" in response:
                logger.error(f"Transfer failed: {response['error']}")
                raise ValueError(f"Transfer failed: {response['error']}")
            
            if "result" not in response:
                raise ValueError(f"Unexpected response format: {response}")
                
            signature = response["result"]
            
            # Cache transaction
            self.tx_history[signature] = {
                "type": "transfer",
                "amount": amount,
                "recipient": recipient,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
            logger.info(f"Transferred {amount} SOL to {recipient}, signature: {signature}")
            return signature
            
        except Exception as e:
            logger.error(f"Failed to transfer SOL: {str(e)}")
            raise ValueError(f"Failed to transfer SOL: {str(e)}")
    
    def get_token_balance(self, token_mint: str) -> Dict[str, Any]:
        """Get token balance for a specific token"""
        try:
            # Implementation requires spl-token support
            # Placeholder for now
            logger.warning("Token balance functionality is not fully implemented yet")
            return {
                "mint": token_mint,
                "amount": "0",
                "decimals": 0,
                "ui_amount": 0
            }
        except Exception as e:
            logger.error(f"Failed to get token balance: {str(e)}")
            raise ValueError(f"Failed to get token balance: {str(e)}")
    
    def get_transaction(self, signature: str) -> Dict[str, Any]:
        """Get transaction details by signature"""
        try:
            response = self.client.get_transaction(signature)
            
            if "error" in response:
                logger.error(f"Failed to get transaction: {response['error']}")
                raise ValueError(f"Failed to get transaction: {response['error']}")
            
            if "result" not in response:
                raise ValueError(f"Unexpected response format: {response}")
                
            return response["result"]
        except Exception as e:
            logger.error(f"Failed to get transaction: {str(e)}")
            raise ValueError(f"Failed to get transaction: {str(e)}")
    
    def get_recent_transactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent transactions for the wallet"""
        try:
            response = self.client.get_signatures_for_address(
                self.keypair.public_key,
                limit=limit
            )
            
            if "error" in response:
                logger.error(f"Failed to get recent transactions: {response['error']}")
                raise ValueError(f"Failed to get recent transactions: {response['error']}")
            
            if "result" not in response:
                raise ValueError(f"Unexpected response format: {response}")
            
            # Format the results
            transactions = []
            for tx in response["result"]:
                transaction_data = {
                    "signature": tx["signature"],
                    "slot": tx["slot"],
                    "err": tx["err"],
                    "memo": tx.get("memo", None),
                }
                
                if "blockTime" in tx:
                    transaction_data["block_time"] = tx["blockTime"]
                
                transactions.append(transaction_data)
            
            return transactions
        except Exception as e:
            logger.error(f"Failed to get recent transactions: {str(e)}")
            raise ValueError(f"Failed to get recent transactions: {str(e)}")
    
    def _get_network_name(self, rpc_url: str) -> str:
        """Get network name from RPC URL"""
        if "mainnet" in rpc_url:
            return "mainnet"
        elif "testnet" in rpc_url:
            return "testnet"
        elif "devnet" in rpc_url:
            return "devnet"
        else:
            return "unknown" 