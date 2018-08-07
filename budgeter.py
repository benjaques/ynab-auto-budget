"""
Job computes funds needed to budget all scheduled transactions in YNAB.
Finds most active budget, cycles through scheduled transactions that live
within the time period between now and next paycheck, budgets for those
respective categories, and spits out the info regarding how much money is left
for that window to spend at will.

Should be run as cron job on the days user is paid.
"""
from datetime import datetime, timedelta
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
CURRENT_DATE = datetime.now()
NEXT_INCOME = CURRENT_DATE + timedelta(days=config.PAYMENT_WINDOW)

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

# cycle through transactions, removing any that are not due until next paycheck
def filter_transactions(scheduled_transactions):
    filtered_transactions = []
    for transaction in scheduled_transactions:
        next_occurrence = datetime.strptime(transaction['date_next'], '%Y-%m-%d')
        if CURRENT_DATE < next_occurrence < NEXT_INCOME:
            filtered_transactions.append(transaction)

    return filtered_transactions

def earmark_categories(to_be_budgeted, transactions, categories):
    for t in transactions:
        category_name = t['category_name']
        amount = milli_unit_converter(t['amount'])
        print(category_name, amount)



# ynab stores currency as milliunits
def milli_unit_converter(amount):
    return abs(amount / 1000)

# find id of active budget
budgets_response = get_json_response('budgets')
budget_id = find_budget_id(budgets_response)

# find scheduled transactions and filter by payment window
scheduled_transactions = get_json_response('budgets/{0}/scheduled_transactions'.format(budget_id))
immediate_transactions = filter_transactions(scheduled_transactions['data']['scheduled_transactions'])

current_month = get_json_response('budgets/{0}/months/current'.format(budget_id))
to_be_budgeted = current_month['data']['month']['to_be_budgeted']
categories = current_month['data']['month']['categories']

earmark_categories(to_be_budgeted, immediate_transactions, categories)
