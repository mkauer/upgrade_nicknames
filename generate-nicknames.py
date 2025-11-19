#!/usr/bin/env python

import sys
import argparse
import json
from datetime import datetime

from fatcat_db.forwarder import Tunnel
from fatcat_db.mongoreader import MongoReader


valid_date = '2025-11-18'

def main():

    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument('-nt','--no-tunnel', dest='tunnel', action='store_false',
                           help='Do not port forward mongodb server')
    args = cmdparser.parse_args()

    # open ssh tunnel to mongo port
    if args.tunnel: tunnel = Tunnel()

    # connect to mongo
    mongo = MongoReader(database='production_calibration',
                        user='icecube', pswd='skua')
    if not mongo.isConnected:
        print('no connection')
        return
    
    # files I create (device-lookup.py for example)
    fats = []
    prodids = []
    pdates = []
    mbids = []
    icmids = []
    gotpopped = []
    for dt in ['NEW', 'lom16', 'lom18', 'pocam', 'mdom', 'degg']:
        with open('ids_'+dt+'.json', 'r') as jfile:
            fat = json.load(jfile)
            for item in fat:
                
                if 'fatcat_uid' in item:
                    prodid = item['fatcat_uid']
                else:
                    prodid = item['prod_id']
                prodids.append(prodid)
                #print(prodid)
                
                if 'prod_date' in item:
                    pdate = item['prod_date']
                else:
                    pdate = '2001-01-01'
                pdates.append(pdate)
                
                lj = 18
                popi = None
                if item['mbid'] in mbids:
                    i = mbids.index(item['mbid'])
                    print(f"WARNING: duplicate MBID:")
                    print(f"    {prodids[i].ljust(lj)} {pdates[i]} - MBID: {mbids[i]} ICMID: {icmids[i]}")
                    print(f"    {prodid.ljust(lj)} {pdate} - MBID: {item['mbid']} ICMID: {item['icmid']}")
                    if pdate > pdates[i]:
                        popi = i
                    else:
                        popi = -1
                    print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                mbids.append(item['mbid'])
                
                if item['icmid'] in icmids:
                    i = icmids.index(item['icmid'])
                    print(f"WARNING: duplicate ICMID:")
                    print(f"    {prodids[i].ljust(lj)} {pdates[i]} - MBID: {mbids[i]} ICMID: {icmids[i]}")
                    print(f"    {prodid.ljust(lj)} {pdate} - MBID: {item['mbid']} ICMID: {item['icmid']}")
                    if pdate > pdates[i]:
                        popi = i
                    else:
                        popi = -1
                    print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                icmids.append(item['icmid'])
                
                fats.append(item)
                
                # keep track of oddballs
                # DEgg2021-3-045_v1 and DEgg2021-3-077_v1
                # are the only ones I've found so far
                if item['mbid'] == "":
                    print(f"WARNING: no MBID:")
                    popi = -1
                    print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                
                if popi is not None:
                    gotpopped.append(fats[popi])
                    fats.pop(popi)
                    prodids.pop(popi)
                    pdates.pop(popi)
                    mbids.pop(popi)
                    icmids.pop(popi)
                    print()
                    
    """
    print(' THESE WERE REMOVED')
    print('==================================')
    for device in gotpopped:
        print(device)
    print('==================================')
    """

    total_devices = len(fats)
    comments = [
        f'{total_devices} TOTAL devices'
    ]
    counts = {}
    for item in fats:
        if item['device_type'] not in counts:
            counts[item['device_type']] = 1
        else:
            counts[item['device_type']] += 1
    for dtype in counts:
        comments.append(f'{counts[dtype]} {dtype} devices')
        print(f'{counts[dtype]} {dtype} devices')
    devices = {
        'timestamp' : valid_date,
        'comments': comments,
        'devices': fats
    }
    print(f"\n{len(devices['devices'])} total devices found")
    fname = 'upgrade_nicknames.json' # fats
    with open(fname, 'w') as jfile:
        json.dump(devices, jfile, separators=(', ', ': '), indent=4)
    
    
    return

    
if __name__ == "__main__":
    main()
