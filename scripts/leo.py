#! /usr/bin/env/python

import boto.ec2
import argparse
import sys


def init(name, size="small", ami="3fec7956"):
    ec2_id = open("/etc/aws-id")
    ec2_key = open("/etc/aws-key")
    conn = boto.ec2.connect_to_region('us-east', ec2_id.read(), ec2_key.read())

    salt = open("salt.sh").read()

    conn.run_instances(ami, key_name="zklapow", user_data=salt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")

    parser.add_argument("cmd", type=str, nargs="?")
    parser.add_argument("name", type=str, nargs="*")

    args = parser.parse_args()
    if args.cmd == "init":
        name = args.get('name', None)
        if not name:
            print("You must supply a name for the new server")
            sys.exit()
        else:
            init(name)
