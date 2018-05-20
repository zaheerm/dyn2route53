"""
Migrate dyn.com dns to route 53

Set enviroment variables DYN_CUSTOMER DYN_USERNAME and DYN_PASSWORD
Usage: migrate.py <domainname>
"""
import os
import random
from typing import List, Dict
import docopt
from dyn.tm.session import DynectSession
from dyn.tm.zones import Zone
from dyn.tm.errors import DynectGetError, DynectAuthError
import boto3


class MigrationNotSupported(Exception):
    pass


def delete_route53_zone(zone_id: str):
    client = boto3.client('route53')
    client.delete_hosted_zone(Id=zone_id)
    print(f"Deleted zone {zone_id}")


def convert_dyn_to_route53_changes(zone_name: str, dyn_zone: Zone) -> List[Dict]:
    dyn_records = dyn_zone.get_all_records()
    route53_records = []
    for name, value in dyn_records.items():
        print(f"Zone {dyn_zone} has {name} with {value}")
        record_type = value[0].rec_name.upper()
        record_name = value[0].fqdn
        if record_type in ("SOA", "NS"):
            if record_name == zone_name:
                continue
            else:
                raise MigrationNotSupported(f"{record_type} records not supported")
        resource_records = []
        for sub_record in value:
            try:
                val = sub_record.address
            except AttributeError:
                val = sub_record.cname
            resource_records.append({"Value": val})
        record = {
            "Action": "INSERT",
            "ResourceRecordSet": {
                "Name": record_name,
                "Type": value[0].rec_name.upper(),
                "ResourceRecords": resource_records
            }}
        route53_records.append(record)
    return route53_records


def create_route53_zone(zone_name: str, dyn_zone: Zone):
    client = boto3.client('route53')
    route53_zone = client.create_hosted_zone(
        Name=zone_name,
        CallerReference=f"dyn2route53_{zone_name}_{random.randrange(100000)}")
    route53_changes = convert_dyn_to_route53_changes(zone_name, dyn_zone)
    print(route53_changes)
    all_route53_zones = client.list_hosted_zones()
    for zone in all_route53_zones.get("HostedZones", []):
        print(f"Route53 has {zone['Name']} hosted")
        if zone["Name"] == zone_name + ".":
            delete_route53_zone(zone["Id"])


def main():
    args = docopt.docopt(__doc__)
    try:
        with DynectSession(
                os.environ["DYN_CUSTOMER"],
                os.environ["DYN_USERNAME"],
                os.environ["DYN_PASSWORD"]) as session:
            zone = Zone(args["<domainname>"])
            create_route53_zone(args["<domainname>"], zone)
    except DynectGetError as exc:
        print(f"Zone could not be retrieved because of '{exc.message}'")
    except DynectAuthError as exc:
        print(f"Could not authenticate to dyn. Please check your environment variables")


if __name__ == '__main__':
    main()
