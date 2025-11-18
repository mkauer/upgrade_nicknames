#!/usr/bin/env python

import sys
import argparse
import json

from fatcat_db.forwarder import Tunnel
from fatcat_db.mongoreader import MongoReader


def main():

    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument(dest='dtype', help='device type')
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

    uids = []
    prodids = []
    docs = mongo.db.devices.find({'device_type': args.dtype})
    for doc in docs:
        uids.append(doc['uid'])
        for item in doc['aux_ids']:
            if item['type'] == 'serial-number':
                prodids.append(item['id'])
    uids = list(set(uids))
    prodids = list(set(prodids))
    
    
    # searching prod_id doesn't work for devices without *_v1 format
    # basically just degg and mdom
    # does not work for pocams
    if args.dtype in ['degg', 'mdom']:
        these_ids = prodids
    else:
        these_ids = uids
    
    data = []
    for thisid in these_ids:
        #thisid = 'mDOM_D073'
        if args.dtype in ['degg', 'mdom']:
            regid = thisid+'*_v?'
        else:
            regid = thisid
        docs = mongo.db.devices.find(
            {'uid': {'$regex': regid}, 'device_type': args.dtype}
            ).sort({'production_date': -1}).limit(1)
        doc = docs[0]
        #print(doc)
        #return
        
        dat = {}
        dat['device_type'] = doc['device_type']
        dat['fatcat_uid'] = doc['uid']
        dat['prod_date'] = doc['production_date']
        prodid = ""
        for item in doc['aux_ids']:
            if item['type'] == 'nickname':
                dat['name'] = item['id']
            if item['type'] == 'serial-number':
                prodid = item['id']
        if args.dtype == 'pocam':
            prodid = 'PC_'+prodid
        dat['prod_id'] = prodid
        
        
        # lookup mainboard and icm ids
        duid = mongo.db.device_assembly.find_one({'_id': doc['uid']})
        for uid in duid['devices']:
            if 'mainboard' in uid:
                mbdoc = mongo.db.devices.find_one({'uid': uid})
                for item in mbdoc['aux_ids']:
                    if item['type'] == 'eeprom':
                        dat['mbid'] = item['id']
                        #dat['dut_id'] = item['id']
                    if item['type'] == 'serial-number':
                        dat['mbsn'] = item['id']
            if 'icm_' in uid:
                icmdoc = mongo.db.devices.find_one({'uid': uid})
                for item in icmdoc['aux_ids']:
                    if item['type'] == 'eeprom':
                        dat['icmid'] = item['id']
                        
        if args.dtype in ['degg', 'mdom', 'lom16', 'lom18']:
            dat['subdevices'] = sorted(duid['devices'])
        
        data.append(dat)

    print(len(data), args.dtype+'s', 'found')
    filename = args.dtype+'_ids2.json'
    with open(filename, 'w') as jfile:
        json.dump(data, jfile, separators=(', ', ': '), indent=4)
    
    
    return


if __name__ == "__main__":
    main()
