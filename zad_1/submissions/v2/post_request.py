from datetime import datetime
from http import HTTPStatus
from zad_1.common.utility import get_json_body_params, get_address_line
from zad_1.common.validator import validate_post_params
from zad_1.models import OrPodanieIssues, BulletinIssues, RawIssues


def post_data(request):
    params = get_json_body_params(request)
    if not params:
        return {'errors': [{'reasons': ['invalid_json']}]}, HTTPStatus.UNPROCESSABLE_ENTITY
    errors = validate_post_params(params)
    if errors:
        return {'errors': errors}, HTTPStatus.UNPROCESSABLE_ENTITY

    bulletin_issue = BulletinIssues.objects.create(
        year=datetime.now().year,
        number=BulletinIssues.objects.filter(year=datetime.now().year).values('number')
                   .latest('number')['number'] + 1,
        published_at=datetime.now(),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    raw_issue = RawIssues.objects.create(bulletin_issue_id=bulletin_issue.id,
                                         file_name='-',
                                         created_at=datetime.now(),
                                         updated_at=datetime.now())

    podanie_issue = OrPodanieIssues.objects.create(bulletin_issue_id=bulletin_issue.id,
                                                   raw_issue_id=raw_issue.id,
                                                   br_mark='-',
                                                   br_court_code='-',
                                                   br_court_name=params['br_court_name'],
                                                   kind_name=params['kind_name'],
                                                   cin=params['cin'],
                                                   registration_date=params['registration_date'],
                                                   corporate_body_name=params['corporate_body_name'],
                                                   br_section=params['br_section'],
                                                   br_insertion=params['br_insertion'],
                                                   text=params['text'],
                                                   created_at=datetime.now(),
                                                   updated_at=datetime.now(),
                                                   address_line=get_address_line(params),
                                                   street=params['street'],
                                                   postal_code=params['postal_code'],
                                                   city=params['city'],
                                                   )
    return {'response': [{'id': podanie_issue.id,
                          'br_court_name': podanie_issue.br_court_name,
                          'kind_name': podanie_issue.kind_name,
                          'cin': podanie_issue.cin,
                          'registration_date': podanie_issue.registration_date,
                          'corporate_body_name': podanie_issue.corporate_body_name,
                          'br_section': podanie_issue.br_section,
                          'text': podanie_issue.text,
                          'street': podanie_issue.street,
                          'postal_code': podanie_issue.postal_code,
                          'city': podanie_issue.city}]}, HTTPStatus.CREATED
