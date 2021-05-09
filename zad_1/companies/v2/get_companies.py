from math import ceil

from django.db.models import Count
from zad_1.common.validator import validate_query_string
from zad_1.models import Companies


def prepare_filter(q_string):
    from django.db.models import Q
    q = Q()

    if q_string.get('query'):
        q |= Q(name__icontains=q_string.get('query'))
        q |= Q(address_line__icontains=q_string.get('query'))

    if q_string.get('last_update_gte'):
        q &= Q(last_update__gte=q_string.get('last_update_gte'))

    if q_string.get('last_update_lte'):
        q &= Q(last_update__lte=q_string.get('last_update_lte'))
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
    params['order_by'] = q_string.get('order_by', 'cin')
    params['order_type'] = q_string.get('order_type', 'desc')
    return params


def get_metadata(q_string, filter_q):
    count = Companies.objects.filter(filter_q).values('cin').count()
    metadata = {'page': int(q_string.get('page', 1)),
                'per_page': int(q_string.get('per_page', 10)),
                'pages': ceil(count / int(q_string.get('per_page', 10))),
                'total': count,
                }
    return metadata


def get_data(request):
    q_string = validate_query_string(request, endpoint='companies')
    params = prepare_query_params(q_string)
    order = get_order_clause(params)
    filter_q = prepare_filter(q_string)

    x = Companies.objects.values('cin', 'name', 'br_section', 'address_line', 'last_update').filter(filter_q).annotate(
        or_podanie_issues_count=Count('orpodanieissues', distinct=True),
        znizenie_imania_issues_count=Count('znizenieimaniaissues',
                                           distinct=True),
        likvidator_issues_count=Count('likvidatorissues', distinct=True),
        konkurz_vyrovnanie_issues_count=Count('konkurzvyrovnanieissues',
                                              distinct=True),
        konkurz_restrukturalizacia_actors_count=Count('konkurzrestrukturalizaciaactors',
                                                      distinct=True)
    ).order_by(order)[params['from']: params['to']]

    print(x.query)
    companies_list = list(x)
    metadata = get_metadata(q_string, filter_q)
    return {'items': companies_list, 'metadata': metadata}
