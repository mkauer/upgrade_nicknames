#!/usr/bin/env python

import sys
import json
import datetime

nicknames = 'nicknames.txt'
with open(nicknames, 'r') as tfile:
    gen1 = tfile.readlines()

valid_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H:%M:%S")
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
        'dead': False
    }

deaddoms = 'dead-doms.txt'
with open(deaddoms, 'r') as tfile:
    dead = tfile.readlines()
for line in dead:
    bits = line.strip().split()
    name = bits[0]
    S = bits[1].zfill(2)
    P = bits[2].zfill(2)
    strpos = S+'-'+P
    mbid = bits[3]
    prod_id = bits[4]
    #if mbid not in devices:
    #    print(mbid, strpos, 'not in nicknames')
    devices[mbid] = {
        'device_type': 'gen1_dom',
        'mbid': mbid,
        'prod_id': prodid,
        'name': name,
        'str-pos': strpos,
        'dead': True
    }
    #else:
    #    print(f'{mbid} already in list')
    #    print(devices[mbid])


comments = []
comments.append(f'{len(devices)} gen1_dom devices')
print(f'{len(devices)} Gen1 devices')

names = {
    'timestamp': valid_date,
    'comments': comments,
    'devices': devices
}

with open('gen1-nicknames_'+valid_date+'.json', 'w') as jfile:
    json.dump(names, jfile, separators=(', ', ': '), indent=4)

