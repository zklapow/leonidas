def wait_for_ping(target):
    import salt.client
    client = salt.client.LocalClient()

    while True:
        ret = client.cmd(target, "test.ping")

        # when the ping is seen and true
        for key in ret.keys():
            if key == target and ret[key]:
                return


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

    wait_for_ping(target)

    client.cmd(target, 'saltutil.sync_all')
    # Refresh pillar
    client.cmd(target, 'saltutil.refresh_pillar')
    # Sync everything first to make sure highstate is correct
    client.cmd(target, 'saltutil.sync_all')

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


def write_instance_id(target, instance_id):
    import salt.client
    client = salt.client.LocalClient()

    client.cmd(target, 'cmd.run', ['touch /etc/id && cat "%s" > /etc/id' % instance_id])


def sync_grains(target, instance_id):
    import salt.client
    client = salt.client.LocalClient()

    import boto
    import boto.ec2
    conn = boto.connect_ec2()

    rl = conn.get_all_instances(instance_ids=[instance_id])
    instance = rl[0].instances[0]

    tags = instance.__dict__['tags']
    for key in tags.keys():
        client.cmd(target, 'grains.setval', [key, tags[key]])


def git_pull(target, path, rev):
    import salt.client
    client = salt.client.LocalClient()

    # Fetch first
    client.cmd(target, 'git.fetch', [path, '--all'])
    # Then checkout
    client.cmd(target, 'git.checkout', [path, rev])
