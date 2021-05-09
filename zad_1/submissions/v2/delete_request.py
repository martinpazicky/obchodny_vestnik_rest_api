from http import HTTPStatus

from zad_1.models import OrPodanieIssues, BulletinIssues, RawIssues


def delete_data(record_id):
    # get raw/bulletin ids
    bulletin_id = OrPodanieIssues.objects.values('bulletin_issue').filter(pk=record_id)
    bulletin_id = bulletin_id[0]['bulletin_issue'] if bulletin_id else ''
    raw_id = OrPodanieIssues.objects.values('raw_issue').filter(pk=record_id)
    raw_id = raw_id[0]['raw_issue'] if raw_id else ''
    # delete podanie
    deleted = OrPodanieIssues.objects.filter(pk=record_id).delete()[0]
    if deleted == 0:
        return {"message": "Záznam Neexistuje"}, HTTPStatus.NOT_FOUND
    # count bulletin and raw in podanie
    raw_count_podanie = OrPodanieIssues.objects.filter(raw_issue=raw_id).count()
    blin_count_podanie = OrPodanieIssues.objects.filter(bulletin_issue=bulletin_id).count()
    # if bulletin or raw are not used delete them
    if raw_count_podanie == 0:
        RawIssues.objects.filter(pk=raw_id).delete()
    blin_count_raw = RawIssues.objects.filter(bulletin_issue=bulletin_id).count()
    if blin_count_podanie == 0 and blin_count_raw == 0:
        BulletinIssues.objects.filter(pk=bulletin_id).delete()
    return '', HTTPStatus.NO_CONTENT
