"""Order placement logic — validates inputs, builds API params, calls client."""

from bot import validators
from bot.logging_config import setup_logger

logger = setup_logger()

def place_market_order(client, symbol: str, side: str, quantity) -> dict:
    """Place a MARKET order (executes immediately at current price)."""
    # Validate FIRST
    symbol = validators.validate_symbol(symbol)
    side = validators.validate_side(side)
    quantity = validators.validate_quantity(quantity)

    # Only log "placing" once inputs are confirmed valid
    logger.info(f"Placing MARKET {side} order - {quantity} {symbol}")

    # Build + send
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }
    return client.post("/fapi/v1/order", params)

def place_limit_order(
    client, symbol: str, side: str, quantity, price
) -> dict:
    """Place a LIMIT order (executes only when market reaches your price)."""
    symbol = validators.validate_symbol(symbol)
    side = validators.validate_side(side)
    quantity = validators.validate_quantity(quantity)
    price = validators.validate_price(price, "LIMIT")

    logger.info(f"Placing LIMIT {side} order — {quantity} {symbol} @ {price}")

    # Build params — LIMIT needs price + timeInForce (GTC = stays open until filled)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC",
    }

    # Send
    return client.post("/fapi/v1/order", params)