import requests, os, socket
from dotenv import load_dotenv
load_dotenv()


# Replace these with your actual values
domain = os.getenv('DUCKDNS_DOMAIN')
token = os.getenv('DUCKDNS_TOKEN')

def get_ipv6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(("2001:4860:4860::8888", 80))
        return s.getsockname()[0]
    finally:
        s.close()

ip_address = get_ipv6()

if ip_address:
    url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ipv6={ip_address}"
else:
    url = f"https://duckdns.org/update/{domain}/{token}"

try:
    print("Ip Addr: ", ip_address)
    response = requests.get(url)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)
except requests.exceptions.RequestException as e:
    print("Error:", e)