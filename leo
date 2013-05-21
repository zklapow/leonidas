#! /usr/bin/env python

import boto.ec2
import argparse

from fabric.api import env
from fabric.api import *

from redis import Redis

from leonidas import create_server, get_active_names, deploy


def init(args):
    conn = boto.ec2.connect_to_region(args.region)

    env.host_string = args.host_string
    with settings(user="ubuntu", host_string="salt.coherentclothes.com:22", key_filename=args.keyfile):
        create_server(conn, args.name, rconn=Redis(host=args.redish), role=args.role, env=args.env)


def list_instances(args):
    conn = boto.ec2.connect_to_region(args.region)

    active = get_active_names(conn)
    for name in active:
        print(name)


def deploy_repo(args):
    deploy(args.target, args.path, args.rev, Redis(args.redish))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="deploy servers and applications")
    subparsers = parser.add_subparsers()

    parser.add_argument("--salt-host", dest="host_string", type=str, default="ubuntu@salt.coherentclothes.com:22")
    parser.add_argument("-i", dest='keyfile', type=str, default="~/.ssh/zklapow.pem")
    parser.add_argument("--region", dest='region', type=str, default="us-east-1")
    parser.add_argument("--target", dest='target', type=str, default="*")
    parser.add_argument("--redis-host", dest="redish", type=str, default="salt.coherentclothes.com")

    init_args = subparsers.add_parser('create')
    init_args.add_argument("name", type=str, nargs="?")
    init_args.add_argument("--role", dest="role", type=str, default="app")
    init_args.add_argument("--env", dest="env", type=str, default="dev")
    init_args.set_defaults(func=init)

    list_args = subparsers.add_parser('list')
    list_args.set_defaults(func=list_instances)

    deploy_args = subparsers.add_parser('deploy')
    deploy_args.add_argument("--path", dest="path", type=str, default="/var/www/coherent")
    deploy_args.add_argument("--rev", dest="rev", type=str, default="master")
    deploy_args.set_defaults(func=deploy_repo)

    args = parser.parse_args()
    args.func(args)
