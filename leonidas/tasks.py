def highstate(target="*"):
    import salt.client
    client = salt.client.LocalClient()

    ret = client.cmd(target, "state.highstate")


def highstate_after_ping(target):
    """
    Ping the minion until it returns true, the run highstate.
    Useful for bootup.
    """
    import salt.client
    client = salt.client.LocalClient()

    ping = False
    while not ping:
        ret = client.cmd(target, "test.ping")

        # when the ping is seen and true
        for key in ret.keys():
            if key == target and ret[key]:
                ping = True

    client.cmd(target, 'state.highstate')


def wait_for_dns_update(name, instance_id):
    import boto
    import boto.ec2

    from .dns import create_dns_record

    conn = boto.connect_ec2()
    dns = None
    while not dns:
        rl = conn.get_all_instances(instance_ids=[instance_id])
        instance = rl[0].instances[0]

        dns = instance.public_dns_name

    create_dns_record(dns, name)
