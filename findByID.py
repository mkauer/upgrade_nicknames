#!/usr/bin/env python

import sys
import os
import json
import argparse
from pprint import pprint

PATH = '/home/mkauer/GITHUB/upgrade_nicknames'

cmdparser = argparse.ArgumentParser()
cmdparser.add_argument(dest='ID', help='give a device ID')
args = cmdparser.parse_args()
ID = args.ID

newnames = os.path.join(PATH, 'upgrade_devices.json')
with open(newnames, 'r') as jfile:
    upgrade = json.load(jfile)

nicknames = os.path.join(PATH, 'gen1-nicknames.json')
with open(nicknames, 'r') as jfile:
    gen1 = json.load(jfile)

if ID in gen1['devices']:
    pprint(gen1['devices'][ID])
elif 'devices' in upgrade:
    if ID in upgrade['devices']:
        pprint(upgrade['devices'][ID])
    elif ID in upgrade:
        pprint(upgrade[ID])
else:
    print('ID not found')

