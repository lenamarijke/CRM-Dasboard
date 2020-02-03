from flask import Flask, render_template, flash, redirect, url_for, request, logging, Markup, Response, jsonify
import requests as api_request
import json
from datetime import datetime
import os

app = Flask(__name__, static_url_path='/static')

# Comma seperate numbers
app.jinja_env.filters['commafy'] = lambda v: "{:,}".format(v)

# Caching Control
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)

def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                 endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

# Headers for REST API call. 
headers = {
    "Content-Type": "application/json",
    "Accept": "application/hal+json",
    "x-api-key": "api-key"
}

# Get current year
this_year = int((datetime.now()).year)

# Example of function for REST API call to get data from API
saved_data = {}
def get_api_data(headers, url):
    if saved_data.get(url):
        return saved_data.get(url)
    # First call to get first data page from the API
    response = api_request.get(url=url, headers=headers, data=None, verify=False)

    # Convert the response string into json data and get embedded companyobjects
    json_data = json.loads(response.text)
    companyobjects = json_data.get("_embedded").get("companyobjects")
     
    # Check for more data pages and get those too
    nextpage = json_data.get("_links").get("next")
    while nextpage is not None:
        url = nextpage["href"]
        response = api_request.get(url=url, headers=headers, data=None, verify=False)
        json_data = json.loads(response.text)
        companyobjects += json_data.get("_embedded").get("companyobjects")
        nextpage = json_data.get("_links").get("next")

    saved_data[url] = companyobjects
    return companyobjects

# Index page
@app.route('/')
def index():
    # API call to get deals
    base_url = "https://api-test.company-crm.com/api-test/api/v1/companyobject/deal/"
    params = "?_limit=50"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)
    
    # API call to get customers
    base_url = "https://api-test.company-crm.com/api-test/api/v1/companyobject/company/"
    params = "?_limit=50"
    url = base_url + params
    response_companies = get_api_data(headers=headers, url=url)

    # TASK 1 - AVERAGE WON DEALS LAST YEAR
    # Filter for won deals last year. 
    won_deals_lasy_year = []
    deals_per_customer = {}
    deals_per_month = {'01': 0, '02': 0, '03': 0, '04': 0, '05': 0, '06': 0, '07': 0, '08': 0, '09': 0, '10': 0, '11': 0, '12': 0}
    bar_values = []
    for deal in response_deals:
        if (deal.get('dealstatus', {}).get('key') == 'agreement') and (str(this_year - 1) in deal.get('closeddate')):
            won_deals_lasy_year.append(deal.get('value'))

            # TASK 2 - WON DEALS PER MONTH LAST YEAR
            # ternary opertaor
            key = deal.get('closeddate')[5:7]
            deals_per_month[key] = deals_per_month.get(key) and deals_per_month.get(key) + 1 or 1  

            # TASK 3 - TOTAL VALUE OF DEALS PER CUSTOMER LAST YEAR
            key = deal.get('company')
            deals_per_customer[key] = deals_per_customer.get(key) and float(deals_per_customer.get(key)) + float(deal.get('value')) or float(deal.get('value'))
  
    for value in sorted (deals_per_month.keys()):
        bar_values.append(deals_per_month[value])

    company_map = {}
    for company in response_companies:
        company_map[company.get('_id')] = company
    
    average_won_deal = sum(won_deals_lasy_year) / len(won_deals_lasy_year)

    return render_template('home.html', year=str(this_year - 1), values=bar_values, deal=average_won_deal, customer_deals=deals_per_customer, company_map=company_map)

# Company data API Endpoint
@app.route('/api/companies')
def api_endpoint():
     # API call to get deals
    base_url = "https://api-test.company-crm.com/api-test/api/v1/companyobject/deal/"
    params = "?_limit=10"
    url = base_url + params
    response_deals = get_api_data(headers=headers, url=url)
    
    # API call to get customers
    base_url = "https://api-test.company-crm.com/api-test/api/v1/companyobject/company/"
    params = "?_limit=10"
    url = base_url + params
    response_companies = get_api_data(headers=headers, url=url)

    # TASK 4 - CUSTOMER STATUS
    # Set because mutable list without duplicates, order doesn't matter
    # Customer = a company that has bought sthg 2019 -> get ID of company in "Deals" 2019
    # Prospect = Never bought anything & not irrelevant -> get all IDs 'Deals' and =! 'Customer and =! irrelevant it's a prospect
    # Inactive = all left over companies in 'deals' that are no customers
    customer_status = set()
    prospect_status = set()
    inactive_status = set()
    all_deals = set()
    all_customers = set()

    for deal in response_deals:
        if (deal.get('dealstatus', {}).get('key') == 'agreement') and (str(this_year - 1) in deal.get('closeddate')) and deal.get('company') is not None:
            customer_status.add(deal.get('company'))
        if (deal.get('dealstatus', {}).get('key') == 'agreement') and deal.get('company') is not None:
            all_deals.add(deal.get('company'))
        if (deal.get('dealstatus', {}).get('key') == 'agreement') and (str(this_year - 1) not in deal.get('closeddate')) and deal.get('company') is not None:
            inactive_status.add(deal.get('company'))

    for company in response_companies:
        if (company.get('buyingstatus', {}).get('key') != 'notinterested'):
            all_customers.add(company.get('_id'))
    prospect_status = all_customers - all_deals

    # List with states of companies
    companies_by_status = list(map(lambda id: (id, 'Customer'), customer_status))+list(map(lambda id: (id, 'Prospect'), prospect_status))+list(map(lambda id: (id, 'Inactive'), inactive_status))

    company_map = {}
    for company in response_companies:
        company_map[company.get('_id')] = company

    return jsonify({
        'deals': response_companies, 
        'companies_by_status': companies_by_status, 
        'company_map': company_map,  
        'customers': len(customer_status), 
        'prospects': len(prospect_status), 
        'inactives': len(inactive_status)
    })

# Company page
@app.route('/companies')
def company():
    return render_template('companies.html', deals=[])


if __name__ == '__main__':
    app.secret_key = 'somethingsecret'
    app.run(debug=True)
    api.setup(app)