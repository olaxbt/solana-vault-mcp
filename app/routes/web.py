"""
Web Routes
Provides routes for the web interface
"""
from flask import Blueprint, render_template, redirect, url_for, current_app, jsonify
from app.utils.logger import get_component_logger
from app.services.solana_wallet import get_wallet

logger = get_component_logger("web_routes")

# Create blueprint
web_bp = Blueprint('web', __name__)

@web_bp.route('/')
def index():
    """Home page"""
    try:
        wallet = get_wallet()
        return jsonify({
            "service": "Solana Vault MCP",
            "status": "running",
            "endpoints": {
                "mcp_query": "/api/mcp/query",
                "health": "/api/mcp/ping"
            },
            "wallet": {
                "address": wallet.public_key,
                "network": wallet.network,
                "balance": f"{wallet.get_balance():.6f} SOL"
            }
        })
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify({
            "service": "Solana Vault MCP",
            "status": "initializing",
            "error": str(e)
        })

@web_bp.route('/health')
def health():
    """Health check endpoint"""
    try:
        wallet = get_wallet()
        return jsonify({
            "status": "healthy",
            "wallet_initialized": True,
            "wallet_address": wallet.public_key,
            "network": wallet.network
        }), 200
    except Exception as e:
        logger.warning(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "initializing",
            "wallet_initialized": False,
            "error": str(e)
        }), 503  # Service Unavailable 