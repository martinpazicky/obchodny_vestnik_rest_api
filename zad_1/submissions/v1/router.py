from django.http import JsonResponse, HttpResponse
from zad_1.submissions.v1.delete_request import delete_data
from zad_1.submissions.v1.get_request import get_data
from zad_1.submissions.v1.post_request import post_data


def handle_request(request, record_id):
    if request.method == 'GET':
        data = get_data(request)
        dict_out = {'items': data['items'],
                    'metadata': data['metadata']}
        return JsonResponse(dict_out, json_dumps_params={'ensure_ascii': False})
    if request.method == 'POST':
        response, status = post_data(request)
        return JsonResponse(response, status=status)
    if request.method == 'DELETE':
        response, status = delete_data(record_id)
        if response:
            return JsonResponse(response, status=status)
        return HttpResponse(status=status)

