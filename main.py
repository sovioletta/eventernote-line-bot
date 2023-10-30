import configparser

import requests

import sheet_helper
import utils
import time
from linebot import LineBotApi
from linebot.models import TextSendMessage
from linebot.exceptions import LineBotApiError
from datetime import datetime, timedelta
from bs4 import BeautifulSoup


config = configparser.ConfigParser()
config.read('./configs.ini')
username = config['eventernote']['username']
line_channel_access_token = config['line']['access_token']
line_receiver_uid = config['line']['receiver_uid']
sheet_id = config['googlesheet']['sheet_id']
sheet_name = username

dump_file = './event_history'
base_date = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
en_home_url = 'https://www.eventernote.com'
en_user_url = '{}/users/{}'.format(en_home_url, username)

pushed_list = utils.load_pushed_list(dump_file)
push_queue = []

page = requests.get(en_user_url)
soup = BeautifulSoup(page.content, 'html.parser')

actors_list = soup.find('ul', attrs={'class': 'gb_actors_list'}).find_all('li')
for actor in actors_list:
    actor_postfix = actor.find('a')['href']
    en_actor_url = '{}{}/events'.format(en_home_url, actor_postfix)

    page = requests.get(en_actor_url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # TODO: traverse pages
    events_list = soup.find('div', attrs={'class': 'gb_event_list'}).find('ul').find_all('li', recursive=False)
    for event_soup in events_list:
        event = utils.event_soup_to_json(event_soup)
        if event['id'] not in pushed_list and event['date'] >= base_date:
            print(event)
            push_queue.append(event)
            pushed_list[event['id']] = event['date']

    time.sleep(1)

line_bot_api = LineBotApi(line_channel_access_token)
sheet = sheet_helper.init_sheet()
for event in push_queue:
    message = '[{date}]\n{title}\n{time}\n{actors}\n{place}\n{url}'.format(title=event['name'],
                                                                           date=event['date'],
                                                                           time=event['time_str'],
                                                                           place=event['place'],
                                                                           actors=', '.join(event['actors']),
                                                                           url=event['url'])
    try:
        # send to line
        line_bot_api.push_message(line_receiver_uid, TextSendMessage(text=message))
        pushed_list[event['id']] = event['date']

        # write to googlesheet
        sheet_helper.add_event(sheet, sheet_id, sheet_name, event['date'], event['name'], event['url'])
    except LineBotApiError as e:
        # TODO: exception handling
        pass

cleanup_list = []
for event_id in pushed_list:
    event_date = pushed_list[event_id]
    if event_date < base_date:
        cleanup_list.append(event_id)

for event_id in cleanup_list:
    pushed_list.pop(event_id)

utils.dump_pushed_list(dump_file, pushed_list)
