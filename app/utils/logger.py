"""
Logging setup for Solana Vault MCP
"""
import os
import sys
from loguru import logger
import datetime

def setup_logging():
    """Configure the logger for the application"""
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_file = os.environ.get("LOG_FILE", "logs/solana_mcp.log")
    
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    logger.remove()
    
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    logger.add(
        log_file,
        rotation="10 MB",
        retention="1 week",
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True
    )
    
    logger.add(
        "logs/errors.log",
        rotation="5 MB",
        retention="1 week",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        backtrace=True,
        diagnose=True,
        filter=lambda record: record["level"].name == "ERROR"
    )
    
    logger.info(f"Logging initialized at level {log_level}")
    return logger


def get_component_logger(component_name):
    """Create a contextualized logger for a specific component"""
    return logger.bind(component=component_name) 