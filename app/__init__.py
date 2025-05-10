"""
Solana Vault MCP - Flask Application
A Model Context Protocol (MCP) implementation for the Solana blockchain using Python
"""
import os
import json
from flask import Flask
from flask_cors import CORS
from loguru import logger
import dotenv
from app.utils.logger import setup_logging

def create_app(test_config=None):
    """Create and configure the Flask application"""
    # Load environment variables
    dotenv.load_dotenv()
    
    # Configure logging
    setup_logging()
    logger.info("Starting Solana Vault MCP")
    
    # Create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    
    # Set default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev"),
        PORT=int(os.environ.get("PORT", 5000)),
        RPC_URL=os.environ.get("RPC_URL", "https://api.mainnet-beta.solana.com"),
        SOLANA_PRIVATE_KEY=os.environ.get("SOLANA_PRIVATE_KEY"),
        LOG_LEVEL=os.environ.get("LOG_LEVEL", "INFO"),
        RATE_LIMIT_PER_MINUTE=int(os.environ.get("RATE_LIMIT_PER_MINUTE", 100)),
        VERSION="1.0.0"
    )
    
    # Load development configuration if available
    try:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "dev_config.json")
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config_data = json.load(f)
                if "version" in config_data:
                    app.config["VERSION"] = config_data["version"]
                logger.info(f"Loaded dev config from {config_path}")
    except Exception as e:
        logger.warning(f"Could not load dev config: {str(e)}")
    
    # Load test config if provided
    if test_config is not None:
        app.config.from_mapping(test_config)
        logger.info("Test configuration loaded")
    
    # Enable CORS
    CORS(app)
    
    # Create instance directory if needed
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Register blueprints
    from app.routes.web import web_bp
    from app.routes.mcp import mcp_bp
    
    app.register_blueprint(web_bp)
    app.register_blueprint(mcp_bp)
    
    # Initialize Solana wallet
    if app.config.get("SOLANA_PRIVATE_KEY"):
        try:
            from app.services.solana_wallet import initialize_wallet
            initialize_wallet(app.config["SOLANA_PRIVATE_KEY"], app.config["RPC_URL"])
            logger.info(f"Wallet initialized with RPC: {app.config['RPC_URL']}")
        except Exception as e:
            logger.error(f"Failed to initialize wallet: {str(e)}")
    else:
        logger.warning("No Solana private key provided. Wallet not initialized.")
    
    logger.info(f"Flask app initialized on port {app.config.get('PORT', 5000)}")
    return app 