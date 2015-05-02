import redis
import requests

from datetime import datetime, timedelta
from flask import Flask, render_template
from json import loads

from settings import REDIS_HOST, REDIS_PORT, REDIS_DB
from settings import REDIS_KEY, REDIS_KEY_TIMESTAMP

app = Flask(__name__)



@app.route('/container/<container_id>')
def describe_container(container_id):
    data = {}
    data['time'] = []

    # obtain timeseries from redis
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
    for resource in ['cpu', 'mem', 'net']:
        data[resource] = []
        for delta in range(60):
            timestamp = datetime.now() - timedelta(minutes=delta)
            key = REDIS_KEY.format(timestamp=timestamp.strftime(REDIS_KEY_TIMESTAMP),
                                   container_id=container_id, resource=resource)
            value = r.get(key)
            value = loads(value) if resource == 'net' else value
            if value != None:
                data[resource].append(value)
                data['time'].append(timestamp.strftime('%Y-%m-%d %H:%M'))

    # memory from bytes to MB
    data['mem'] = [int(x) / (1024.0)**2 for x in data['mem']]
    data['net'] = {
        'tx': map(lambda x: x['TxBps'], data['net']),
        'rx': map(lambda x: x['RxBps'], data['net']),
        'tx_err': map(lambda x: x['Transmit']['Errs'], data['net']),
        'rx_err': map(lambda x: x['Received']['Errs'], data['net']),
    }

    # feed the template with the retrieved data
    return render_template('container.html', data=data, name=container_id,
                           items=['CPU', 'Memory'])


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
