import argparse
import webbrowser
from requests import Session
import bs4
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
from pyfiglet import Figlet
import csv
from tabulate import tabulate
from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()


def main():

    if new_user():
        portfolio = new_port()
    else:
        portfolio = load_port()

    if command() == "buy":
        portfolio = add_buy(portfolio)
    elif command() == "sell":
        portfolio = add_sell(portfolio)

    print(title())
    portfolio = update(portfolio)
    display(portfolio)

    if command() == "news":
        print(latest_news())


def update(port):
    port_sym = (list(port.keys()))
    data = api_cmc(port_sym)
    quote = sort_cmc(data, port)
    return(quote)


def command():
    parser = argparse.ArgumentParser(description="Track your crypto portfolio and industry news")
    parser.add_argument("-b", help="Enter a Buy transaction", action="store_true")
    parser.add_argument("-s", help="Enter a Sell transaction", action="store_true")
    parser.add_argument("-n", help="Check the news", action= "store_true")
    args = parser.parse_args()              

    if args.b:
        return "buy"
    elif args.s:
        return "sell"
    elif args.n:
        return "news"


def new_user():
    """ Checks for a saved portfolio.csv file """
    try:
        with open("portfolio.csv", "r", newline='') as file:
            reader = csv.DictReader(file)
    except FileNotFoundError:
        return True


def load_port():
    """ reads saved portfolio.csv or sets up new one and creates dict object"""

    port = {}
    try:
        with open("portfolio.csv", "r", newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                port[row["symbol"]] = {"symbol": row["symbol"], "amount": float(row["amount"])}
    except FileNotFoundError:
        print("Welcome to CryptoFolio! Let's set up a new portfolio for you")
    return port


def new_port():
    """ Creates new portfolio as a dict of dicts from user input """

    print("Welcome to CryptoFolio! Let's set up your portfolio")
    port = enter_coins()
    write_csv(port)
    return port


def enter_coins():

    listings = ['BTC', 'ETH', 'USDT', 'USDC', 'BNB', 'BUSD', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DAI', 'DOT', 'TRX', 'SHIB', 'LEO', 'AVAX', 'WBTC', 'MATIC', 'UNI', 'LTC', 'FTT', 'BNB', 'LINK', 'CRO', 'XLM', 'NEAR', 'ATOM', 'XMR', 'ALGO', 'ETC', 'BCH', 'ICP', 'VET', 'FLOW', 'MANA', 'XTZ', 'SAND', 'APE', 'HBAR', 'FIL', 'TUSD', 'BNB', 'THETA', 'EGLD', 'AXS', '{symbol: HNT', 'QNT', 'AAVE', 'BSV', 'USDP', 'EOS', 'KCS', 'MKR', 'ZEC', 'BTT', 'TRX', 'USDN', 'MIOTA', 'XEC', 'OKB', 'USDD', 'RUNE', 'BNB', 'HT', 'GRT', 'CHZ', 'KLAY', 'FTM', 'NEO', 'PAXG', 'BAT', 'LRC', 'WAVES', 'GMT', 'BNB', 'STX', 'ZIL', 'CRV', 'USTC', 'DASH', 'ENJ', 'FEI', 'CAKE', 'BNB', 'KSM', 'AR', 'MINA', 'KAVA', 'CELO', 'AMP', 'COMP', 'NEXO', 'CVX', 'XEM', 'GALA', 'HOT', '1INCH', 'XDC', 'DCR', 'GT', 'GNO', 'XYM', 'QTUM', 'KDA', 'SNX', 'IOTX'] 

    print("\nEnter each cryptocurrency (symbol) in your portfolio\nfollowed by their amounts. Press Enter when done.\n") 
    
    port_input = {}
    while True:
        symbol = input("Crypto symbol: ").upper()
        if symbol == "":
            break
        elif symbol in listings:
            pass
        else:
            print("Invalid listing")
            continue

        amount = float(input(f"{symbol} amount: "))
        if amount == "":
            break
        elif amount > 0:
            pass
        port_input[symbol] = {"symbol": symbol, "amount": amount}
    return port_input


def add_buy(port):
    """ Adds a buy transaction """

    print("\nLet's add a Buy transaction")
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
    """ Adds a sell transaction """

    print("\nLet's add a Sell transaction")
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
    """ takes in {symbol: {symbol, value}} and saves to csv file"""

    with open("portfolio.csv", "w", newline='') as file:
        fieldnames = ["symbol", "amount"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for crypto in port:
            writer.writerow(port[crypto])


def title():
    figlet = Figlet()
    title = "CryptoFolio"
    figlet.setFont(font="big")
    name =  figlet.renderText(title)
    return f'\n{name}'


def latest_news():
    url = "https://cryptopanic.com/api/v1/posts/"
    auth_token = "2589302fe33d4a0169b908f7c911a7d0166e75cf" 
    headers = {"auth_token": auth_token, "kind": "news"} 

    response = requests.get(url, headers)
    try:
        response.raise_for_status()
    except Exception as exc:
        print("There was a problem: %s" % (exc))
    data = response.json()
    headlines = data["results"]
    
    newsfeed = ""
    top = 0
    while top < 5:
        h = headlines[top]
        newsfeed = newsfeed + '\n' + (f'{h["title"]}\n') + f'{h["url"]}' + '\n'
        top += 1
    return newsfeed


def api_coin_gecko():
    url = "https://api.blocknative.com/gasprices/blockprices"
    api_key = "3c93fef6-db22-41a5-bca6-4f68897c84b9"
    headers = {"Authorization": "3c93fef6-db22-41a5-bca6-4f68897c84b9"}

    response = requests.get(url, headers=headers)
    j = response.json()
    j = str(j)
    with open("response_json.txt", "w") as file:
        file.write(j)


def api_blocknative():
    url = "https://api.blocknative.com/gasprices/blockprices"
    api_key = "3c93fef6-db22-41a5-bca6-4f68897c84b9"
    headers = {"Authorization": "3c93fef6-db22-41a5-bca6-4f68897c84b9"}

    response = requests.get(url, headers=headers)
    j = response.json()
    j = str(j)
    with open("response_json.txt", "w") as file:
        file.write(j)


def api_cmc(port_sym):
    """Connects to CoinMarketCap API and requests current quotes"""

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
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    # print(json.dumps(data, sort_keys=True, indent=4))
    return data


def sort_cmc(dump, port):
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
    

def api_eth_gas():

    url = "https://owlracle.info/eth/gas"
    api_key = "0c775e4a69e241589043a0d40a7ec2bc"
    api_secret = "63d86c75c2334d8295d5ad97071f095c"

    r = requests.get(url)
    data = json.loads(r.text)
    standard = (data["speeds"][1])
    print(f'Ethereum Standard Gas Fee: ${standard["estimatedFee"]:.2f} | Gwei: {standard["gasPrice"]:.2f}')


def display(port):
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
    print(tabulate(coin_display, headers="keys", tablefmt="grid", numalign="decimal"))


if __name__ == "__main__":
    main()