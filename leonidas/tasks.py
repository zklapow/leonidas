import salt.client


def highstate(target="*"):
    client = salt.client.LocalClient()

    ret = client.cmd(target, "state.highstate")


def highstate_after_ping(target):
    """
    Ping the minion until it returns true, the run highstate.
    Useful for bootup.
    """
    client = salt.client.LocalClient()

    ping = False
    while not ping:
        ret = client.cmd(target, "test.ping")

        # when the ping is seen and true
        for key in ret.keys():
            if key == target and ret[key]:
                ping = True

    client.cmd(target, 'state.highstate')
