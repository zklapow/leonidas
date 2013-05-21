from rq import Queue
from redis import Redis

from .tasks import git_pull

def deploy(target='*', path='/var/www/coherent', rev='master', rconn=None):
    if rconn is None:
        rconn = Redis()

    q = Queue('deploy', connection=rconn)
    q.enqueue(git_pull, target, path, rev)
