"""
MCP Routes
Implements the Model Context Protocol for Solana Vault operations
"""
from flask import Blueprint, request, jsonify, current_app
import json
from model_context_protocol import MCPRequest, MCPResponse
from app.utils.logger import get_component_logger
from app.services.solana_wallet import get_wallet
from app.handlers.wallet_actions import handle_wallet_action

logger = get_component_logger("mcp_routes")

# Create Blueprint
mcp_bp = Blueprint('mcp', __name__, url_prefix='/api/mcp')

@mcp_bp.route('/query', methods=['POST'])
def mcp_query():
    """
    Main MCP query endpoint
    Processes MCP requests and returns MCP responses
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data:
            logger.error("Invalid request: No JSON data provided")
            return jsonify({
                "error": "Invalid request: No JSON data provided"
            }), 400
        
        # Parse MCP request
        try:
            mcp_request = MCPRequest(**data)
            logger.info(f"Received MCP request: action={mcp_request.action}")
        except Exception as e:
            logger.error(f"Failed to parse MCP request: {str(e)}")
            return jsonify({
                "error": f"Invalid MCP request format: {str(e)}"
            }), 400
        
        # Process the request based on the action
        if mcp_request.action.startswith("wallet."):
            result = handle_wallet_action(mcp_request)
        else:
            logger.warning(f"Unknown action requested: {mcp_request.action}")
            return jsonify({
                "error": f"Unknown action: {mcp_request.action}"
            }), 400
        
        # Create and return MCP response
        response = MCPResponse(
            id=mcp_request.id,
            result=result
        )
        
        return jsonify(response.dict()), 200
        
    except Exception as e:
        logger.error(f"Error processing MCP request: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}"
        }), 500

@mcp_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    wallet = None
    try:
        wallet = get_wallet()
        network = wallet.network
        address = wallet.public_key
        status = "ready"
    except Exception:
        network = "unknown"
        address = "not_initialized"
        status = "initializing"
    
    return jsonify({
        "service": "solana-vault-mcp",
        "status": status,
        "network": network,
        "wallet": address[:6] + "..." + address[-4:] if address != "not_initialized" else "not_initialized",
        "version": current_app.config.get("VERSION", "1.0.0")
    }), 200 