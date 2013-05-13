#! /usr/bin/env/python

import boto.ec2
import argparse

from fabric.api import env
from fabric.api import *

from leonidas import create_server, get_active_names

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")

    parser.add_argument("cmd", type=str, nargs="?")
    parser.add_argument("name", type=str, nargs="?")

    parser.add_argument("--salt-host", dest="host_string", type=str, default="ubuntu@salt.coherentclothes.com:22")
    parser.add_argument("-i", dest='keyfile', type=str, default="~/.ssh/zklapow.pem")

    args = parser.parse_args()

    conn = boto.ec2.connect_to_region('us-east-1')

    env.host_string = args.host_string
    with settings(user="ubuntu", host_string="salt.coherentclothes.com:22", key_filename=args.keyfile):
        if args.cmd == "init":
            create_server(conn, args.name)
        if args.cmd == "list":
            active = get_active_names(conn)

            for name in active:
                print(name)
