import boto.ec2
import os.path
import random

fpath = os.path.dirname(os.path.abspath(__file__))


def get_names():
    with open(os.path.join(fpath, "names.txt")) as nf:
        return [l for l in nf.read().splitlines()]


def get_active_names(conn):
    active = []
    res = conn.get_all_instances()
    instances = [i for r in res for i in r.instances]
    for i in instances:
        active.append(i.__dict__['tags']['Name'])

    return active


def pick_name(conn):
    active = get_active_names(conn)
    names = get_names()

    name = random.choice(names)
    while name in active:
        name = random.choice(names)

    return name
