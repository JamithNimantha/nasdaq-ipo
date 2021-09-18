import csv
from datetime import datetime, timedelta
import os
import requests

headers = {
    'authority': 'api.nasdaq.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36',
    'origin': 'https://www.nasdaq.com',
    'sec-fetch-site': 'same-site',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-dest': 'document',
    'referer': 'https://www.nasdaq.com/',
    'accept-language': 'en-US,en;q=0.9,si;q=0.8',
}

priced_headers = 'Deal ID', 'Symbol', 'Company Name', 'Exchange/ Market', 'Price', 'Shares', 'Date', 'Offer Amount', 'Actions'
upcoming_headers = 'Deal ID', 'Symbol', 'Company Name', 'Exchange/ Market', 'Price', 'Shares', 'Expected IPO Date', 'Offer Amount'


def get_ipo_calendar_data():
    today = datetime.today()
    last_month = today.replace(day=1) - timedelta(days=1)

    current_month_year_str = today.strftime('%Y-%m')
    last_month_year_str = last_month.strftime('%Y-%m')

    # print(f'current_month_year_str {current_month_year_str}')
    # print(f'last_month_year_str {last_month_year_str}')
    this_month = send_request(current_month_year_str)
    past_month = send_request(last_month_year_str)

    priced_list = []
    upcoming_list = []

    get_priced_list(priced_list, this_month)
    get_priced_list(priced_list, past_month)
    print(f'Found {len(priced_list)} records for IPO_Priced')

    get_upcoming_list(upcoming_list, this_month)
    get_upcoming_list(upcoming_list, past_month)
    print(f'Found {len(upcoming_list)} records for IPO_Upcoming')

    if not os.path.exists(f'{current_month_year_str}'):
        os.mkdir(f'{current_month_year_str}')

    path = f'{current_month_year_str}{os.sep}'
    write_to_csv(f'{path}IPO_Priced.csv', priced_headers, priced_list)
    write_to_csv(f'{path}IPO_Upcoming.csv', upcoming_headers, upcoming_list)


def get_priced_list(lst, month):
    if month['data']['priced']['rows'] is not None:
        for row in month['data']['priced']['rows']:
            lst.append(row.values())
    return lst


def write_to_csv(file_name, headers, data):
    with open(file_name, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
        f.close()


def get_upcoming_list(lst, month):
    if month['data']['upcoming']['upcomingTable']['rows'] is not None:
        for row in month['data']['upcoming']['upcomingTable']['rows']:
            lst.append(row.values())
    return lst


def send_request(date_str):
    params = {'date': date_str}
    url = 'https://api.nasdaq.com/api/ipo/calendar'
    print(f'Getting data for: {date_str}')
    response = requests.get(url, params=params, headers=headers)
    if response.json()['status']['rCode'] == 200:
        return response.json()
    else:
        print(f'No records were found for: {date_str}')
        return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    get_ipo_calendar_data()
