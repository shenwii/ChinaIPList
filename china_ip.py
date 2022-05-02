#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import re
import sys
import json
import time
import requests
import urllib.parse

class HttpClient():
    def __init__(self, proxy = None):
        self.__session__ = requests.Session()
        self.__user_agent__ = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36"
        self.__proxies = {}
        if proxy is not None and proxy != "":
            self.__proxies["http"] = proxy
            self.__proxies["https"] = proxy

    def get(self, url, headers = {}, **params):
        headers["User-Agent"] = self.__user_agent__
        url = url.rstrip("/")
        if len(params) != 0:
            if url[-1] != "?":
                url = url + "?"
            for k in params.keys():
                url = url + ("%s=%s&" % (k, urllib.parse.quote_plus(str(params[k]))))
            url = url[0:-1]
        return self.__session__.get(url, headers = headers, timeout = 30, proxies = self.__proxies)

    def get_json(self, url, headers = {}, params = {}, encode = "utf-8"):
        response = self.__get(url, headers, params)
        return json.loads(response.content.decode("utf-8"))

class IpCache():
    def __init__(self, cache_file):
        self.__cache_file = cache_file
        self.__cache = self.__load()

    def __load(self):
        if not os.path.exists(self.__cache_file):
            return {}
        try:
            with open(self.__cache_file, "r", encoding = "UTF-8") as f:
                return json.load(f)
        except:
            return {}

    def save(self):
        with open(self.__cache_file, "w", encoding = "UTF-8") as f:
            json.dump(self.__cache, f, indent = 4, ensure_ascii = False)

    def get(self, _key):
        if _key in self.__cache:
            return self.__cache[_key]
        return None

    def set(self, _key, _value):
        self.__cache[_key] = _value

def handle(cache_file, source_url, target_file):
    http_client = HttpClient()
    ip_cache = IpCache(cache_file)
    asn_re = re.compile("var ip_result = (\{[^;]+\});")
    headers = {
        "Host": "ip138.com",
        "Referer": "https://ip138.com/"
        }
    ip_list = []
    china_list = ["上海市", "中国 ", "云南省", "内蒙古自治区", "北京市", "吉林省", "四川省", "天津市", "宁夏回族自治区", "安徽省", "山东省", "山西省", "广东省", "广西壮族自治区", "新疆维吾尔自治区", "江苏省", "江西省", "河北省", "河南省", "浙江省", "海南省", "湖北省", "湖南省", "甘肃省", "福建省", "西藏自治区", "贵州省", "辽宁省", "重庆市", "陕西省", "青海省", "黑龙江省"]
    for cidr in http_client.get(source_url).content.decode("utf-8").split("\n"):
        cidr = cidr.strip()
        if len(cidr) == 0:
            continue
        if cidr[0] == "#":
            continue
        cidr_split = cidr.split("/")
        if len(cidr_split) != 2:
            continue
        check_ip = cidr_split[0]
        check_ip = check_ip[0:len(check_ip) - 1] + "1"
        asn_data = ip_cache.get(check_ip)
        if asn_data is None:
            print("miss cache")
            try:
                html_content = http_client.get("https://ip138.com/iplookup.asp", headers = headers, ip = check_ip, action = 2).content.decode("GB18030")
            except:
                ip_cache.save()
                return
            asn_match = asn_re.findall(html_content)
            if len(asn_match) == 1:
                asn_data = json.loads(asn_match[0])
                ip_cache.set(check_ip, asn_data)
            else:
                print("error")
                print(html_content)
        is_pass = False
        for key in china_list:
            if asn_data["ASN归属地"].count(key) > 0:
                is_pass = True
                break
        if is_pass:
            ip_list.append(cidr)
            print(cidr)
    ip_cache.save()
    with open(target_file, 'w', encoding = "UTF-8") as f:
        for ip in ip_list:
            f.write(f"{ip}\n")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("parma error")
        exit(1)
    cache_file = sys.argv[1]
    source_url = sys.argv[2]
    target_file = sys.argv[3]
    handle(cache_file, source_url, target_file)
