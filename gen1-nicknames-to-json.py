#!/usr/bin/env python

import sys
import json
import datetime
import re

nicknames = 'nicknames.txt'
with open(nicknames, 'r') as tfile:
    gen1 = tfile.readlines()

valid_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H:%M:%S")

devices = {}
for line in gen1[1:]:
    bits = line.strip().split()
    #print(bits)
    mbid = bits[0].lower()
    prodid = bits[1].upper()
    name = bits[2]
    strpos = bits[3].upper()
    if mbid in devices:
        print(f'ERROR: {mbid} already exists')
        #print(f'  NEW: {mbid} {prodid} {name} {strpos}')
        #print(f'  OLD: {devices[mbid]['mbid']} {devices[mbid]['prod_id']} '
        #      f'{devices[mbid]['name']} {devices[mbid]['str-pos']}')
        #print()
        continue
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
    mbid = bits[3].lower()
    prodid = bits[4].upper()
    if mbid not in devices:
        print(f' WARN: {mbid} adding dead dom to nicknames')
    devices[mbid] = {
        'device_type': 'gen1_dom',
        'mbid': mbid,
        'prod_id': prodid,
        'name': name,
        'str-pos': strpos,
        'dead': True
    }


comments = []
comments.append(f'{len(devices)} gen1_dom devices')
print(f'{len(devices)} Gen1 devices')

names_file = {
    'timestamp': valid_date,
    'comments': comments,
    'devices': devices
}

# write json file of gen1 nicknames
with open('gen1-nicknames_'+valid_date+'.json', 'w') as jfile:
    json.dump(names_file, jfile, separators=(', ', ': '), indent=4)
with open('gen1-nicknames.json', 'w') as jfile:
    json.dump(devices, jfile, separators=(', ', ': '), indent=4)

# write sorted txt file of gen1 nicknames
names = {}
domids = {}
locas = {}
for dom in devices:
    name = devices[dom]['name']
    domid = devices[dom]['prod_id']
    loca = devices[dom]['str-pos']
    if not re.match("[0-9][0-9]-[0-9][0-9]", loca):
        if loca+name in locas:
            print(f'ERROR: {loca+name} already exists')
        locas[loca+name] = devices[dom]
    elif not re.match("[A-Z][A-Z][0-9][A-Z][0-9][0-9][0-9][0-9]", domid):
        if domid+name in domids:
            print(f'ERROR: {domid+name} already exists')
        domids[domid+name] = devices[dom]
    else:
        if name in names:
            print(f'ERROR: {name} already exists')
        names[name] = devices[dom]

#for dom in sorted(domids.keys()):
#    print(domids[dom])
#for dom in sorted(locas.keys()):
#    print(locas[dom])
#for dom in sorted(names.keys()):
#    print(names[dom])

print(len(locas)+len(domids)+len(names), 'Gen1 devices')

with open('nicknames.pretty.txt', 'w') as of:
    of.write('{0}{1}{2}{3}\n'.format('mbid'.ljust(16), 'domid'.ljust(12),
                                   'name'.ljust(30), 'location'))
    for domdict in [locas, domids, names]:
        for dom in sorted(domdict.keys()):
            of.write(f'{domdict[dom]['mbid'].ljust(16)}{domdict[dom]['prod_id'].ljust(12)}'
                     f'{domdict[dom]['name'].ljust(33)}{domdict[dom]['str-pos']}\n')
    
with open('nicknames.txt.new', 'w') as of:
    of.write('{0}\t{1}\t{2}\t{3}\n'.format('mbid', 'domid', 'name', 'location'))
    for domdict in [locas, domids, names]:
        for dom in sorted(domdict.keys()):
            of.write(f'{domdict[dom]['mbid']}\t{domdict[dom]['prod_id']}\t'
                     f'{domdict[dom]['name']}\t{domdict[dom]['str-pos']}\n')
    
    
