from http import HTTPStatus

from django.db import connection

from zad_1.common.db_utills import fetch_all_as_dict


def prepare_queries():
    queries = {}
    queries['raw_blin_ids'] = '''SELECT bulletin_issue_id, raw_issue_id FROM ov.or_podanie_issues WHERE id = %s;'''
    queries['del_podanie'] = '''WITH deleted AS (DELETE FROM ov.or_podanie_issues WHERE id = %s
RETURNING id) SELECT COUNT(id) FROM deleted;'''
    queries['raw_count_podanie'] = '''SELECT count(id) FROM ov.or_podanie_issues WHERE raw_issue_id = %s;'''
    queries['blin_count_podanie'] = '''SELECT count(id) FROM ov.or_podanie_issues WHERE bulletin_issue_id = %s;'''
    queries['del_raw'] = '''DELETE FROM ov.raw_issues WHERE id = %s;'''
    queries['blin_count_raw'] = '''SELECT count(id) FROM ov.raw_issues WHERE bulletin_issue_id = %s;'''
    queries['del_blin'] = '''DELETE FROM ov.bulletin_issues WHERE id = %s;'''
    return queries


def delete_data(record_id):
    q = prepare_queries()
    with connection.cursor() as cursor:
        cursor.execute(q['raw_blin_ids'], [record_id])
        other_ids = fetch_all_as_dict(cursor)
        other_ids = other_ids[0] if other_ids else {}
        cursor.execute(q['del_podanie'], [record_id])
        deleted = fetch_all_as_dict(cursor)[0]['count']
        if deleted == 0:
            return {"message": "Záznam Neexistuje"}, HTTPStatus.METHOD_NOT_ALLOWED
        cursor.execute(q['raw_count_podanie'], [other_ids['raw_issue_id']])
        raw_count = fetch_all_as_dict(cursor)[0]['count']
        cursor.execute(q['blin_count_podanie'], [other_ids['bulletin_issue_id']])
        blin_count = fetch_all_as_dict(cursor)[0]['count']
        if raw_count == 0:
            cursor.execute(q['del_raw'], [other_ids['raw_issue_id']])
        cursor.execute(q['blin_count_raw'], [other_ids['bulletin_issue_id']])
        blin_count_in_raw = fetch_all_as_dict(cursor)[0]['count']
        if blin_count == 0 and blin_count_in_raw == 0:
            cursor.execute(q['del_blin'], [other_ids['bulletin_issue_id']])

    return '', HTTPStatus.NO_CONTENT
