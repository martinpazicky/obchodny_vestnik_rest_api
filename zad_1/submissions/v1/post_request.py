from http import HTTPStatus
from django.db import connection
from zad_1.common.db_utills import fetch_all_as_dict
from zad_1.common.utility import get_json_body_params, get_address_line
from zad_1.common.validator import validate_post_params


def prepare_queries():
    bulletin_insert = '''INSERT INTO ov.bulletin_issues (year,number,published_at,created_at,updated_at) VALUES
(EXTRACT(year FROM current_timestamp),
 (SELECT number FROM ov.bulletin_issues WHERE year = EXTRACT(year FROM current_timestamp) ORDER BY number desc LIMIT 1) + 1
 ,date_trunc('day', current_timestamp),current_timestamp,current_timestamp)
RETURNING id;'''

    raw_insert = '''INSERT INTO ov.raw_issues (bulletin_issue_id, file_name, created_at, updated_at) VALUES
('%s','-',current_timestamp,current_timestamp)
RETURNING  id'''

    podanie_insert = '''INSERT INTO ov.or_podanie_issues (bulletin_issue_id, raw_issue_id, br_mark, br_court_code,
                                  br_court_name, kind_code, kind_name, cin, registration_date,
                                  corporate_body_name, br_section, br_insertion, text, created_at,
                                  updated_at, address_line, street, postal_code, city)
VALUES (%s,%s,'-','-',%s,'-',%s,%s,%s,%s,%s,%s,%s,current_timestamp,current_timestamp,%s,%s,%s,%s)
RETURNING id, br_court_name, kind_name, cin, registration_date, corporate_body_name, br_section, text,
    street, postal_code, city'''

    return {'bulletin': bulletin_insert, 'raw': raw_insert, 'podanie': podanie_insert}


def post_data(request):
    params = get_json_body_params(request)
    if not params:
        return {'errors': [{'reasons': ['invalid_json']}]}, HTTPStatus.UNPROCESSABLE_ENTITY
    errors = validate_post_params(params)
    if errors:
        return {'errors': errors}, HTTPStatus.UNPROCESSABLE_ENTITY

    queries = prepare_queries()
    address_line = get_address_line(params)
    with connection.cursor() as cursor:
        cursor.execute(queries['bulletin'])
        result = fetch_all_as_dict(cursor)
        bulletin_id = int(result[0]['id'])
        cursor.execute(queries['raw'], [bulletin_id])
        result = fetch_all_as_dict(cursor)
        raw_id = int(result[0]['id'])
        cursor.execute(queries['podanie'], [bulletin_id, raw_id, params['br_court_name'], params['kind_name'],
                                            params['cin'], params['registration_date'][:10], params['corporate_body_name'],
                                            params['br_section'], params['br_insertion'], params['text'],
                                            address_line, params['street'], params['postal_code'], params['city'],
                                            ])
        result = fetch_all_as_dict(cursor)

    return {'response': result}, HTTPStatus.CREATED
