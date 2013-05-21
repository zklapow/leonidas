from .names import pick_name

from fabric.api import *
from fabric.operations import get

from sh import rm

from rq import Queue
from .tasks import highstate_after_ping, wait_for_dns_update, wait_for_ping, sync_grains

import os.path
import time
import sys

fpath = os.path.dirname(os.path.abspath(__file__))


def create_server(conn, name=None, type="t1.micro", ami="ami-3fec7956", rconn=None, role="app", env="dev"):
    if name is None:
        name = pick_name(conn)

    proceed = raw_input("Initializing %s as %s server. Proceed?[Y/n]: " % (name, type))

    if proceed in ['n', 'N', 'no', 'No']:
        print("Not inializing %s" % name)
        return

    # Create, tranfer and delete the keys
    run('mkdir -p tmp')
    with cd('tmp'):
        run("salt-key --gen-keys=%s" % name)
        sudo("cp %s.pub /etc/salt/pki/master/minions/%s" % (name, name))

        # Get the keys for distribution to the minion
        get("%s.pem" % name, "tmp.pem")
        get("%s.pub" % name, "tmp.pub")
    sudo('rm -rf tmp')

    # Insert the keys into the bootstrap script
    pem = open('tmp.pem')
    pub = open('tmp.pub')

    salt = open(os.path.join(fpath, "salt.sh")).read()
    salt = salt % (name, pem.read(), pub.read())
    #print(salt)

    reservation = conn.run_instances(ami,
                                     key_name="zklapow",
                                     user_data=salt,
                                     instance_type=type)

    # Name and DNS
    instance = reservation.instances[0]
    sys.stdout.write('\nWaiting for %s to start.' % name)
    while instance.state == 'pending':
        sys.stdout.write('.')
        time.sleep(1)
        instance.update()
    sys.stdout.write('\n')

    instance.add_tag("Name", name)
    instance.add_tag("env", env)
    instance.add_tag("role", role)

    if rconn is None:
        rconn = Redis()
    q = Queue(name, connection=rconn, default_timeout=1800)

    print("%s Public DNS: %s" % (name, instance.public_dns_name))
    q.enqueue_call(func=wait_for_dns_update, args=(name, instance.id), timeout=1800)

    # Don't do anything else until salt is available
    q.enqueue(wait_for_ping, name)

    # This needs to be done before highstate
    q.enqueue(sync_grains, name, instance.id)

    # Run highstate on the salt master
    q.enqueue(highstate_after_ping, name)

    # Cleanup
    rm("tmp.pem")
    rm("tmp.pub")
