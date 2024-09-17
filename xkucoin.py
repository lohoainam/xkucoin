import requests
import os
import time
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from requests.auth import HTTPProxyAuth
import itertools
import sys

# Hàm hiển thị banner
def show_banner():
    banner = r"""
     _    _ _____         _____   ______ _____  _____   _______ ______  
    \ \  / (_____)  /\   / ___ \ / _____) ___ \(____ \ (_______|_____ \ 
     \ \/ /   _    /  \ | |   | | /    | |   | |_   \ \ _____   _____) )
      )  (   | |  / /\ \| |   | | |    | |   | | |   | |  ___) (_____ ( 
     / /\ \ _| |_| |__| | |___| | \____| |___| | |__/ /| |_____      | |
    /_/  \_(_____)______|\_____/ \______)_____/|_____/ |_______)     |_|
                                                                       
    """
    print(banner)
    print("Dev by: Lo Hoài Nam")
    print("Contact: @Xiaocoderz")
    time.sleep(1)  # Tạm dừng 1 giây để hiển thị banner trước khi tiếp tục

# Hiệu ứng loading
def loading_animation(stop_event):
    for c in itertools.cycle(['|', '/', '-', '\\']):
        if stop_event.is_set():
            break
        sys.stdout.write('\rĐang tải ' + c)
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write('\rHoàn thành!     \n')

class KucoinAPIClient:
    def __init__(self, account_index=0, proxy=None):
        self.headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
            "Origin": "https://www.kucoin.com",
            "Referer": "https://www.kucoin.com/miniapp/tap-game?inviterUserId=376905749&rcode=QBSLTEH5",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Mobile Safari/537.36"
        }
        self.account_index = account_index
        self.proxy = proxy

    def log(self, msg, log_type="info"):
        timestamp = time.strftime('%H:%M:%S', time.localtime())
        account_prefix = f"[Tài khoản {self.account_index + 1}]"
        log_message = f"[{timestamp}] {account_prefix} {msg}"

        if log_type == "success":
            print(f"\033[92m{log_message}\033[0m")  # Green
        elif log_type == "error":
            print(f"\033[91m{log_message}\033[0m")  # Red
        else:
            print(f"\033[94m{log_message}\033[0m")  # Blue

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            time.sleep(1)

    def generate_random_points(self, total_points, num_requests):
        points = [0] * num_requests
        remaining_points = total_points

        for i in range(num_requests - 1):
            max_point = min(60, remaining_points - (num_requests - i - 1))
            points[i] = random.randint(0, max_point)
            remaining_points -= points[i]

        points[num_requests - 1] = remaining_points
        random.shuffle(points)
        return points

    def increase_gold(self, cookie, increment, molecule):
        url = "https://www.kucoin.com/_api/xkucoin/platform-telebot/game/gold/increase?lang=en_US"
        data = {'increment': increment, 'molecule': molecule}
        headers = self.headers.copy()
        headers["Cookie"] = cookie
        proxies = {"https": self.proxy} if self.proxy else None

        try:
            response = requests.post(url, data=data, headers=headers, proxies=proxies)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {"success": False, "error": f"HTTP Error: {response.status_code}"}
        except requests.RequestException as e:
            return {"success": False, "error": str(e)}

    def process_account(self, cookie):
        points = self.generate_random_points(3000, 55)
        total_points = 0
        current_molecule = 3000

        for j, increment in enumerate(points):
            current_molecule -= increment
            result = self.increase_gold(cookie, increment, current_molecule)

            if result["success"]:
                total_points += increment
                self.log(f"Cho ăn thành công, bón {result['data']['data']} sâu | Còn lại {current_molecule} sâu", "success")
            else:
                self.log(f"Lỗi khi bón sâu: {result['error']}", "error")

            self.countdown(3)

        self.log(f"Tổng số gold đã tăng: {total_points}", "success")

def load_cookies_and_proxies(cookie_file, proxy_file=None):
    with open(cookie_file, 'r') as f:
        cookies = [line.strip() for line in f if line.strip()]
    proxies = None
    if proxy_file and os.path.exists(proxy_file):
        with open(proxy_file, 'r') as f:
            proxies = [line.strip() for line in f if line.strip()]
    return cookies, proxies

def main():
    show_banner()  # Hiển thị banner trước khi tiếp tục
    
    # Khởi động hiệu ứng loading
    stop_event = threading.Event()
    loading_thread = threading.Thread(target=loading_animation, args=(stop_event,))
    loading_thread.start()
    
    # Chạy hiệu ứng loading trong 2 giây
    time.sleep(2)
    
    # Kết thúc hiệu ứng loading sau 2 giây
    stop_event.set()
    loading_thread.join()

    cookie_file = 'data.txt'
    proxy_file = 'proxy.txt'

    cookies, proxies = load_cookies_and_proxies(cookie_file, proxy_file)

    max_threads = 3
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(KucoinAPIClient(i, proxies[i % len(proxies)] if proxies else None).process_account, cookie) for i, cookie in enumerate(cookies)]
        # Chờ cho tất cả các nhiệm vụ hoàn thành
        for future in futures:
            future.result()

    print("Hoàn thành !")

if __name__ == "__main__":
    main()
