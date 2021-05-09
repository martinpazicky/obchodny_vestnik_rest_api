from math import ceil
from django.db import connection
from zad_1.common.db_utills import fetch_all_as_dict
from zad_1.common.validator import validate_query_string


def prepare_where_clause(q_string):
    params = []
    clause = "WHERE"
    query = q_string.get('query', '').lower()
    if query:
        clause += " (LOWER(corporate_body_name) LIKE %s OR LOWER(city) LIKE %s OR cin::text LIKE %s)"
        params.append(("%" + query + "%"))
        params.append(("%" + query + "%"))
        params.append(("%" + query + "%"))
    if q_string.get('registration_date_gte'):
        if query:
            clause += " AND"
        clause += " registration_date >= %s "
        params.append(q_string.get('registration_date_gte'))
    if q_string.get('registration_date_lte'):
        if query or q_string.get('registration_date_gte'):
            clause += " AND"
        clause += "  registration_date <= %s"
        params.append(q_string.get('registration_date_lte'))

    clause = "" if clause == "WHERE" else clause
    return {'clause': clause, 'params': params}


# expects valid query string
# other params are prepared in prepare_where_clause
def prepare_query_params(q_string):
    params = {}
    params['limit'] = int(q_string.get('per_page', 10))
    page = int(q_string.get('page', 1))
    params['offset'] = (page - 1) * params['limit']
    params['order_by'] = q_string.get('order_by', 'id')
    params['order_type'] = q_string.get('order_type', 'desc')
    return params


def get_full_count(where_clause):
    query = f'''SELECT count(id)
    FROM ov.or_podanie_issues {where_clause['clause']};'''
    with connection.cursor() as cursor:
        cursor.execute(query, where_clause['params'])
        count = fetch_all_as_dict(cursor)[0]['count']
        print(cursor.query)
    return count


def get_metadata(q_string, where_clause):
    count = get_full_count(where_clause)
    metadata = {'page': int(q_string.get('page', 1)),
                'per_page':  int(q_string.get('per_page', 10)),
                'pages': ceil(count/int(q_string.get('per_page', 10))),
                'total': count,
                }
    return metadata


def get_data(request):
    q_string = validate_query_string(request)
    params = prepare_query_params(q_string)
    where_clause = prepare_where_clause(q_string)
    query = f'''SELECT id, br_court_name, kind_name, cin, registration_date, 
corporate_body_name,br_section,
br_insertion, text, street, postal_code, city 
FROM ov.or_podanie_issues
{where_clause['clause']}
ORDER BY {params['order_by']} {params['order_type']}
LIMIT %s OFFSET %s;'''

    with connection.cursor() as cursor:
        cursor.execute(query, where_clause['params'] + [params['limit'], params['offset']])
        print(cursor.query)
        rows = fetch_all_as_dict(cursor)
    metadata = get_metadata(q_string, where_clause)
    return {'items': rows, 'metadata': metadata}
