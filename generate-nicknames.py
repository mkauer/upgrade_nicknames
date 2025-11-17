#!/usr/bin/env python

import sys
import argparse
import json
from datetime import datetime

from fatcat_db.forwarder import Tunnel
from fatcat_db.mongoreader import MongoReader


valid_date = '2025-11-13'

def main():

    cmdparser = argparse.ArgumentParser()
    #cmdparser.add_argument(dest='dtype', help='device type')
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

    # current list from mongo by John J
    # mongo.db.stf_spat_devices.find({}).sort({'timestamp': -1}).limit(1)
    #spatfile = 'spat_devices.json'
    """
    spatfile = '../spat_devices_v2_fix-pdom-mbids.json'
    with open(spatfile, 'r') as jfile:
        temp = json.load(jfile)
        spats = temp['devices']
        comments = temp['comments']
    """
    
    # files I create (device-lookup.py for example)
    fats = []
    prodids = []
    pdates = []
    mbids = []
    icmids = []
    gotpopped = []
    for dt in ['NEW', 'pocam', 'mdom', 'degg']:
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
    print('THESE WERE REMOVED')
    for device in gotpopped:
        print(device)
    """
    """
    print("SPAT double check...")
    new_spats = []
    for fat in fats:
        found = False
        if not fat['mbid']:
            print(f"WARNING: no MBID for {fat}")
            continue
        for spat in spats:
            if fat['mbid'] == spat['mbid']:
                if not fat['icmid']:
                    print(f"WARNING: no ICMID for {spat['dut_type']} MBID {spat['mbid']}")
                spat['prod_id'] = fat['prod_id']
                spat['icmid'] = fat['icmid']
                if 'uid' in fat:
                    spat['fatcat_uid'] = fat['uid']
                spat['name'] = fat['name']
                found = True
                break
        if found:
            new_spats.append(spat)
        else:
            new_spats.append(fat)
    """
    
    #total_devices = len(new_spats)
    total_devices = len(fats)
    comments = [
        #'using the [new_spats] list',
        #'using the [fats] list',
        #'trying a different [round_2] method to make sure things are consistent',
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
        #'devices': new_spats
        'devices': fats
    }
    print(f"\n{len(devices['devices'])} total devices found")
    #fname = 'spat_devices_v11.json' # new_spats
    #fname = 'spat_devices_v12.json' # fats
    fname = 'upgrade_nicknames.json' # fats
    with open(fname, 'w') as jfile:
        json.dump(devices, jfile, separators=(', ', ': '), indent=4)
    
    
    return


def getNickname(uid):
    nicknames = {
        
    }
    
    return


def checkFatcat(uid, mongo):
    fpd = findParentDevices(uid, mongo)
    if len(fpd.parents) != 0:
        #print('[{0}] is not associated with any devices'.format(fpd.uid))
        for device in fpd.parents:
            print('\tuid: \"{0}\",  device_type: \"{1}\"'
                  .format(device['uid'], device['device_type']))
    return


class findParentDevices:
    
    def __init__(self, uid, mongoObj=False):
        if not mongoObj:
            self.mongo = MongoReader()
        else:
            self.mongo = mongoObj
        self.uid = uid
        self.parents = []
        if self.searchForDevice():
            #print('Found device [{0}], searching for associations...'.format(self.uid))
            self.findAssociationTree()
            
        
    def searchForDevice(self):
        if not self.mongo.findDeviceByUID(self.uid):
            devs = self.mongo.findDeviceByGenericID(self.uid)
            if not devs:
                print('\tDevice [{0}] is not in the database'.format(self.uid))
                return False
            elif len(devs) > 1:
                print('\tFound multiple matches...')
                for i, dev in enumerate(devs):
                    print('\t   [{2}] : device \"{0}\" uid \"{1}\"'
                          .format(dev['device_type'], dev['uid'], i+1))
                select = input('Select [1-{0}]: '.format(len(devs)))
                try:
                    select = int(select)
                except:
                    print('quitting, not int')
                    return False
                if select not in list(range(1, len(devs)+1)):
                    print('quitting, not in range')
                    return False
                self.uid = devs[select-1]['uid']
                return True
            else:
                self.uid = devs[0]['uid']
                return True
        else:
            return True
    
    
    def findAssociationTree(self):
        ids = self.mongo.findDeviceAssociationByIndex(self.uid)
        if ids:
            devs = []
            for _id in ids:
                devs.extend(self.mongo.findDeviceByUID(_id))
        # indexes might not be up-to-date, so then check the slower way
        else:
            devs = self.mongo.findDeviceAssociationByUID(self.uid)

        self.parents = devs
        return

    
if __name__ == "__main__":
    main()
