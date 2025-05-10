#!/usr/bin/env python3
"""
Solana Vault MCP - Main entry point
Run this file to start the Solana Vault MCP server
"""
from app import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config.get("PORT", 5000)) 