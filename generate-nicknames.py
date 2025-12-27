#!/usr/bin/env python

import sys
import json
import datetime

from fatcat_db.forwarder import Tunnel
from fatcat_db.mongoreader import MongoReader


valid_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d_%H:%M:%S")
write = 1

def main():
    
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
                
                if 'prod_date' in item:
                    pdate = item['prod_date']
                else:
                    pdate = '2001-01-01'
                pdates.append(pdate)
                
                lj = 18
                popi = None
                if item['mbid'] in mbids or item['icmid'] in icmids:
                    if item['mbid'] in mbids:
                        i = mbids.index(item['mbid'])
                        print(f"WARNING: duplicate MBID:")
                    if item['icmid'] in icmids:
                        i = icmids.index(item['icmid'])
                        print(f"WARNING: duplicate ICMID:")

                    mbids.append(item['mbid'])
                    icmids.append(item['icmid'])
                    
                    if pdate > pdates[i]:
                        popi = i
                        print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                        print(f"    {prodid.ljust(lj)} {pdate} - MBID: {item['mbid']} ICMID: {item['icmid']}")
                    else:
                        popi = -1
                        print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                        print(f"    {prodids[i].ljust(lj)} {pdates[i]} - MBID: {mbids[i]} ICMID: {icmids[i]}")
                    
                else:
                    mbids.append(item['mbid'])
                    icmids.append(item['icmid'])
                
                fats.append(item)
                
                # Devices with no MBID
                # oddballs (DEgg2021-3-045_v1 and DEgg2021-3-077_v1)
                if item['mbid'] == "":
                    print(f"WARNING: no MBID:")
                    popi = -1
                    print(f"    {prodids[popi].ljust(lj)} {pdates[popi]} - MBID: {mbids[popi]} ICMID: {icmids[popi]} - removed")
                # Devices with no ICMID
                if item['icmid'] == "":
                    print(f"WARNING: no ICMID:")
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
                    
    
    print('THESE WERE REMOVED')
    for device in gotpopped:
        print(device['device_type'], device['prod_id'], device['mbid'], device['icmid'])
    print()

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

    devices = {}
    trimmed = {}
    for device in fats:
        icmid = device['icmid']
        if icmid in devices:
            print(f'ERROR: [{icmid}] already exists')
        devices[icmid] = device
        if 'subdevices' in device:
            del device['subdevices']
        trimmed[icmid] = device
        
    device_file = {
        'timestamp' : valid_date,
        'comments': comments,
        'devices': devices
    }
    trimmed_file = {
        'timestamp' : valid_date,
        'comments': comments,
        'devices': trimmed
    }
    
    print(f"\n{len(device_file['devices'])} total devices found")
    fname = 'upgrade_devices_'+valid_date+'.json' # fats
    if write:
        with open(fname, 'w') as jfile:
            json.dump(device_file, jfile, separators=(', ', ': '), indent=4)
        with open('upgrade_devices.json', 'w') as jfile:
            json.dump(trimmed_file, jfile, separators=(', ', ': '), indent=4)
            
    return

    
if __name__ == "__main__":
    main()
