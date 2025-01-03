import secrets
from datetime import timedelta
from . import starter


from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS


app = Flask(__name__)

rs = CORS(app, resources={r"/api/*": {"origins": "*"}})
api = Api(app)
app.config['SECRET_KEY'] = secrets.token_urlsafe(16)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(
    days=3650
)


def run_with_json_images_input(code, raw_img):
    result_text, result_imgs = starter.run_from_api(code.split("\n"), raw_img)
    return {
        "result_text": result_text,
        "result_imgs": result_imgs
    }


class GadukaRunCodeApi(Resource):
    def post(self):
        args = request.get_json()
        args['images'] = [i.split(",")[1] for i in args['images']]

        result = run_with_json_images_input(args['code'], args['images'])
        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response


api.add_resource(GadukaRunCodeApi, "/api/v1/engine")


def main():
    app.run(host='0.0.0.0', port=8081)
