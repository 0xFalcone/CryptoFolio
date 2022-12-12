import argparse
import requests
import json
import csv
from pyfiglet import Figlet
from tabulate import tabulate
from requests import Session


def main():

    # Check for new or existing user to create or load portfolio
    if new_user():
        portfolio = new_port()
    else:
        portfolio = load_port()

    # Check if a buy or sell transaction is being entered
    if command() == "buy":
        portfolio = add_buy(portfolio)
    elif command() == "sell":
        portfolio = add_sell(portfolio)

    # Update portfolio with current values
    portfolio = update(portfolio)
    total = total_value(portfolio)

    # Update Ethereum network gas fees
    gas = current_gas_fee()

    # Display CryptoFolio title ascii graphic
    print(title())

    # Display final report in table
    display(portfolio, total, gas)



def command():
    # Read and process command line arguments for buy/sell transactions

    parser = argparse.ArgumentParser(description="Track your crypto portfolio")
    parser.add_argument("-b", help="Enter a Buy transaction", action="store_true")
    parser.add_argument("-s", help="Enter a Sell transaction", action="store_true")
    args = parser.parse_args()

    if args.b:
        return "buy"
    elif args.s:
        return "sell"


def new_user():
    # Check for an existing portfolio

    try:
        with open("portfolio.csv", "r", newline='') as file:
            reader = csv.DictReader(file)
    except FileNotFoundError:
        return True


def load_port():
    # Read csv file from disk and format as a dictionary

    port = {}
    try:
        with open("portfolio.csv", "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                port[row["symbol"]] = {"symbol": row["symbol"],\
                    "amount": float(row["amount"])}
    except FileNotFoundError:
        print("No existing portfolio found. Let's set up a new portfolio for you")
    return port


def new_port():
    # Create a new portfolio from user input

    print(title())
    print("\nWelcome to CryptoFolio! Let's set up your portfolio...")
    port = enter_coins()
    write_csv(port)
    return port


def enter_coins():
    # Prompt and check for correct coin symbol input

    listings = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'BUSD', 'BNB', 'XRP', 'ADA', 'SOL',
                'DOGE', 'DAI', 'DOT', 'TRX', 'SHIB', 'LEO', 'AVAX', 'WBTC', 'MATIC', 'UNI',
                'LTC', 'FTT', 'BNB', 'LINK', 'CRO', 'XLM', 'NEAR', 'ATOM', 'XMR', 'ALGO',
                'ETC', 'BCH', 'ICP', 'VET', 'FLOW', 'MANA', 'XTZ', 'SAND', 'APE', 'HBAR',
                'FIL', 'TUSD', 'BNB', 'THETA', 'EGLD', 'AXS', 'HNT', 'QNT', 'AAVE', 'BSV',
                'USDP', 'EOS', 'KCS', 'MKR', 'ZEC', 'BTT', 'TRX', 'USDN', 'MIOTA', 'XEC',
                'OKB', 'USDD', 'RUNE', 'BNB', 'HT', 'GRT', 'CHZ', 'KLAY', 'FTM', 'NEO',
                'PAXG', 'BAT', 'LRC', 'WAVES', 'GMT', 'BNB', 'STX', 'ZIL', 'CRV', 'USTC',
                'DASH', 'ENJ', 'FEI', 'CAKE', 'BNB', 'KSM', 'AR', 'MINA', 'KAVA', 'CELO',
                'AMP', 'COMP', 'NEXO', 'CVX', 'XEM', 'GALA', 'HOT', '1INCH', 'XDC', 'DCR',
                'GT', 'GNO', 'XYM', 'QTUM', 'KDA', 'SNX', 'IOTX']

    print("\nEnter each cryptocurrency followed by their amounts. Press Enter when done.\n")

    port_input = {}
    while True:
        symbol = input("Crypto symbol: ").upper()
        if symbol == "":
            break
        elif symbol in listings:
            pass
        else:
            print("Symbol not found. Please enter a valid token symbol.")
            continue

        try:
            amount = float(input(f"{symbol} amount: "))
        except ValueError:
            continue
        if amount == "":
            break
        elif amount > 0:
            pass
        port_input[symbol] = {"symbol": symbol, "amount": amount}
    return port_input


