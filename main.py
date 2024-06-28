import httpx
import random
from faker import Faker
import asyncio
from colorama import init, Fore, Back, Style
import json
import sys
import time
init()

colors = [Fore.LIGHTWHITE_EX, Fore.WHITE]

fake = Faker()

def generate_random_name():
    return fake.name()

def generate_random_email():

    emails = ["gmail.com", "icloud.com"]

    email = random.choice(emails)

    period = ["", "."]

    email_prefix = fake.user_name() + random.choice(period) + str(random.randint(1000, 9999))

    return f"{email_prefix}@{email}"

def convert_null_to_none(z):
    if isinstance(z, dict):
        return {key: convert_null_to_none(value) for key, value in z.items()}
    elif isinstance(z, list):
        return [convert_null_to_none(item) for item in z]
    elif z == "null":
        return None
    else:
        return z
asf = convert_null_to_none(json.loads(input("payload: ")))['votes']

async def req(client, url, headers, pl, request_count, name, email): 

    retries = 3

    for attempt in range(retries):
        try:
            resp = await client.post(url, headers=headers, json=pl, timeout=10.0)
            print(f"[{Fore.RED}{resp.status_code}{Fore.RESET}][{random.choice(colors)}+1{Fore.RESET}] -- {Fore.WHITE}{name}")
            with open('req_sent.txt', 'a') as txt:
                txt.write(name + ':' + email + '\n')
                #   [Total Requests: {request_count}]")
            return resp.json()
        except httpx.RequestError as exc:
            print(f"request error: {exc} on attempt {attempt + 1}")
        except httpx.HTTPStatusError as exc:
            print(f"http error: {exc} on attempt {attempt + 1}")
        except httpx.ConnectTimeout:
            print(f"timeout error on attempt {attempt + 1}")

    return None


def payload_():
    name = generate_random_name()
    email = generate_random_email()
    payload = {
        "name": name,
        "email": email,
        "marketing": "n",
        "thirdparty": "n",
        "votes": asf
        # "votes": [None] * 382 + [11]
    }

    return payload

async def main(num_requests):
    url = "https://esportsawards.com/wp-json/vote/v1/vote/"
    headers = {
        "Cookie": "sizzle_gdpr_has_displayed=true; sizzle_gdpr_analytical=optin; sizzle_gdpr_functional=optin; _gid=GA1.2.2048305606.1719545573; ppwp_wp_session=4c65b20e6f4eb1a5beaca93ebf149e8e%7C%7C1719547389%7C%7C1719547029; _fbp=fb.1.1719545593579.80433553612110115; _gat_UA-96165527-1=1; _ga=GA1.2.1091666244.1719545573; AWSALB=cv2eh282lCuXCBNyckchtgGAqTCFTpyUcKl9IXXX9HECXr/V3vx4JrLgRhgflJlBYMT8mrBTHr2JJobVKslatJY5PZhDQ2G+4sJw4rGBH0bqgNPELJ1G9/OnJemZ; _ga_Q92XFFV6GS=GS1.1.1719545593.1.1.1719546626.31.0.0",
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "Accept-Language": "en-US",
        "Sec-Ch-Ua-Mobile": "?0",
        "Authorization": "Basic YWRtaW46ZHJpenpsZTE=",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.57 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://esportsawards.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://esportsawards.com/vote/details",
        "Accept-Encoding": "gzip, deflate, br",
        "Priority": "u=1, i"
    }

    async with httpx.AsyncClient() as client:
        request_count = 1
        if num_requests == float('inf'):
            while True:
                tasks = []
                for _ in range(100): 
                    payload = payload_()
                    tasks.append(req(client, url, headers, payload, request_count, payload['name'], payload['email']))
                    request_count += 1
                await asyncio.gather(*tasks)
        else:
            for _ in range(num_requests):
                payload = payload_()
                await req(client, url, headers, payload, request_count, payload['name'], payload['email'])
                request_count += 1

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

if __name__ == "__main__":
    num_requests = input("Number of requests in each batch (or 'infinite' to run indefinitely): ")
    
    if num_requests.lower() == 'infinite':
        num_requests = float('inf')
    elif is_int(num_requests):
        num_requests = int(num_requests)
    else:
        print('invalid input, defaulting to infinite) # not a number or "infinite", defaults to infinite')
        time.sleep(1)
        num_requests = float('inf')
        # sys.exit()
    
    asyncio.run(main(num_requests))
