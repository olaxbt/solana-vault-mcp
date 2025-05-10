#!/usr/bin/env python3
"""
Solana Vault MCP - CLI Tool
Command line interface for interacting with Solana Vault MCP
"""
import os
import sys
import click
import json
import requests
from dotenv import load_dotenv
from model_context_protocol import MCPRequest

# Load environment variables
load_dotenv()

# Default server URL
DEFAULT_SERVER_URL = f"http://localhost:{os.environ.get('PORT', 5000)}"


@click.group()
@click.option('--url', default=DEFAULT_SERVER_URL, help='MCP server URL')
@click.pass_context
def cli(ctx, url):
    """Solana Vault MCP - CLI Tool"""
    ctx.ensure_object(dict)
    ctx.obj['url'] = url


@cli.command()
@click.pass_context
def ping(ctx):
    """Check if the MCP server is running"""
    try:
        response = requests.get(f"{ctx.obj['url']}/api/mcp/ping")
        if response.status_code == 200:
            data = response.json()
            click.echo(click.style("✅ MCP Server is running", fg="green"))
            click.echo(f"Service: {data.get('service', 'Unknown')}")
            click.echo(f"Status: {data.get('status', 'Unknown')}")
            click.echo(f"Network: {data.get('network', 'Unknown')}")
            click.echo(f"Wallet: {data.get('wallet', 'Unknown')}")
            click.echo(f"Version: {data.get('version', 'Unknown')}")
        else:
            click.echo(click.style(f"❌ Error: {response.status_code} - {response.text}", fg="red"))
    except requests.RequestException as e:
        click.echo(click.style(f"❌ Connection Error: {str(e)}", fg="red"))


@cli.command()
@click.pass_context
def info(ctx):
    """Get wallet information"""
    _send_mcp_request(ctx, "wallet.info")


@cli.command()
@click.pass_context
def balance(ctx):
    """Get SOL balance"""
    _send_mcp_request(ctx, "wallet.balance")


@cli.command()
@click.argument('recipient')
@click.argument('amount', type=float)
@click.pass_context
def transfer(ctx, recipient, amount):
    """Transfer SOL to another wallet"""
    _send_mcp_request(ctx, "wallet.transfer", {
        "recipient": recipient,
        "amount": amount
    })


@cli.command()
@click.option('--limit', default=10, help='Number of transactions to retrieve')
@click.pass_context
def transactions(ctx, limit):
    """Get recent transactions"""
    _send_mcp_request(ctx, "wallet.transactions", {
        "limit": limit
    })


@cli.command()
@click.argument('token_mint')
@click.pass_context
def token_balance(ctx, token_mint):
    """Get token balance for a specific token"""
    _send_mcp_request(ctx, "wallet.token_balance", {
        "token_mint": token_mint
    })


def _send_mcp_request(ctx, action, params=None):
    """Send MCP request and display the result"""
    try:
        req = MCPRequest(
            id=f"cli-{action}",
            action=action,
            params=params or {}
        )
        
        response = requests.post(
            f"{ctx.obj['url']}/api/mcp/query",
            json=req.dict(),
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if "result" in data:
                click.echo(click.style(f"✅ Success: {action}", fg="green"))
                click.echo(json.dumps(data["result"], indent=2))
            else:
                click.echo(click.style(f"⚠️ No result data: {data}", fg="yellow"))
        else:
            click.echo(click.style(f"❌ Error {response.status_code}: {response.text}", fg="red"))
    except requests.RequestException as e:
        click.echo(click.style(f"❌ Connection Error: {str(e)}", fg="red"))
    except Exception as e:
        click.echo(click.style(f"❌ Error: {str(e)}", fg="red"))


if __name__ == '__main__':
    cli(obj={}) 