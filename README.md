# Solana Vault MCP

A Model Context Protocol (MCP) implementation for secure Solana blockchain wallet operations in python.

## Overview

Solana Vault MCP provides secure wallet operations for Solana blockchain through a standardized Model Context Protocol interface. It allows AI assistants to securely interact with the Solana blockchain without direct access to private keys.

## Features

- Secure Solana wallet operations
- SOL balance checking
- SOL transfer capabilities
- Transaction history retrieval
- Model Context Protocol compliant API
- Support for Flask web server and WebSocket connections
- Detailed logging and error handling

## Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/olaxbt/solana-vault-mcp.git
   cd solana-vault-mcp
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Edit the `.env` file to add your Solana private key and RPC URL.

## Usage

### Starting the Server

```bash
python run.py
```

The server will start on the port specified in your `.env` file (default: 5000).

### API Endpoints

- `GET /` - Welcome page with service information
- `GET /health` - Health check endpoint
- `GET /api/mcp/ping` - MCP service health check
- `POST /api/mcp/query` - Main MCP query endpoint

### MCP Actions

The Solana Vault MCP supports the following actions:

1. `wallet.info` - Get wallet information
2. `wallet.balance` - Get SOL balance
3. `wallet.transfer` - Transfer SOL to another wallet
4. `wallet.transactions` - Get recent transactions
5. `wallet.token_balance` - Get token balance for a specific token

### Example Query

```json
{
  "id": "request123",
  "action": "wallet.balance",
  "params": {}
}
```

Response:
```json
{
  "id": "request123",
  "result": {
    "balance": 1.5,
    "currency": "SOL",
    "address": "YourSolanaPublicKey"
  }
}
```

## Development

### Project Structure

```
solana-vault-mcp/
├── app/
│   ├── handlers/        # Action handlers
│   ├── routes/          # API routes
│   ├── services/        # Core services
│   └── utils/           # Utilities
├── logs/                # Log files
├── tests/               # Test cases
├── .env                 # Environment variables
├── .env.example         # Example environment file
├── requirements.txt     # Dependencies
├── run.py               # Main entry point
└── README.md            # Documentation
```

### Running Tests

```bash
pytest
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 