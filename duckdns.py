import requests, os, socket
from dotenv import load_dotenv
load_dotenv()

domain = os.getenv('DUCKDNS_DOMAIN')
token = os.getenv('DUCKDNS_TOKEN')
ip_file = 'last_ipv6.txt'

def get_ipv6():
    s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
    try:
        s.connect(("2001:4860:4860::8888", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def read_last_ip():
    if os.path.exists(ip_file):
        with open(ip_file, 'r') as file:
            return file.read().strip()
    return None

def store_ip(ip):
    with open(ip_file, 'w') as file:
        file.write(ip)

ip_address = get_ipv6()
last_ip = read_last_ip()

if ip_address != last_ip:
    if ip_address:
        url = f"https://www.duckdns.org/update?domains={domain}&token={token}&ipv6={ip_address}"
    else:
        url = f"https://duckdns.org/update/{domain}/{token}"

    try:
        print("Current IP Addr:", ip_address)
        response = requests.get(url)
        print("Status Code:", response.status_code)
        print("Response Text:", response.text)
        if response.status_code == 200:
            store_ip(ip_address)
    except requests.exceptions.RequestException as e:
        print("Error:", e)
else:
    print("No IP change detected. Skipping the request.")