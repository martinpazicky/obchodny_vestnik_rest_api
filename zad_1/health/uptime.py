from django.db import connection


def get_server_uptime():
    with connection.cursor() as cursor:
        cursor.execute('''SELECT date_trunc('second', current_timestamp - pg_postmaster_start_time()) as uptime''')
        row = cursor.fetchone()
    return row

