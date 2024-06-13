from supabase import create_client, Client
import credentials
import requests
import random

random_int = random.randint(1, 30)

supabase: Client = create_client(credentials.url, credentials.key)

table = supabase.table("investments")

coin = input("Input coin type: ")
currency = input("Currency: ")
url = f"https://dummyjson.com/products/{random_int}"
data = requests.get(url).json()
amount = data["price"]

add_investment_template = """
insert into investments (
coin, currency, amount
) values%s
"""

data = [
    ("ETH", "GBP", 10.31),
    ("DOG", "EUR", 12.45)]

values = ", ".join(
    f"('{item[0]}', '{item[1]}', {item[2]})" for item in data
)

sql_command = add_investment_template % values

data, count = supabase.table('investments').insert({"coin": coin, "currency": currency, "amount": amount}).execute()


responseOne = supabase.rpc("execute_raw_sql", {"sql": sql_command}).execute()
response = supabase.table('investments').select("*").execute()

print(response)
# table.save()