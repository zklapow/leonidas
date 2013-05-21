from rq import Queue
from redis import Redis

from .tasks import git_pull, restart_supervisor

def deploy(target='*', path='/var/www/coherent', rev='master', rconn=None):
    if rconn is None:
        rconn = Redis()

    q = Queue(connection=rconn)
    q.enqueue(git_pull, target, path, rev)
    q.enqueue(restart_supervisor, target)
