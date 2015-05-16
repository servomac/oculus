#!/usr/bin/env python3
import os

from datetime import datetime

from docker import Client
from itertools import islice
from json import dumps
from redis import StrictRedis

from settings import REDIS_DB, REDIS_KEY, REDIS_KEY_TIMESTAMP, REDIS_EXPIRE_TIME

DEBUG = True
SAMPLE_SIZE = 1 #TODO

DOCKER_HOST = os.getenv('DOCKER_HOST', 'unix:///var/run/docker.sock')
REDIS_HOST = os.getenv('DB_PORT_6379_TCP_ADDR')
REDIS_PORT = os.getenv('DB_PORT_6379_TCP_PORT')

def feed_db(container_id, stats):
    """ Store data to Redis.
        args:
         - constainer_id : (str) container's hash 12 first characters
         - stats : a dictionary of stats
    """
    if DEBUG:
        print('feed db with container {} stats'.format(container_id))

    # convert the time provided by stats to UTC format, parse it with strptime,
    # and transform it again to the desired REDIS_KEY_TIMESTAMP format
    instant_str = stats['read'][:-9]+stats['read'][-6:].replace(':', '')
    instant = datetime.strptime(instant_str, '%Y-%m-%dT%H:%M:%S.%f%z')
    timestamp = instant.strftime(REDIS_KEY_TIMESTAMP)

    r = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    for resource, value in stats.items():
        if resource != 'read':
            key = REDIS_KEY.format(timestamp=timestamp,
                                   container_id=container_id,
                                   resource=resource)

            r.set(key, dumps(value))
            r.expire(key, REDIS_EXPIRE_TIME)

            if DEBUG:
                print("Stored {} => {}".format(key, value))



if __name__ == '__main__':
    print(DOCKER_HOST)
    cli = Client(base_url=DOCKER_HOST)
    containers = cli.containers()

    for c in containers:
        container_id = c['Id'][:12]
        # stats_obj is a generator that streams stats
        stats_generator = cli.stats(c['Id'], decode=True)
        for stats in islice(stats_generator, 0, SAMPLE_SIZE):
            feed_db(container_id, stats)

