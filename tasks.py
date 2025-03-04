import requests
import http.client
import pandas as pd
import logging
import os
import random

# from dotenv import load_dotenv
# load_dotenv()

logging.basicConfig(level=logging.INFO, filename='status.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def lottery(date):
    # pick 5+1 numbers between 1 and 49
    x = random.sample(range(1, 50), 6)
    logger.info(f"The lottery numbers for {date} are: {x[:-1]} and the bonus number is: {x[-1]}")
    return x 

def get_pools():
    conn = http.client.HTTPSConnection("cardano-mainnet.blockfrost.io")
    headers = { 'Project_id': API_KEY }
    
    conn.request("GET", "/api/v0/pools", headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status == 200:
        pools = data.decode("utf-8")
        logger.info(f"Successfully retrieved pools: {pools}")
        return pools
    else:
        logger.error(f"Failed to retrieve pools: {res.status} - {data.decode('utf-8')}")
        return None

if __name__ == "__main__":

    try:
        API_KEY = os.environ["API_KEY"]
    except KeyError:
        API_KEY = "secret_api_key_empty"
        logger.error("API_KEY not found in environment variables")

    today = pd.Timestamp.today().tz_localize('UTC').strftime('%Y-%m-%d')
    
    lottery(today)

    get_pools()