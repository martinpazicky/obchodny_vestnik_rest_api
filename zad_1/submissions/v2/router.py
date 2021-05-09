from django.http import HttpResponse, JsonResponse

from zad_1.submissions.v2.delete_request import delete_data
from zad_1.submissions.v2.get_request import get_data
from zad_1.submissions.v2.post_request import post_data
from zad_1.submissions.v2.put_request import update_data


def handle_request(request, record_id):
    if request.method == 'GET':
        data = get_data(request, record_id)
        return JsonResponse(data, json_dumps_params={'ensure_ascii': False}, safe=False)
    if request.method == 'POST':
        response, status = post_data(request)
        return JsonResponse(response, status=status)
    if request.method == 'PUT':
        response, status = update_data(request, record_id)
        return JsonResponse(response, status=status)
    if request.method == 'DELETE':
        response, status = delete_data(record_id)
        if response:
            return JsonResponse(response, status=status)
        return HttpResponse(status=status)
