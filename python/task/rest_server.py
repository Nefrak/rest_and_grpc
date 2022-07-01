from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

stats = [
    {
        'create_datetime': '2021-02-14 11:22:33.000',
        'size': 5,
        'mimetype': 'image',
        'name': 'asd'
    }
]

@app.route('/file/9c465aa7-05fd-46eb-b759-344c48abc85f/stat/', methods=['GET'])
def get_stats():
    return jsonify({'stats': stats})

@app.route('/file/9c465aa7-05fd-46eb-b759-344c48abc85f/read/', methods=['GET'])
def get_read():
    try:
        return send_from_directory('/home/nefrak/flask_app', 'test.txt')
    except:
        return "Missing file"

if __name__ == '__main__':
    app.run(debug=True)