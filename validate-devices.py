#!/usr/bin/env python

import sys
import json
import argparse

from fatcat_db.forwarder import Tunnel
from fatcat_db.mongoreader import MongoReader


def main():
    
    cmdparser = argparse.ArgumentParser()
    #cmdparser.add_argument(dest='dtype', help='device type')
    cmdparser.add_argument('-nt','--no-tunnel', dest='tunnel', action='store_false',
                           help='Do not port forward mongodb server')    
    args = cmdparser.parse_args()

    # open ssh tunnel to mongo port
    #if args.tunnel: tunnel = Tunnel()

    # connect to mongo
    mongo = MongoReader(database='production_calibration',
                        user='icecube', pswd='skua')
    if not mongo.isConnected:
        print('no connection')
        return
    
    with open('nicknames.json', 'r') as jfile:
        devices = json.load(jfile, object_pairs_hook=check_dupes)
    
    for icmid in devices:
        try:
            doc = mongo.db.stfraw.find(
                {"phases.measurements.icmElectronicId.measured_value": icmid}
            ).sort({"start_time_millis": -1}).limit(1)[0]
        except:
            print('no STF results for', icmid, devices[icmid]["prod_id"])
            continue
        
        try:    date = doc["metadata"]["test_group_id"].split('_')[0]
        except: date = None

        try:    station = doc["station_id"]
        except: station = None
        
        mbid = doc["metadata"]["device"]["id"]
        if len(mbid) > 16:
            continue
        
        if mbid != devices[icmid]["mbid"]:
            prod_id = None
            for key in devices:
                if mbid == devices[key]["mbid"]:
                    prod_id = devices[key]["prod_id"]
            print(f"{date} STF mbid [{mbid}] {prod_id}  !=  "
                  f"nicknames mbid [{devices[icmid]["mbid"]}] {devices[icmid]["prod_id"]}")
            
        
    return


def check_dupes(pairs):
    result = dict()
    for key, val in pairs:
        if key in result:
            print(f"Duplicate key specified: {key}")
            #raise KeyError(f"WARNING: duplicate key: {key}")
        result[key] = val
    return result


if __name__ == "__main__":
    main()
