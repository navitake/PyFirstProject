from flask import Flask
import flask
from flask import request
from ocrClass import OcrClass

app = Flask(__name__)


@app.route("/", methods=["POST"])
def index():
    if request.form == None:
        return flask.jsonify({
            "code": 400, "msg": "Bad"
        })

    else:
        string = OcrClass.funcOCR(request.files["upload_file"].stream.read() )
        print(string)
        if bool(string):
            return flask.jsonify({
                "code": 200, "msg": "OK", "result": string
            })
        else:
            return flask.jsonify({
                "code": 400, "msg": "Bad"
            })


if __name__ == "__main__":
    app.run(host="localhost", port=8080, debug=False)
