import pickle
import json
from os import environ as env
from os.path import basename

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


def store_single(path):
    db[path] = pickle.dumps(dict(
        data=request.data,
        headers=dict(request.headers),
        content_type=request.content_type,
        content_length=request.content_length
    ))
    del db['mp|%s' % path]


def store_multipart(path):
    files = {}
    for key, file in request.files.items():
        files[key] = dict(
            filename=file.filename,
            headers=dict(file.headers),
            content_length=file.content_length,
            content_type=file.content_type,
            mimetype=file.mimetype,
            data=file.stream.read()
        )
    db['mp|%s' % path] = pickle.dumps(dict(
        data=request.data,
        headers=dict(request.headers),
        content_type=request.content_type,
        content_length=request.content_length,
        form=dict(request.form),
        files=files
    ))
    del db[path]


def retrieve_single(path):
    try:
        return pickle.loads(db[path])
    except KeyError:
        pass
    val = pickle.loads(db['mp|%s' % path])
    return dict(
        data=json.dumps(dict(
            type='multipart_metadata',
            form_keys=list(val['form'].keys()),
            file_keys=list(val['files'].keys())
        )),
        content_type='application/json',
    )


def retrieve_multipart(path):
    try:
        mpart_path, mpart_lookup = path.rsplit('/', 1)
    except ValueError:
        raise KeyError()
    val = pickle.loads(db['mp|%s' % mpart_path])
    ret = dict(
        data=None,
        content_type=None
    )
    try:
        ret['data'] = val['form'][mpart_lookup]
        ret['content_type'] = 'text/plain'
    except KeyError:
        file = val['files'][mpart_lookup]
        ret['data'] = file['data']
        ret['content_type'] = file['content_type']
    return ret


@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'POST':
        content_type = request.headers.get('Content-Type', '')
        if content_type.split(';')[0].lower() == 'multipart/form-data':
            store_multipart(path)
        else:
            store_single(path)
        return '', 200
    else:
        try:
            val = retrieve_single(path)
        except KeyError:
            try:
                val = retrieve_multipart(path)
            except KeyError:
                return '', 404
        return Response(
            val['data'],
            content_type=val['content_type'],
            headers=val.get('headers', {})
        )


if __name__ == '__main__':
    app.run(
        host=env.get('HTTP_HOST', '127.0.0.1'),
        port=int(env.get('HTTP_PORT', 5000))
    )
