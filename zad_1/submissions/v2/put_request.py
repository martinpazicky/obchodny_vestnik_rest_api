from http import HTTPStatus

from zad_1.common.utility import get_json_body_params
from zad_1.common.validator import validate_put_params
from zad_1.models import OrPodanieIssues


def update_data(request, record_id):
    params = get_json_body_params(request)
    if not params:
        return {'errors': [{'reasons': ['invalid_json']}]}, HTTPStatus.UNPROCESSABLE_ENTITY
    errors = validate_put_params(params)
    if errors:
        return {'errors': errors}, HTTPStatus.UNPROCESSABLE_ENTITY

    try:
        podanie_issue = OrPodanieIssues.objects.get(pk=record_id)
    except OrPodanieIssues.DoesNotExist:
        return {'errors': [{'reasons': ['invalid_id']}]}, HTTPStatus.UNPROCESSABLE_ENTITY

    if 'br_court_name' in params:
        podanie_issue.br_court_name = params['br_court_name']
    if 'kind_name' in params:
        podanie_issue.kind_name = params['kind_name']
    if 'cin' in params:
        podanie_issue.cin = params['cin']
    if 'registration_date' in params:
        podanie_issue.registration_date = params['registration_date']
    if 'corporate_body_name' in params:
        podanie_issue.corporate_body_name = params['corporate_body_name']
    if 'br_section' in params:
        podanie_issue.br_section = params['br_section']
    if 'br_insertion' in params:
        podanie_issue.br_insertion = params['br_insertion']
    if 'text' in params:
        podanie_issue.text = params['text']
    if 'street' in params:
        podanie_issue.street = params['street']
    if 'postal_code' in params:
        podanie_issue.postal_code = params['postal_code']
    if 'city' in params:
        podanie_issue.city = params['city']
    podanie_issue.save()

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
