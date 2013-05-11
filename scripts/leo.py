#! /usr/bin/env/python

import boto.ec2
import argparse


def init(name, size="small", ami="3fec7956"):
    ec2_id = open("/etc/aws-id")
    ec2_key = open("/etc/aws-key")
    conn = boto.ec2.connect_to_region('us-east', aws_access_key_id=ec2_id.read(), aws_secret_access_key=ec2_key.read())

    salt = open("salt.sh").read()

    conn.run_instances(ami, key_name="zklapow", user_data=salt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")

    parser.add_argument("cmd", type=str, nargs="?")
    parser.add_argument("name", type=str, nargs="+")

    args = parser.parse_args()
    if args.cmd == "init":
        init(args.name)
