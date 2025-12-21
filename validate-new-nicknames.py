#!/usr/bin/env python

import sys
import json
import argparse

cmdparser = argparse.ArgumentParser()
cmdparser.add_argument(dest='devices', help='give a devices file')
args = cmdparser.parse_args()
    
#newnames = 'upgrade_devices.json'
newnames = args.devices
with open(newnames, 'r') as jfile:
    upgrade = json.load(jfile)

nicknames = 'gen1-nicknames.txt'
with open(nicknames, 'r') as tfile:
    gen1 = tfile.readlines()


allnames = []
for name in gen1:
    name = name.strip()
    if name not in allnames:
        allnames.append(name)
    else:
        print(f'found again : {name}')

for key in upgrade['devices']:
    if "name" in key:
        name = key['name'].strip()
        if name not in allnames:
            allnames.append(name)
        else:
            for key2 in upgrade['devices']:
                if "name" in key2:
                    if name == key2['name'].strip():
                        pid2 = key2['prod_id'].strip()
                        break
            pid = key['prod_id'].strip()
            print(f'found \"{name}\" in [{pid2}] and [{pid}]')

