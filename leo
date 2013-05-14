#! /usr/bin/env python

import boto.ec2
import argparse

from fabric.api import env
from fabric.api import *

from leonidas import create_server, get_active_names


def init(args):
    conn = boto.ec2.connect_to_region(args.region)

    env.host_string = args.host_string
    with settings(user="ubuntu", host_string="salt.coherentclothes.com:22", key_filename=args.keyfile):
        create_server(conn, args.name, rconn=Redis(host=args.redish))


def list_instances(args):
    conn = boto.ec2.connect_to_region(args.region)

    active = get_active_names(conn)
    for name in active:
        print(name)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")
    subparsers = parser.add_subparsers()

    parser.add_argument("--salt-host", dest="host_string", type=str, default="ubuntu@salt.coherentclothes.com:22")
    parser.add_argument("-i", dest='keyfile', type=str, default="~/.ssh/zklapow.pem")
    parser.add_argument("--region", dest='region', type=str, default="us-east-1")

    init_args = subparsers.add_parser('create')
    init_args.add_argument("name", type=str, nargs="?")
    init_args.add_argument("--redis-host", dest="redish", type=str, default="salt.coherentclothes.com")
    init_args.set_defaults(func=init)

    list_args = subparsers.add_parser('list')
    list_args.set_defaults(func=list_instances)

    args = parser.parse_args()
    args.func(args)
