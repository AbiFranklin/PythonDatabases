import sqlite3
import requests
import click
import datetime
import csv
from headers import headers
from dataclasses import dataclass

# SQL statement to create the investments table if it doesn't exist
CREATE_INVESTMENTS_SQL = """
CREATE TABLE IF NOT EXISTS investments (
    coin_id TEXT,
    currency TEXT,
    amount REAL,
    sell INT, 
    date TIMESTAMP
);
"""


@dataclass
class Investment:
    """
    A class representing an investment.

    Attributes:
        coin_id (str): The ID of the cryptocurrency.
        currency (str): The currency in which the investment is made.
        amount (float): The amount of the investment.
        sell (bool): Whether the investment is a sell transaction.
        date (datetime): The date and time of the investment.
    """
    coin_id: str
    currency: str
    amount: float
    sell: bool
    date: datetime.datetime

    def compute_value(self) -> float:
        """
        Computes the value of the investment based on the current coin price.
        """
        return self.amount * get_coin_price(self.coin_id, self.currency)


def investment_row_factory(_, row):
    """
    Row factory function to convert database rows to Investment objects.
    """
    return Investment(
        coin_id=row[0],
        currency=row[1],
        amount=row[2],
        sell=bool(row[3]),
        date=str(datetime.datetime.now())
    )


def get_coin_price(coin_id, currency):
    """
    Retrieves the current price of a cryptocurrency in the specified currency.
    """
    url = f"https://rest.coinapi.io/v1/exchangerate/{coin_id}/{currency}"
    data = requests.get(url, headers=headers).json()
    rate = data["rate"]
    return rate


@click.group()
def cli():
    """
    Click command group for CLI commands.
    """
    pass


@click.command()
@click.option("--coin_id", default="BTC")
@click.option("--currency", default="USD")
def show_coin_price(coin_id, currency):
    """
    CLI command to show the current price of a cryptocurrency.
    """
    coin_price = get_coin_price(coin_id, currency)
    print(
        f"The price of {coin_id.upper()} is ${coin_price:.2f} {currency.upper()}")


@click.command()
@click.option("--coin_id")
@click.option("--currency")
@click.option("--amount", type=float)
@click.option("--sell", is_flag=True)
def add_investment(coin_id, currency, amount, sell):
    """
    CLI command to add an investment to the database.
    """
    sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
    values = (coin_id.upper(), currency.upper(),
              amount, sell, datetime.datetime.now())
    cursor.execute(sql, values)
    database.commit()

    if sell:
        print(f"Added sell of {amount} {coin_id.upper()}")
    else:
        print(f"Added buy of {amount} {coin_id.upper()}")


@click.command()
@click.option("--coin_id")
@click.option("--currency")
def get_investment_value(coin_id, currency):
    """
    CLI command to get the total value of investments for a cryptocurrency.
    """
    coin_price = get_coin_price(coin_id, currency)
    sql = """
    SELECT * 
    FROM investments 
    WHERE coin_id=? 
    AND currency=? 
    AND sell=?
    """
    buy_results = cursor.execute(
        sql, (coin_id.upper(), currency.upper(), False)).fetchall()
    sell_results = cursor.execute(
        sql, (coin_id.upper(), currency.upper(), True)).fetchall()
    buy_amount = sum([row.amount for row in buy_results])
    sell_amount = sum([row.amount for row in sell_results])

    total = buy_amount - sell_amount

    print(
        f"You own a total of {total} {coin_id} worth {total * coin_price} {currency.upper()}")


@click.command()
@click.option("--csv_file")
def import_investments(csv_file):
    """
    CLI command to import investments from a CSV file.
    """
    with open(csv_file, "r") as f:
        rdr = csv.reader(f, delimiter=",")
        rows = list(rdr)
        sql = "INSERT INTO investments VALUES (?, ?, ?, ?, ?);"
        cursor.executemany(sql, rows)
        database.commit()

        print(f"Imported {len(rows)} investments from {csv_file}")


# Add commands to the CLI group
cli.add_command(show_coin_price)
cli.add_command(add_investment)
cli.add_command(get_investment_value)
cli.add_command(import_investments)

if __name__ == "__main__":
    # Connect to the SQLite database
    database = sqlite3.connect("portfolio.db")
    database.row_factory = investment_row_factory
    cursor = database.cursor()

    # Create the investments table if it doesn't exist
    cursor.execute(CREATE_INVESTMENTS_SQL)

    # Run the CLI
    cli()
