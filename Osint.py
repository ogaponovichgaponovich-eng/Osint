#!/usr/bin/env python3
import requests
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import sys
import csv
import os
import time
import re
import platform
import subprocess
from datetime import datetime
from pathlib import Path
try:
    from PIL import ImageGrab
except:
    os.system("pip3 install pillow")
    from PIL import ImageGrab
try:
    import cv2
except:
    os.system("pip3 install opencv-python")
    import cv2

class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    RESET = '\033[0m'

banner = r"""
  ____  _____ _____ _   _ _____ _   _ 
 / __ \|  __ \_   _| \ | |_   _| \ | |
| |  | | |__) || | |  \| | | | |  \| |
| |  | |  ___/ | | | . ` | | | | . ` |
| |__| | |    _| |_| |\  |_| |_| |\  |
 \____/|_|   |_____|_| \_|_____|_| \_|
            OSINT + Ratnik
"""
print(Colors.CYAN + banner + Colors.RESET)

def menu():
    print(Colors.YELLOW + "\nВиберіть функцію:" + Colors.RESET)
    print("1. Пошук по номеру телефону")
    print("2. Пошук по нікнейму")
    print("3. Пошук по email")
    print("4. Перевірка домену")
    print("5. Перевірка IP")
    print("6. Ratnik (локальні функції)")
    print("0. Вийти")
    choice = input(Colors.GREEN + "Введіть номер функції: " + Colors.RESET)
    return choice

def phone_lookup():
    number = input(Colors.GREEN + "\nВведіть номер телефону (з кодом країни, напр. +380...): " + Colors.RESET)
    try:
        phone = phonenumbers.parse(number)
        country = geocoder.description_for_number(phone, "uk")
        city_timezones = timezone.time_zones_for_number(phone)
        oper = carrier.name_for_number(phone, "uk")
        print(Colors.MAGENTA + f"\n[Інформація про номер]" + Colors.RESET)
        print(f"Країна: {country}")
        print(f"Часові пояси: {', '.join(city_timezones)}")
        print(f"Оператор: {oper}")
        sites = [f"https://www.truecaller.com/search/{number}",
                 f"https://www.whitepages.com/phone/{number}",
                 f"https://www.sync.me/search/?q={number}",
                 f"https://www.numverify.com/number/{number}",
                 f"https://www.whocalledme.com/Phone/{number}"]
        for site in sites:
            time.sleep(0.3)
            print(f"Перевірка сайту: {site}")
        Path("results").mkdir(exist_ok=True)
        with open("results/phone_results.txt", "a") as f:
            f.write(f"{number},{country},{','.join(city_timezones)},{oper}\n")
        with open("results/phone_results.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([number, country, ",".join(city_timezones), oper])
    except Exception as e:
        print(Colors.RED + f"Помилка: {e}" + Colors.RESET)

def nickname_lookup():
    nickname = input(Colors.GREEN + "\nВведіть нікнейм: " + Colors.RESET)
    sites = {"GitHub": f"https://github.com/{nickname}",
             "Twitter": f"https://twitter.com/{nickname}",
             "Instagram": f"https://www.instagram.com/{nickname}",
             "TikTok": f"https://www.tiktok.com/@{nickname}",
             "Telegram": f"https://t.me/{nickname}",
             "Reddit": f"https://www.reddit.com/user/{nickname}",
             "YouTube": f"https://www.youtube.com/{nickname}",
             "Pinterest": f"https://www.pinterest.com/{nickname}/",
             "Facebook": f"https://www.facebook.com/{nickname}",
             "Steam": f"https://steamcommunity.com/id/{nickname}/",
             "Medium": f"https://medium.com/@{nickname}",
             "DevTo": f"https://dev.to/{nickname}",
             "HackerNews": f"https://news.ycombinator.com/user?id={nickname}",
             "Flickr": f"https://www.flickr.com/people/{nickname}/",
             "Vimeo": f"https://vimeo.com/{nickname}"}
    print(Colors.MAGENTA + f"\n[Перевірка нікнейму: {nickname}]" + Colors.RESET)
    for site, url in sites.items():
        try:
            resp = requests.get(url)
            time.sleep(0.2)
            if resp.status_code == 200:
                print(Colors.GREEN + f"[+] {site}: Знайдено -> {url}" + Colors.RESET)
            else:
                print(Colors.RED + f"[-] {site}: Не знайдено" + Colors.RESET)
        except:
            print(Colors.YELLOW + f"[!] {site}: Помилка при перевірці" + Colors.RESET)
    Path("results").mkdir(exist_ok=True)
    with open("results/nickname_results.txt", "a") as f:
        f.write(f"{nickname}\n")
    with open("results/nickname_results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([nickname])

def email_lookup():
    email = input(Colors.GREEN + "\nВведіть email: " + Colors.RESET)
    print(Colors.MAGENTA + f"\n[Перевірка email: {email}]" + Colors.RESET)
    try:
        resp = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}", headers={"User-Agent": "OSINT-Tool"})
        time.sleep(0.3)
        if resp.status_code == 200:
            print(Colors.RED + f"[!] Email знайдено у зламаних базах!" + Colors.RESET)
        elif resp.status_code == 404:
            print(Colors.GREEN + "[+] Інформація про email не знайдена" + Colors.RESET)
        else:
            print(Colors.YELLOW + f"[!] Помилка: {resp.status_code}" + Colors.RESET)
    except:
        print(Colors.YELLOW + "[!] Неможливо перевірити email" + Colors.RESET)
    Path("results").mkdir(exist_ok=True)
    with open("results/email_results.txt", "a") as f:
        f.write(f"{email}\n")
    with open("results/email_results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([email])

def domain_lookup():
    domain = input(Colors.GREEN + "\nВведіть домен (наприклад example.com): " + Colors.RESET)
    print(Colors.MAGENTA + f"\n[Перевірка домену: {domain}]" + Colors.RESET)
    try:
        resp = requests.get(f"https://api.domainsdb.info/v1/domains/search?domain={domain}")
        time.sleep(0.3)
        if resp.status_code == 200:
            data = resp.json()
            for d in data.get("domains", []):
                print(f"Domain: {d.get('domain')}, Create Date: {d.get('create_date')}, Update Date: {d.get('update_date')}")
        else:
            print(Colors.YELLOW + f"Помилка при перевірці домену: {resp.status_code}" + Colors.RESET)
    except:
        print(Colors.YELLOW + "Неможливо перевірити домен" + Colors.RESET)
    Path("results").mkdir(exist_ok=True)
    with open("results/domain_results.txt", "a") as f:
        f.write(f"{domain}\n")
    with open("results/domain_results.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([domain])

def ip_lookup():
    ip = input(Colors.GREEN + "\nВведіть IP адресу: " + Colors.RESET)
    print(Colors.MAGENTA + f"\n[Перевірка IP: {ip}]" + Colors.RESET)
    try:
        resp = requests.get(f"http://ip-api.com/json/{ip}")
        time.sleep(0.3)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Країна: {data.get('country')}")
            print(f"Місто: {data.get('city')}")
            print(f"Region: {data.get('regionName')}, ZIP: {data.get('zip')}")
            print(f"ISP: {data.get('isp')}, Org: {data.get('org')}")
        else:
            print(Colors.YELLOW + f"Помилка при перевірці IP: {resp.status_code}" + Colors.RESET)
    except:
        print(Colors.YELLOW + "Неможливо перевірити IP" + Colors.RESET)
    Path("results").mkdir(exist_ok=True)
    with open("results/ip_results.txt", "a") as f:
        f.write(f"{ip}\n")
    with open("results/ip_results.csv", "
