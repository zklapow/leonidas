import boto
import boto.route53 as r53


def create_dns_record(instance, name, region="us-east-1", zone=None):
    conn = boto.connect_route53()

    if zone is None:
        zone = conn.get_zones()[0]
    else:
        zone = conn.get_hosted_zone_by_name(zone)

    dns = name + "." + zone.name
    zone.add_cname(dns, instance.public_dns_name)
