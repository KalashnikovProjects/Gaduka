import os
from datetime import timedelta

import config
from gaduka_engine import starter

from flask import Flask, request, jsonify, abort
from flask_restful import Resource, reqparse, abort, Api  # , Api
app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
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

        # if args["token"] not in config.REST_API_TOKENS:
        #     abort(403, message=f"Доступ к API без токена запрещён")
        result = run_with_json_images_input(args['code'], args['images'])
        return jsonify(result)


api.add_resource(GadukaRunCodeApi, "/api/v1/engine")