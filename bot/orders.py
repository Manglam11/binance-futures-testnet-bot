"""Order placement logic — validates inputs, builds API params, calls client."""

from bot import validators
from bot.logging_config import setup_logger

logger = setup_logger()

def place_market_order(client, symbol: str, side: str, quantity) -> dict:
    """Place a MARKET order (executes immediately at current price)."""
    logger.info(f"Placing MARKET {side} order — {quantity} {symbol}")
    # 1. Validate everything before touching the network
    symbol = validators.validate_symbol(symbol)
    side = validators.validate_side(side)
    quantity = validators.validate_quantity(quantity)

    # 2. Build the params Binance expects (no price, no timeInForce for MARKET)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "MARKET",
        "quantity": quantity,
    }

    # 3. Send to Binance via our signed client
    return client.post("/fapi/v1/order", params)


def place_limit_order(
    client, symbol: str, side: str, quantity, price
) -> dict:
    """Place a LIMIT order (executes only when market reaches your price)."""
    logger.info(f"Placing LIMIT {side} order — {quantity} {symbol} @ {price}")
    # 1. Validate
    symbol = validators.validate_symbol(symbol)
    side = validators.validate_side(side)
    quantity = validators.validate_quantity(quantity)
    price = validators.validate_price(price, "LIMIT")

    # 2. Build params — LIMIT needs price + timeInForce (GTC = stays open until filled)
    params = {
        "symbol": symbol,
        "side": side,
        "type": "LIMIT",
        "quantity": quantity,
        "price": price,
        "timeInForce": "GTC",
    }

    # 3. Send
    return client.post("/fapi/v1/order", params)