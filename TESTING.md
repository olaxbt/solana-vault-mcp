# Testing the Solana Vault MCP

This guide will help you verify the functionality of your Solana Vault MCP implementation.

## Prerequisites

Before testing, make sure you have:

1. Installed all dependencies with `pip install -r requirements.txt`
2. Created a `.env` file based on `.env.example` with your Solana private key and RPC URL
3. Added test SOL to your wallet if you're testing on devnet/testnet
   - For devnet, you can use the [Solana Faucet](https://solfaucet.com/) to get free test SOL

## Unit Tests

The repository includes unit tests that mock Solana RPC responses to test the wallet functionality without making actual blockchain calls:

```bash
# Run all tests
pytest

# Run specific tests
pytest tests/test_wallet.py
```

## Manual Testing

### 1. Starting the Server

First, start the server:

```bash
python run.py
```

The server should start and you should see log messages indicating:
- The Flask app was initialized
- The wallet was initialized
- The server is listening on the configured port (default 5000)

### 2. Testing the API Endpoints

#### Health Check

```bash
curl http://localhost:5000/health
```

You should receive a JSON response with server status information.

#### MCP Ping Endpoint

```bash
curl http://localhost:5000/api/mcp/ping
```

You should see a response with wallet information, network status, and service details.

### 3. Testing MCP Queries

To test MCP queries, you can use the CLI tool:

```bash
# Check wallet information
python cli.py info

# Check SOL balance
python cli.py balance

# Get recent transactions
python cli.py transactions --limit 5
```

For transfer operations, be cautious as they will move actual SOL (use a devnet wallet):

```bash
# Transfer 0.01 SOL to another address
python cli.py transfer RECIPIENT_ADDRESS 0.01
```

### 4. Integration with MCP Clients

If you're using this with an MCP-compatible client like Claude, you can test it with this prompt:

```
Check my Solana wallet balance and recent transactions.
```

## Common Issues and Troubleshooting

### Connection Issues

- **Problem**: "Failed to connect to Solana RPC"
- **Solution**: Verify your RPC URL in the .env file. Make sure it's accessible and not rate-limited.

### Wallet Initialization Failures

- **Problem**: "Wallet not initialized" errors
- **Solution**: Ensure your Solana private key is correctly formatted (base58 encoded) and set in the .env file.

### Transaction Failures

- **Problem**: Transfer fails with "insufficient balance"
- **Solution**: Make sure your wallet has enough SOL to cover both the transfer amount and transaction fees.

## Monitoring Logs

The application logs to both the console and files in the `logs/` directory:

```bash
# View the latest logs
tail -f logs/solana_mcp.log

# Check for errors specifically
cat logs/errors.log
```

## Getting Help

If you encounter issues not covered here, please:

1. Review the [Solana Developer Documentation](https://docs.solana.com/)
2. Open an issue on the repository with details about your problem 