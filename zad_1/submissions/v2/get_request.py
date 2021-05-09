from math import ceil

from zad_1.common.validator import validate_query_string


def prepare_filter(q_string, record_id):
    from django.db.models import Q
    q = Q()

    if record_id != -1:
        q &= Q(id=record_id)

    if q_string.get('query'):
        if q_string.get('query').isnumeric():
            q |= Q(cin=int(q_string.get('query')))
        else:
            q |= Q(city__icontains=q_string.get('query'))
            q |= Q(corporate_body_name__icontains=q_string.get('query'))

    if q_string.get('registration_date_gte'):
        q &= Q(registration_date__gte=q_string.get('registration_date_gte'))

    if q_string.get('registration_date_lte'):
        q &= Q(registration_date__lte=q_string.get('registration_date_lte'))
    return q


def get_order_clause(params):
    from django.db.models import F
    order = F(params['order_by']).desc(nulls_last=True) if params['order_type'] == 'desc' else \
        F(params['order_by']).asc(nulls_last=True)
    return order


def prepare_query_params(q_string):
    params = {}
    page = int(q_string.get('page', 1))
    params['from'] = (page - 1) * int(q_string.get('per_page', 10))
    params['to'] = params['from'] + int(q_string.get('per_page', 10))
    params['order_by'] = q_string.get('order_by', 'id')
    params['order_type'] = q_string.get('order_type', 'desc')
    return params


def get_metadata(q_string, filter_q):
    from zad_1.models import OrPodanieIssues
    count = OrPodanieIssues.objects.filter(filter_q).values('id').count()
    metadata = {'page': int(q_string.get('page', 1)),
                'per_page': int(q_string.get('per_page', 10)),
                'pages': ceil(count / int(q_string.get('per_page', 10))),
                'total': count,
                }
    return metadata


def get_data(request, record_id):
    q_string = validate_query_string(request)
    params = prepare_query_params(q_string)
    filter_q = prepare_filter(q_string, record_id)
    metadata = get_metadata(q_string, filter_q)
    order = get_order_clause(params)
    from zad_1.models import OrPodanieIssues
    issues = OrPodanieIssues.objects.filter(filter_q)\
    .order_by(order) \
        .values('id', 'br_court_name', 'kind_name', 'cin', 'registration_date', 'corporate_body_name',
                'br_section', 'br_insertion', 'text', 'street', 'postal_code', 'city')\
        [params['from']: params['to']]

    print(issues.query)
    issues_list = list(issues)
    out = {"items": issues_list,
           "metadata": metadata}
    return out
