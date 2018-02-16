import pickle
from os import environ as env

from flask import Flask, request, Response
from flask_cors import CORS
from redis import Redis

app = Flask(__name__)
CORS(app)
db = Redis(
    host=env.get('REDIS_HOST', 'localhost'),
    port=int(env.get('REDIS_PORT', 6379)),
    db=int(env.get('REDIS_DB', 0))
)


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'POST':
        db[path] = pickle.dumps(dict(
            data=request.data,
            headers=dict(request.headers)
        ))
        return '', 200
    else:
        try:
            val = pickle.loads(db[path])
        except KeyError:
            return '', 404
        return Response(
            val['data'],
            headers={'Content-Type': val['headers'].get('Content-Type')}
        )


if __name__ == '__main__':
    app.run(
        host=env.get('HTTP_HOST', '127.0.0.1'),
        port=int(env.get('HTTP_PORT', 5000))
    )
