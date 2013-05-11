#! /usr/bin/env/python

import boto.ec2
import argparse


def init(name, size="small", ami="ami-3fec7956"):
    conn = boto.ec2.connect_to_region('us-east-1')
    salt = open("salt.sh").read()
    conn.run_instances(ami, key_name="zklapow", user_data=salt)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")

    parser.add_argument("cmd", type=str, nargs="?")
    parser.add_argument("name", type=str, nargs="+")

    args = parser.parse_args()
    if args.cmd == "init":
        init(args.name)
