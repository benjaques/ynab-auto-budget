from datetime import datetime
import json
import requests
import config

# api info
API_TOKEN = config.API_TOKEN
API_BASE_URL = 'https://api.youneedabudget.com/v1/'
HEADERS = {'Content-Type': 'application/json', 'Authorization': 'Bearer {0}'.format(API_TOKEN)}

# date stuff
ISO_FORMAT = '%Y-%m-%dT%H:%M:%S%z'
EARLIEST_DATE = '1970-01-01T00:00:00+00:00'

# returns json object of response given url 
def get_json_response(endpoint):
    api_url = '{0}{1}'.format(API_BASE_URL, endpoint)

    response = requests.get(api_url, headers=HEADERS)
    if response.status_code == 200:
        return json.loads(response.content.decode('utf-8'))
    else:
        return None

# find most recent budget, we want to use the active budget
def find_budget_id(json_response):
    if json_response is not None:
        most_recent = datetime.strptime(EARLIEST_DATE, ISO_FORMAT)

        for budget in json_response['data']['budgets']:
            budget_date = datetime.strptime(budget['last_modified_on'], ISO_FORMAT)
            if (max(budget_date, most_recent) == budget_date):
                most_recent = budget_date
                budget_id = budget['id']
            return budget_id
        else:
            return None


budgets_response = get_json_response('budgets')
budget_id = find_budget_id(budgets_response)
scheduled_transactions = get_json_response('budgets/{0}/scheduled_transactions'.format(budget_id))
print(json.dumps(scheduled_transactions, indent=4))
