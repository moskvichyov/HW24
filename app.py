import os

from flask import Flask, request
from werkzeug.exceptions import BadRequest

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


def build_query(f, query):
    query_items = query.split('|')
    result = map(lambda v: v.strip(), f)
    for item in query_items:
        split_item = item.split(':')
        cmd = split_item[0]
        if cmd == 'filter':
            arg = split_item[1]
            result = filter(lambda v, txt=arg: txt in v, result)
        elif cmd == 'map':
            arg = int(split_item[1])
            result = map(lambda v, idx=arg: v.split(" ")[idx], result)
        elif cmd == 'unique':
            result = set(result)
        elif cmd == 'sort':
            arg = split_item[1]
            if arg == 'desc':
                reverse = True
            else:
                reverse = False
            result = sorted(result, reverse=reverse)
        elif cmd == 'limit':
            arg = int(split_item[1])
            result = list(result)[:arg]
        return result


@app.route("/perform_query")
def perform_query():
    try:
        query = request.args['query']
        file_name = request.args['file_name']
    except KeyError:
        raise BadRequest(description="Не указаны необходимые параметры")

    file_path = os.path.join(DATA_DIR, file_name)
    if not os.path.exists(file_path):
        return BadRequest(description=f"{file_name} файл не найден")

    with open(file_path) as f:
        result = build_query(f, query)
        content = '\n'.join(result)

    return app.response_class(content, content_type="text/plain")

if __name__ == "__main__":
    app.run()