from .names import pick_name
from .dns import create_dns_record

from fabric.api import *
from fabric.operations import get

from sh import rm

from rq import Connection, Queue
from .tasks import highstate_after_ping

import os.path

fpath = os.path.dirname(os.path.abspath(__file__))


def create_server(conn, name=None, type="t1.micro", ami="ami-3fec7956", rconn=None):
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
    instance.add_tag("Name", name)
    create_dns_record(instance, name)

    # Run highstate on the salt master
    if rconn is None:
        rconn = Redis()
    q = Queue(connection=rconn)

    q.enqueue(highstate_after_ping, name)

    # Cleanup
    rm("tmp.pem")
    rm("tmp.pub")
