from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


def index(request):
    return HttpResponse("welcome")


def health(request):
    from zad_1.health.uptime import get_server_uptime
    uptime = get_server_uptime()
    dict_out = {'pgsql': {'uptime': str(uptime[0]).replace(',', '', 1)}}
    return JsonResponse(dict_out)


@csrf_exempt
def submissions(request, record_id=-1):
    from zad_1.submissions.v1.router import handle_request
    return handle_request(request, record_id)


@csrf_exempt
def v2submissions(request, record_id=-1):
    from zad_1.submissions.v2.router import handle_request
    return handle_request(request, record_id)


def companies(request):
    from zad_1.companies.v1.get_companies import get_data
    if request.method == 'GET':
        data = get_data(request)
        dict_out = data
        return JsonResponse(dict_out, json_dumps_params={'ensure_ascii': False})
    return HttpResponse("")


def v2companies(request):
    from zad_1.companies.v2.get_companies import get_data
    if request.method == 'GET':
        data = get_data(request)
        dict_out = data
        return JsonResponse(dict_out, json_dumps_params={'ensure_ascii': False})
    return HttpResponse("")
