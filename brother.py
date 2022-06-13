from twittic import TwitterAPI
from twittic.exceptions import NotFound
from pprint import pprint
proxyies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}
try:
    get = TwitterAPI(proxies=proxyies)
    bro = get.get_status(tweet_id="1536394282856329225")
    pprint(bro)
except NotFound as e:
    print("nigga")