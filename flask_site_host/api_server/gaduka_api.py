from gaduka_engine import starter


from flask import request, jsonify
from flask_restful import Resource


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

        # API открытое, токен не нужен
        # if args["token"] not in config.REST_API_TOKENS:
        #     abort(403, message=f"Доступ к API без токена запрещён")
        result = run_with_json_images_input(args['code'], args['images'])
        response = jsonify(result)
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add('Access-Control-Allow-Headers', "*")
        response.headers.add('Access-Control-Allow-Methods', "*")
        return response
