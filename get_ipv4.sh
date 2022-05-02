#!/bin/sh

cd "$(dirname "$0")"
./china_ip.py cache4.json 'https://ispip.clang.cn/all_cn.txt' "cn_ipv4.txt"
