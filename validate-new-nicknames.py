#!/usr/bin/env python

import sys
import json
import argparse

def main():
    
    cmdparser = argparse.ArgumentParser()
    cmdparser.add_argument(dest='devices', help='give Upgrade devices json file')
    args = cmdparser.parse_args()

    newnames = args.devices
    with open(newnames, 'r') as jfile:
        upgrade = json.load(jfile, object_pairs_hook=check_dupes)

    nicknames = 'gen1-nicknames.json'
    with open(nicknames, 'r') as jfile:
        gen1 = json.load(jfile, object_pairs_hook=check_dupes)

    gen1_names = []
    for key in gen1['devices']:
        name = gen1['devices'][key]['name']
        if name in gen1_names:
            print(f'Gen1 [{name}] found in gen1_names')
        gen1_names.append(name)

    icu_names = []
    #for key in upgrade['devices']:
    #    name = upgrade['devices'][key]['name']
    for key in upgrade:
        name = upgrade[key]['name']
        if name in gen1_names:
            print(f'ICU [{name}] found in gen1_names')
        if name in icu_names:
            print(f'ICU [{name}] found in icu_names')
        icu_names.append(name)

    print(f'{len(gen1_names)} Gen1 names')
    print(f'{len(icu_names)} ICU names')

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
