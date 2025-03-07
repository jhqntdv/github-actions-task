import requests
import http.client
import pandas as pd
import logging
import os
import random
import json

# from dotenv import load_dotenv
# load_dotenv()

logging.basicConfig(level=logging.INFO, filename='status.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def lottery(date):
    x = random.sample(range(1, 50), 6)
    logger.info(f"The lottery numbers for {date} are: {x[:-1]} and the bonus number is: {x[-1]}")
    return x 

def get_pools(API_KEY):
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

def get_total_rewards(API_KEY, stake_address, count=100, page=1):
    conn = http.client.HTTPSConnection("cardano-mainnet.blockfrost.io")
    headers = { 'Project_id': API_KEY }
    
    endpoint = f"/api/v0/accounts/{stake_address}/rewards?count={count}&page={page}"
    conn.request("GET", endpoint, headers=headers)
    res = conn.getresponse()
    data = res.read()
    
    if res.status == 200:
        rewards = json.loads(data.decode("utf-8"))
        total_rewards = sum(int(reward["amount"]) for reward in rewards) / 1_000_000
        logger.info(f"Successfully retrieved total rewards: {total_rewards} ADA")
        return total_rewards

    else:
        logger.error(f"Failed to retrieve rewards: {res.status} - {data.decode('utf-8')}")
        return None

if __name__ == "__main__":

    try:
        API_KEY = os.environ["API_KEY"]
    except KeyError:
        API_KEY = "secret_api_key_empty"
        logger.error("API_KEY not found in environment variables")

    today = pd.Timestamp.today().tz_localize('UTC').strftime('%Y-%m-%d')
    
    lottery(today)

    get_pools(API_KEY)

    get_total_rewards(API_KEY, "stake1uxqt2hr9nytznnyk8ku3ajemzv88mxx8ag2udmp2r83t4egzakat3", 100, 1)