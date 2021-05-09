from math import ceil

from django.db import connection

from zad_1.common.db_utills import fetch_all_as_dict
from zad_1.common.validator import validate_query_string


def prepare_where_clause(q_string):
    params = []
    clause = "WHERE"
    query = q_string.get('query', '').lower()
    if query:
        clause += " (LOWER(name) LIKE %s OR LOWER(address_line) LIKE %s)"
        params.append(("%" + query + "%"))
        params.append(("%" + query + "%"))
    if q_string.get('last_update_gte'):
        if query:
            clause += " AND"
        clause += " last_update >= %s "
        params.append(q_string.get('last_update_gte'))
    if q_string.get('last_update_lte'):
        if query or q_string.get('last_update_lte'):
            clause += " AND"
        clause += "  last_update <= %s"
        params.append(q_string.get('last_update_lte'))

    clause = "" if clause == "WHERE" else clause
    return {'clause': clause, 'params': params}


def get_count(where_clause):
    query = f'''SELECT count(cin) as count
    FROM ov.companies comp
        LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.or_podanie_issues GROUP BY company_id) 
        podanie
            ON podanie.company_id = comp.cin
        LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.znizenie_imania_issues GROUP BY company_id)
        imanie
            ON imanie.company_id = comp.cin
        LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.likvidator_issues GROUP BY company_id) 
        likvidator
            ON likvidator.company_id = comp.cin
        LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.konkurz_vyrovnanie_issues GROUP BY company_id) 
        vyrovnanie
            ON vyrovnanie.company_id = comp.cin
        LEFT JOIN (SELECT company_id, count(company_id) AS count
            FROM ov.konkurz_restrukturalizacia_actors GROUP BY company_id) restrukturalizacia
                ON restrukturalizacia.company_id = comp.cin
    {where_clause['clause']}'''
    with connection.cursor() as cursor:
        cursor.execute(query, where_clause['params'])
        count = fetch_all_as_dict(cursor)[0]['count']
        print(cursor.query)
    return count


def get_metadata(q_string, where_clause):
    count = get_count(where_clause)
    metadata = {'page': int(q_string.get('page', 1)),
                'per_page': int(q_string.get('per_page', 10)),
                'pages': ceil(count / int(q_string.get('per_page', 10))),
                'total': count,
                }
    return metadata


def prepare_query_params(q_string):
    params = {}
    params['limit'] = int(q_string.get('per_page', 10))
    page = int(q_string.get('page', 1))
    params['offset'] = (page - 1) * params['limit']
    params['order_by'] = q_string.get('order_by', 'cin')
    params['order_type'] = q_string.get('order_type', 'desc')
    return params


def get_data(request):
    q_string = validate_query_string(request, endpoint='companies')
    params = prepare_query_params(q_string)
    where_clause = prepare_where_clause(q_string)
    query = f'''SELECT comp.cin,name,comp.br_section,comp.address_line,last_update,
       COALESCE(podanie.count,0) AS or_podanie_issues_count,
       COALESCE(imanie.count,0) AS znizenie_imania_issues_count,
       COALESCE(likvidator.count,0) AS likvidator_issues_count,
       COALESCE(vyrovnanie.count,0) AS konkurz_vyrovnanie_issues_count,
       COALESCE(restrukturalizacia.count,0) AS konkurz_restrukturalizacia_actors_count
FROM ov.companies comp
    LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.or_podanie_issues GROUP BY company_id) 
    podanie
        ON podanie.company_id = comp.cin
    LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.znizenie_imania_issues GROUP BY company_id)
    imanie
        ON imanie.company_id = comp.cin
    LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.likvidator_issues GROUP BY company_id) 
    likvidator
        ON likvidator.company_id = comp.cin
    LEFT JOIN (SELECT company_id, count(company_id) AS count FROM ov.konkurz_vyrovnanie_issues GROUP BY company_id) 
    vyrovnanie
        ON vyrovnanie.company_id = comp.cin
    LEFT JOIN (SELECT company_id, count(company_id) AS count
        FROM ov.konkurz_restrukturalizacia_actors GROUP BY company_id) restrukturalizacia
            ON restrukturalizacia.company_id = comp.cin
{where_clause['clause']}
ORDER BY {params['order_by']} {params['order_type']}
LIMIT %s OFFSET %s;'''
    print(params)
    print(where_clause['params'])
    with connection.cursor() as cursor:
        cursor.execute(query, where_clause['params'] + [params['limit'], params['offset']])
        print(cursor.query)
        items = fetch_all_as_dict(cursor)

    metadata = get_metadata(q_string, where_clause)
    return {'items': items, 'metadata': metadata}
