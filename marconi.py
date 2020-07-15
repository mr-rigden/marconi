import datetime
import json
import os.path
import sys 

import dateutil.parser
from jinja2 import Environment, FileSystemLoader
import requests
import requests_cache
from slugify import slugify
import xmltodict

#requests_cache.install_cache()
file_loader = FileSystemLoader('templates')
env = Environment(loader=file_loader)

def initialize_json():
    blank_link = {
        'name': '',
        'url': ''
    }
    blank_link_list = [blank_link, blank_link]
    podcast_dict = {}
    podcast_dict['rss_url'] = ''
    podcast_dict['base_url'] = ''
    podcast_dict['social_links'] = blank_link_list
    podcast_dict['subscribe_links'] = blank_link_list
    podcast_dict['output'] = ''
    print(podcast_dict)
    with open('init.json', 'w') as json_file:
        json.dump(podcast_dict, json_file, indent=4)


def read_json(file_name):
    with open(file_name) as json_file:
        json_data = json.load(json_file)
    return json_data    

def get_episode_data(item):
    episode = {}
    episode['title'] = item['title']
    episode['description'] = item['description']
    episode['enclosure_url'] = item['enclosure']['@url']
    episode['date'] = dateutil.parser.parse(item['pubDate'])
    episode['slug'] = slugify(episode['title'])
    try:
        episode['number'] = item['itunes:episode']
    except:
        episode['number'] = 0

    return episode

def get_podcast(file_name):
    podcast = read_json(file_name)
    podcast['now'] = datetime.datetime.utcnow()
    r = requests.get(podcast['rss_url'])
    rss = xmltodict.parse(r.text)['rss']['channel']
    podcast['title'] = rss['title']
    podcast['image'] = rss['image']['url']
    podcast['description'] = rss['description']
    podcast['episodes'] = []
    podcast['slug'] = slugify(podcast['title'])
    for item in rss['item']:
        episode = get_episode_data(item)
        podcast['episodes'].append(episode)
    return podcast

def render_podcast(podcast):
    render_index(podcast)
    episode_dir = os.path.join(podcast['output'], 'episode')
    if not os.path.exists(episode_dir):
        os.mkdir(episode_dir)
    for episode in podcast['episodes']:
        render_episode(podcast, episode)


def render_index(podcast):
    file_path = os.path.join(podcast['output'], 'index.html')
    template = env.get_template('index.html')
    output = template.render(podcast=podcast)
    with open(file_path,'w') as f:
        f.write(output)
    
def render_episode(podcast, episode):
    file_dir = os.path.join(podcast['output'], 'episode', episode['slug'])
    if not os.path.exists(file_dir):
        os.mkdir(file_dir)
    file_path = os.path.join(file_dir, 'index.html')
    template = env.get_template('episode.html')
    output = template.render(podcast=podcast, episode=episode)
    with open(file_path,'w') as f:
        f.write(output)
    



if __name__ == '__main__':
    if sys.argv[1] == 'init':
        initialize_json()
        exit()

    podcast = get_podcast(sys.argv[1])
    render_podcast(podcast)

