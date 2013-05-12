#! /usr/bin/env/python

import boto.ec2
import argparse
import random

from fabric.api import env
from fabric.api import *
from fabric.operations import get

from sh import rm


def get_names():
    with open("names.txt") as nf:
        return [l for l in nf.read().splitlines()]


def get_active_names(conn):
    active = []
    res = conn.get_all_instances()
    instances = [i for r in res for i in r.instances]
    for i in instances:
        active.append(i.__dict__['tags']['Name'])

    return active


def init(conn, name=None, type="t1.micro", ami="ami-3fec7956"):
    if name is None:
        # Pick a good name
        active = get_active_names(conn)
        names = get_names()

        name = random.choice(names)
        while name in active:
            name = random.choice(names)

    proceed = raw_input("Initializing %s as %s server. Proceed?[Y/n]: " % (name, type))

    if proceed in ['n', 'N', 'no', 'No']:
        print("Not inializing %s" % name)
        return

    run('mkdir -p tmp')
    with cd('tmp'):
        run("salt-key --gen-keys=%s" % name)
        sudo("cp %s.pub /etc/salt/pki/master/minions/%s" % (name, name))

        # Get the keys for distribution to the minion
        get("%s.pem" % name, "tmp.pem")
        get("%s.pub" % name, "tmp.pub")
    sudo('rm -rf tmp')

    pem = open('tmp.pem')
    pub = open('tmp.pub')

    salt = open("salt.sh").read()
    salt = salt % (name, pem.read(), pub.read())
    print(salt)

    reservation = conn.run_instances(ami,
                                     key_name="zklapow",
                                     user_data=salt,
                                     instance_type=type)

    reservation.instances[0].add_tag("Name", name)

    # Cleanup
    rm("tmp.pem")
    rm("tmp.pub")

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
            init(conn, args.name)
        if args.cmd == "list":
            active = get_active_names(conn)

            for name in active:
                print(name)
