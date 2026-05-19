"""CLI entry point — wires user input to order placement."""

import typer
import requests

from bot.client import BinanceClient
from bot import orders
from bot.logging_config import setup_logger

app = typer.Typer(
    help="Binance Futures Testnet trading bot — place MARKET / LIMIT orders.",
    add_completion=False,
)
logger = setup_logger()


@app.command()
def place(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading pair, e.g. BTCUSDT"),
    side: str = typer.Option(..., "--side", help="BUY or SELL"),
    order_type: str = typer.Option(
            ..., "--order-type", "-t", help="MARKET, LIMIT, or STOP_LIMIT"
        ),
    quantity: float = typer.Option(..., "--quantity", "-q", help="Order quantity"),
    price: float = typer.Option(None, "--price", "-p", help="Price (required for LIMIT only)"),
    stop_price: float = typer.Option(
        None, "--stop-price", help="Trigger price (required for STOP_LIMIT only)"
    ),
):
    """Place an order on Binance Futures Testnet."""

    # 1. Request summary — print BEFORE we hit the network
    typer.echo("\n========== Order Request ==========")
    typer.echo(f"  Symbol     : {symbol.upper()}")
    typer.echo(f"  Side       : {side.upper()}")
    typer.echo(f"  Order Type : {order_type.upper()}")
    typer.echo(f"  Quantity   : {quantity}")
    if price is not None:
        typer.echo(f"  Price      : {price}")
    typer.echo("===================================\n")
    if stop_price is not None:
        typer.echo(f"  Stop Price : {stop_price}")

    try:
        client = BinanceClient()

        # 2. Dispatch to the right order function
        order_type_upper = order_type.upper()
        if order_type_upper == "MARKET":
            response = orders.place_market_order(client, symbol, side, quantity)
        elif order_type_upper == "LIMIT":
            response = orders.place_limit_order(client, symbol, side, quantity, price)
        elif order_type_upper == "STOP_LIMIT":
            response = orders.place_stop_limit_order(
                client, symbol, side, quantity, price, stop_price
            )
        else:
            raise ValueError(f"Unsupported order type: {order_type}")

        # 3. Response details — algo orders return algoId/algoStatus, regular orders return orderId/status
        typer.echo("========== Order Response =========")
        typer.echo(f"  Order ID     : {response.get('orderId') or response.get('algoId')}")
        typer.echo(f"  Status       : {response.get('status') or response.get('algoStatus')}")
        typer.echo(f"  Executed Qty : {response.get('executedQty', 'N/A')}")
        typer.echo(f"  Avg Price    : {response.get('avgPrice', 'N/A')}")
        typer.echo("===================================")
        typer.secho("[OK] Order placed successfully.\n", fg=typer.colors.GREEN)
        logger.info(
            f"Order placed — id={response.get('orderId') or response.get('algoId')}, "
            f"status={response.get('status') or response.get('algoStatus')}"
        )

    except ValueError as e:
        typer.secho(f"[FAIL] Invalid input: {e}", fg=typer.colors.RED, err=True)
        logger.error(f"Validation error: {e}")
        raise typer.Exit(code=1)

    except requests.HTTPError as e:
        msg = f"{e.response.status_code} {e.response.text}"
        typer.secho(f"[FAIL] Binance API error: {msg}", fg=typer.colors.RED, err=True)
        logger.error(f"API error: {msg}")
        raise typer.Exit(code=2)

    except requests.RequestException as e:
        typer.secho(f"[FAIL] Network error: {e}", fg=typer.colors.RED, err=True)
        logger.error(f"Network error: {e}")
        raise typer.Exit(code=3)

    except Exception as e:
        typer.secho(f"[FAIL] Unexpected error: {e}", fg=typer.colors.RED, err=True)
        logger.exception("Unexpected error")
        raise typer.Exit(code=99)


if __name__ == "__main__":
    app()