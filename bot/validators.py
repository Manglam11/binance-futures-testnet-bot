"""Input validators for trading bot — fail fast with clear messages."""

_VALID_SIDES = {"BUY", "SELL"}
_VALID_TYPES = {"MARKET", "LIMIT"}

def validate_symbol(symbol: str) -> str:
    """Validate and normalize a trading symbol.

    Returns the cleaned uppercase symbol (e.g., 'btcusdt' → 'BTCUSDT').
    Raises ValueError with a human-readable message if invalid.
    """
    if not isinstance(symbol, str):
        raise ValueError(
            f"Symbol must be a string, got {type(symbol).__name__}"
        )

    if not symbol:
        raise ValueError("Symbol cannot be empty")


    symbol = symbol.strip().upper()

    if not symbol.endswith("USDT"):
        raise ValueError(
            f"Symbol must end with 'USDT', got '{symbol}'"
        )

    if len(symbol) <= 4:
        raise ValueError(
            f"Symbol missing base asset before 'USDT', got '{symbol}' only"
        )

    return symbol


def validate_side(side: str) -> str:
    """
    Validate and normalize an order side.

    Returns the cleaned uppercase side ('buy' → 'BUY').

    Raises ValueError if side is not 'BUY' or 'SELL'.
    """
    if not isinstance(side, str):
        raise ValueError(
            f"Side must be a string, got {type(side).__name__}"
        )

    side = side.strip().upper()

    if side not in _VALID_SIDES:
        raise ValueError(
            f"Side must be one of {sorted(_VALID_SIDES)}, got '{side}'"
        )
    return side

def validate_order_type(order_type: str) -> str:
    """
    Validate and normalize an order type.

    Returns the cleaned uppercase type ('market' → 'MARKET').

    Raises ValueError if order_type is not 'MARKET' or 'LIMIT'.
    """
    if not isinstance(order_type, str):
        raise ValueError(
            f"Type must be a string, got {type(order_type).__name__}"
        )

    order_type = order_type.strip().upper()

    if order_type not in _VALID_TYPES:
        raise ValueError(
            f"Order type must be one of {sorted(_VALID_TYPES)}, got '{order_type}'"
        )
    return order_type

def validate_quantity(quantity) -> float:
    """Validate and normalize an order quantity.

    Accepts string or number input. Returns positive float.

    Raises ValueError if quantity is not a positive number.
    """
    try:
        quantity = float(quantity)  # try to convert
    except (ValueError, TypeError) as e :  # if it crashes...
        raise ValueError(f"Quantity must be a number, got '{quantity}'") from e
    if quantity <= 0:
        raise ValueError(f"Quantity must be positive, got {quantity}")
    return quantity


def validate_price(price, order_type: str) -> float | None:
    """Validate the price field based on order type.

    For MARKET orders, price must be None — returns None.
    For LIMIT orders, price must be a positive number — returns the cleaned float.

    Raises ValueError for invalid combinations.
    """
    # Step 1: order_type is "MARKET" — price MUST be None, otherwise raise
    if order_type == "MARKET":
        if price is not None:
            raise ValueError(f"MARKET orders must not specify a price, got {price}")

        return None

    if order_type == "LIMIT":
        if price is None:
            raise ValueError(f"With order type {order_type} price can not be {price}")
        try:
            price = float(price)
        except (ValueError, TypeError):
            raise ValueError(f"Price must be a number, got '{price}'")
        if price <= 0:
            raise ValueError(f"Price value must be greater than 0 got {price} instead")
        return price


