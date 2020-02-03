

# def average_won_deals(response_data):
#     # TASK 1 - AVERAGE WON DEALS LAST YEAR
#     # Filter for won deals last year. 
#     # Put this in deals.py file
#     won_deals_lasy_year = []
#     for deal in response_deals:
#         if (deal.get('dealstatus', {}).get('key') == 'agreement') and (str(this_year - 1) in deal.get('closeddate')):
#             won_deals_lasy_year.append(deal.get('value'))
#     average_won_deal = sum(won_deals_lasy_year) / len(won_deals_lasy_year)
#     # return
#     print(sum(won_deals_lasy_year) / len(won_deals_lasy_year))

# def won_deals_per_month(response_data):
#     # TASK 2 - WON DEALS PER MONTH LAST YEAR
#     # ternary opertaor
#     deals_per_month = {}
#     for deal in response_deals:
#         if (deal.get('dealstatus', {}).get('key') == 'agreement') and (str(this_year - 1) in deal.get('closeddate')):
#             key = deal.get('closeddate')[5:7]
#             deals_per_month[key] = deals_per_month.get(key) and deals_per_month.get(key) + 1 or 1  
#     print(deals_per_month)

# def dealvalue_per_customer(response_data):
#     # TASK 3 - TOTAL VALUE OF DEALS PER CUSTOMER LAST YEAR
#     deals_per_customer = {}
#     for deal in response_deals:
#         if (deal.get('buyingstatus', {}).get('key') == 'active') and (str(this_year - 1) in deal.get('closeddate')):
#             key = deal.get('company')
#             deals_per_customer[key] = deals_per_customer.get(key) and float(deals_per_customer.get(key)) + float(deal.get('value')) or float(deal.get('value'))
#     print(deals_per_customer)

