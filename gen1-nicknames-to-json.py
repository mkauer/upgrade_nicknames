#!/usr/bin/env python

import sys
import json
import datetime
import argparse

cmdparser = argparse.ArgumentParser()
cmdparser.add_argument(dest='devices', help='give a devices file')
args = cmdparser.parse_args()

nicknames = args.devices
with open(nicknames, 'r') as tfile:
    gen1 = tfile.readlines()

valid_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
devices = {}
for line in gen1[1:]:
    bits = line.strip().split()
    mbid = bits[0]
    prodid = bits[1]
    name = bits[2]
    strpos = bits[3]
    if mbid in devices:
        print(f'ERROR: [{mbid}] already exists')
    devices[mbid] = {
        'device_type': 'gen1_dom',
        'mbid': mbid,
        'prod_id': prodid,
        'name': name,
        'str-pos': strpos,
    }

comments = []
comments.append(f'{len(devices)} gen1_dom devices')
print(f'{len(devices)} Gen1 devices')

names = {
    'timestamp': valid_date,
    'comments': comments,
    'devices': devices
}

with open('gen1-nicknames.json', 'w') as jfile:
    json.dump(names, jfile, separators=(', ', ': '), indent=4)
    