def add_buy(port):
    # Add new buy transaction to portfolio

    print("\nLet's add a Buy transaction...")
    coins_held = list(port.keys())
    tx = enter_coins()

    for coin in tx:
        if coin in coins_held:
            port[coin]["amount"] = port[coin]["amount"] + tx[coin]["amount"]
        else:
            port[coin] = tx[coin]
    write_csv(port)
    return port


def add_sell(port):
    # Add new sell transaction to portfolio

    print("\nLet's add a Sell transaction...")
    coins_held = list(port.keys())
    tx = enter_coins()

    for coin in tx:
        if coin in coins_held:
            port[coin]["amount"] = port[coin]["amount"] - tx[coin]["amount"]
        else:
            port[coin] = tx[coin]
    write_csv(port)
    return port


def write_csv(port):
    # Portfolio in dict format {symbol: {symbol, amount}} is saved to csv file

    with open("portfolio.csv", "w", newline='') as file:
        fieldnames = ["symbol", "amount"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for crypto in port:
            writer.writerow(port[crypto])


def title():
    # Create ascii of program name

    figlet = Figlet()
    title = "CryptoFolio"
    figlet.setFont(font="big")
    name =  figlet.renderText(title)
    return f'\n\n{name}'


def update(port):
    # Update and format coins in portfolio

    port_sym = (list(port.keys()))
    data = api_cmc(port_sym)
    quote = sort_cmc(data, port)
    return quote


def api_cmc(port_sym):
    # Connect to CoinMarketCap API and request current quotes

    port_str = ",".join(port_sym)
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    parameters = {"symbol": port_str}
    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": "d00168e2-fdfd-4186-8b69-5c2de5b26b12",}
    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError) as e:
        print(e)
    return data


def sort_cmc(dump, port):
    # Format API json data received from CoinMarketCap.com

    crypto = list(port.keys())
    for coin in crypto:
        name = dump["data"][coin]["name"]
        port[coin]["name"] = name
        price = dump["data"][coin]["quote"]["USD"]["price"]
        port[coin]["price"] = price
        change24 = dump["data"][coin]["quote"]["USD"]["percent_change_24h"]
        port[coin]["change24"] = change24
        change7 = dump["data"][coin]["quote"]["USD"]["percent_change_7d"]
        port[coin]["change7"] = change7
        amount = port[coin]["amount"]
        port[coin]["amount"] = amount
        value = float(price) * float(amount)
        port[coin]["value"] = float(value)
    return port


def current_gas_fee():
    # Connect to Owlracle API and request current Ethereum gas rate

    url = "https://owlracle.info/eth/gas"
    api_key = "0c775e4a69e241589043a0d40a7ec2bc"
    api_secret = "63d86c75c2334d8295d5ad97071f095c"

    r = requests.get(url)
    data = json.loads(r.text)
    try:
        standard = (data["speeds"][1])
        text_display = (f'Ethereum Standard Gas Fee: \
            ${standard["estimatedFee"]:.2f} | Gwei: {standard["gasPrice"]:.2f}')
        return text_display
    except Exception:
        return "Unable to retrieve Ethereum Gas estimate at this time.\
            Please try again later"


def display(port, total, gas):
    # Format updated portfolio values in a table for display

    crypto = list(port.keys())
    coin_display = []
    for coin in crypto:
        name = f"{port[coin]['name']}"
        price = f'${port[coin]["price"]:,.2f}'
        change24 = f'{port[coin]["change24"]:.2f}%'
        change7 = f'{port[coin]["change7"]:.2f}%'
        amount = float(port[coin]["amount"])
        value = f'${port[coin]["value"]:,.2f}'
        coin_display.append(
            {
                "Coin": name,
                "Price": price,
                "24hr Change": change24,
                "7 Day Change": change7,
                "Amount": amount,
                "Value": value,
            })

    # Display coins
    total_display = f'${total:,.2f}'
    coin_display.append({"Coin": "TOTAL PORTFOLIO", "Value": total_display})
    print(tabulate(coin_display, headers="keys", tablefmt="grid", \
        floatfmt=">10.2f", numalign="decimal"))

    # Display gas fees
    gas_display = [[gas]]
    print(tabulate(gas_display, tablefmt="grid"))
    print("\n")


def total_value(port):
    # Calculate total dollar value of all coins

    total = 0
    for coin in port:
        total = total + port[coin]["value"]
    return total


if __name__ == "__main__":
    main()
