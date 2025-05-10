"""
Wallet Action Handlers
"""
from typing import Dict, Any, List
from model_context_protocol import MCPRequest
from app.utils.logger import get_component_logger
from app.services.solana_wallet import get_wallet

logger = get_component_logger("wallet_actions")

def handle_wallet_action(request: MCPRequest) -> Dict[str, Any]:
    """Route wallet actions to their appropriate handlers"""
    action = request.action
    params = request.params or {}
    
    logger.info(f"Processing wallet action: {action}")
    
    try:
        wallet = get_wallet()
        
        if action == "wallet.info":
            return get_wallet_info()
        elif action == "wallet.balance":
            return get_sol_balance()
        elif action == "wallet.transfer":
            return transfer_sol(params)
        elif action == "wallet.transactions":
            return get_transactions(params)
        elif action == "wallet.token_balance":
            return get_token_balance(params)
        else:
            logger.error(f"Unknown wallet action: {action}")
            raise ValueError(f"Unknown wallet action: {action}")
    except Exception as e:
        logger.error(f"Error processing wallet action {action}: {str(e)}")
        return {
            "error": str(e),
            "action": action,
            "success": False
        }


def get_wallet_info() -> Dict[str, Any]:
    """Get wallet information"""
    wallet = get_wallet()
    
    return {
        "address": wallet.public_key,
        "network": wallet.network,
        "network_version": wallet.network_version['result']['solana-core'],
        "balance": wallet.get_balance()
    }


def get_sol_balance() -> Dict[str, Any]:
    """Get SOL balance"""
    wallet = get_wallet()
    
    balance = wallet.get_balance()
    
    return {
        "balance": balance,
        "currency": "SOL",
        "address": wallet.public_key
    }


def transfer_sol(params: Dict[str, Any]) -> Dict[str, Any]:
    """Transfer SOL to another wallet"""
    # Validate required parameters
    if 'recipient' not in params:
        raise ValueError("Missing required parameter: recipient")
    if 'amount' not in params:
        raise ValueError("Missing required parameter: amount")
    
    recipient = params['recipient']
    try:
        amount = float(params['amount'])
    except ValueError:
        raise ValueError(f"Invalid amount value: {params['amount']}. Must be a valid number.")
    
    # Validate amount
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")
    
    # Transfer SOL
    wallet = get_wallet()
    signature = wallet.transfer_sol(recipient, amount)
    
    return {
        "success": True,
        "signature": signature,
        "amount": amount,
        "recipient": recipient,
        "explorer_url": f"https://explorer.solana.com/tx/{signature}?cluster={wallet.network}"
    }


def get_transactions(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get recent transactions"""
    try:
        limit = int(params.get('limit', 10))
    except ValueError:
        limit = 10
    
    # Validate limit
    if limit <= 0 or limit > 100:
        limit = 10
    
    wallet = get_wallet()
    transactions = wallet.get_recent_transactions(limit=limit)
    
    return {
        "transactions": transactions,
        "count": len(transactions),
        "address": wallet.public_key
    }


def get_token_balance(params: Dict[str, Any]) -> Dict[str, Any]:
    """Get token balance for a specific token"""
    # Validate required parameters
    if 'token_mint' not in params:
        raise ValueError("Missing required parameter: token_mint")
    
    token_mint = params['token_mint']
    
    wallet = get_wallet()
    token_data = wallet.get_token_balance(token_mint)
    
    return {
        "token_mint": token_mint,
        "balance": token_data.get("ui_amount", 0),
        "raw_balance": token_data.get("amount", "0"),
        "decimals": token_data.get("decimals", 0),
        "address": wallet.public_key
    } 