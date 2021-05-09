# returns params dict if input is valid json, false otherwise
import json
import traceback


def get_json_body_params(request):
    body_unicode = request.body.decode('utf-8').replace("'", '"')
    try:
        body = json.loads(body_unicode)
        return body
    except json.decoder.JSONDecodeError:
        traceback.print_exc()
        return False


def get_address_line(params):
    return params['street'] + ', ' + params['postal_code'] + ' ' + params['city']
