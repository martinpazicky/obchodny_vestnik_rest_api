from datetime import datetime

BIG_INT_LIMIT = 9223372036854775807


def is_date_valid(date):
    try:
        datetime.fromisoformat(date)
        return True
    except ValueError:
        return False


# GET
def is_page_in_range(get_q_string):
    per_page = int(get_q_string.get('per_page', 10))
    page = int(get_q_string.get('page', 1)) - 1
    if page < 0 or ((page - 1) * per_page) > BIG_INT_LIMIT:
        return False
    return True


def is_per_page_in_range(get_q_string):
    per_page = int(get_q_string.get('per_page', 10))
    if per_page < 0 or per_page > BIG_INT_LIMIT:
        return False
    return True


# preserves only valid params
def validate_query_string(request, endpoint='submissions'):
    q_string = {}
    # common
    if request.GET.get('order_type', '') in ['asc', 'desc']:
        q_string['order_type'] = request.GET['order_type']
    if request.GET.get('per_page', '').isnumeric() and is_per_page_in_range(request.GET):
        q_string['per_page'] = request.GET['per_page']
    if request.GET.get('page', '').isnumeric() and is_page_in_range(request.GET):
        q_string['page'] = request.GET['page']
    if request.GET.get('query'):
        q_string['query'] = request.GET['query']

    # submissions
    if endpoint == 'submissions':
        if request.GET.get('order_by', '') \
                in ['id', 'br_court_name', 'kind_name', 'cin', 'registration_date',
                    'corporate_body_name', 'br_section', 'br_insertion', 'text',
                    'street', 'postal_code', 'city']:
            q_string['order_by'] = request.GET['order_by']
        if is_date_valid(request.GET.get('registration_date_gte', '')):
            q_string['registration_date_gte'] = request.GET['registration_date_gte'][:10]
        if is_date_valid(request.GET.get('registration_date_lte', '')):
            q_string['registration_date_lte'] = request.GET['registration_date_lte'][:10]

    # companies
    if endpoint == 'companies':
        if request.GET.get('order_by', '') \
                in ['cin', 'name', 'br_section', 'address_line', 'last_update',
                    'or_podanie_issues_count', 'znizenie_imania_issues_count',
                    'likvidator_issues_count', 'konkurz_vyrovnanie_issues_count',
                    'konkurz_restrukturalizacia_actors_count', ]:
            q_string['order_by'] = request.GET['order_by']
        if is_date_valid(request.GET.get('last_update_gte', '')):
            q_string['last_update_gte'] = request.GET['last_update_gte'][:10]
        if is_date_valid(request.GET.get('last_update_lte', '')):
            q_string['last_update_lte'] = request.GET['last_update_lte'][:10]

    return q_string


# POST
def check_for_missing_params(body):
    # list of required params, at first all are missing
    missing = ['br_court_name', 'kind_name', 'cin', 'registration_date', 'corporate_body_name',
               'br_section', 'br_insertion', 'text', 'street', 'postal_code', 'city']

    for param in body.keys():
        if param in missing:
            missing.remove(param)
    return missing


def check_for_correct_type(body):
    str_type = ['br_court_name', 'kind_name', 'registration_date', 'corporate_body_name',
                'br_section', 'br_insertion', 'text', 'street', 'postal_code', 'city']

    incorrect = []
    for key in str_type:
        if key in body and type(body[key]) != str:
            incorrect.append(key)
    return incorrect


def validate_post_params(params):
    missing = check_for_missing_params(params)
    errors = []
    if missing:
        for field in missing:
            errors.append({
                'field': field,
                'reasons': ['required']
            })

    if 'cin' not in missing and not str(params['cin']).isnumeric():
        errors.append({
            'field': 'cin',
            'reasons': ['not_number']
        })

    if 'registration_date' not in missing and (not is_date_valid(str(params['registration_date'])) or
                                               datetime.fromisoformat(str(params['registration_date'])).year
                                               != datetime.now().year):
        errors.append({
            'field': 'registration_date',
            'reasons': ['invalid_range']
        })

    incorrect = check_for_correct_type(params)
    if incorrect:
        for field in incorrect:
            errors.append({
                'field': field,
                'reasons': ['not_string']
            })
    return errors


def validate_put_params(params):
    errors = []

    if 'cin' in params and not str(params['cin']).isnumeric():
        errors.append({
            'field': 'cin',
            'reasons': ['not_number']
        })

    if 'registration_date' in params and (not is_date_valid(str(params['registration_date'])) or
                                          datetime.fromisoformat(str(params['registration_date'])).year
                                          != datetime.now().year):
        errors.append({
            'field': 'registration_date',
            'reasons': ['invalid_range']
        })

    incorrect = check_for_correct_type(params)
    if incorrect:
        for field in incorrect:
            errors.append({
                'field': field,
                'reasons': ['not_string']
            })
    return errors
