import pickle


def event_soup_to_json(event_soup):
    event_name = event_soup.find('div', attrs={'class': 'event'}).find('h4').text.strip()
    event_id = event_soup.find('div', attrs={'class': 'event'}).find('h4').find('a')['href'].split('/')[-1]
    if len(event_soup.find_all('div', attrs={'class': 'place'})) == 2:
        event_place = event_soup.find_all('div', attrs={'class': 'place'})[0].find('a').text.strip()
    else:
        event_place = None
    event_date = event_soup.find('div', attrs={'class': 'date'}).text.strip().split()[0]
    if event_soup.find_all('div', attrs={'class': 'place'}):
        event_time = event_soup.find_all('div', attrs={'class': 'place'})[-1].text.strip()
    else:
        event_time = ''
    event_actors = []
    actors_list_inner = event_soup.find('div', attrs={'class': 'actor'}).find_all('li')[1:]
    for actor_inner in actors_list_inner:
        event_actors.append(actor_inner.text.strip())

    event_json = {
        'name': event_name,
        'id': event_id,
        'url': 'https://www.eventernote.com/events/{}'.format(event_id),
        'place': event_place,
        'date': event_date,
        'time_str': event_time,
        'actors': event_actors
    }

    return event_json


def load_pushed_list(dump_file):
    pushed_list = dict()  # {events_id: date}
    try:
        with open(dump_file, 'rb') as fr:
            pushed_list = pickle.load(fr)
    except FileNotFoundError as e:
        pass

    return pushed_list


def dump_pushed_list(dump_file, pushed_list):
    with open(dump_file, 'wb') as fw:
        pickle.dump(pushed_list, fw)
