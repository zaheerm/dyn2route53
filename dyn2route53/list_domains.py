#!/usr/bin/env python3
"""
List domains hosted on dyn

Set enviroment variables DYN_CUSTOMER DYN_USERNAME and DYN_PASSWORD
Usage: list_domains.py
"""
import os
import docopt
from dyn.tm.session import DynectSession
from dyn.tm.zones import get_all_zones


def list_dyn_domains():
    args = docopt.docopt(__doc__)
    with DynectSession(
            os.environ["DYN_CUSTOMER"],
            os.environ["DYN_USERNAME"],
            os.environ["DYN_PASSWORD"]) as session:
        zones = get_all_zones()
        for zone in zones:
            records = zone.get_all_records()
            for name, value in records.items():
                print(f"Zone {zone} has {name} with {value}")


if __name__ == '__main__':
    list_dyn_domains()
