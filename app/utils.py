from urllib.parse import unquote
from urllib import request
import json

def name_finder(item_link: str) -> str:
    item_name = item_link[47:]
    return unquote(item_name)

def price_finder(item_link: str) -> int:
    # Implement logic to retrieve and return the item's price
    try:
        market_hash_name = item_link[47:]
        target_url = "https://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name=" \
                    + market_hash_name
        url_request = request.urlopen(target_url)
        data = json.loads(url_request.read().decode())
        item_price = str(data.get('lowest_price'))
        item_price = float(item_price.replace('$', ''))
    except:
        item_price = 0

    return item_price



