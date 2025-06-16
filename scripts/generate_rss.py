import requests
from lxml import etree as ET
from datetime import datetime
from dateutil import parser as date_parser
import os

# Constants
BEARER_TOKEN = os.getenv("BEARER_TOKEN")
USERNAME = 'CUSocialMedia'
USER_ID = 132922064 # Value was fetched from using Twitter API v2 /2/users/by/username/CUSocialMedia
MAX_TWEETS = 10
RSS_FILE = '../feeds/cusocialmedia_rss.xml'

# Fetches the latest tweets from a user using Twitter API v2
def get_user_tweets(user_id):
    url = f'https://api.twitter.com/2/users/{user_id}/tweets'
    headers = {'Authorization': f'Bearer {BEARER_TOKEN}'}
    params = {
        'max_results': MAX_TWEETS,
        'exclude': "replies,retweets",
        'tweet.fields': "id,text,author_id,created_at,attachments,entities",
        'expansions': "attachments.media_keys",
        'media.fields': "url,type,alt_text,preview_image_url",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

# Formats tweet text by removing links for media attachments
def format_text(tweet, media_map):
    text = tweet["text"]

    if tweet.get("entities"):
        # URLs - Remove URLs that are media attachments
        if 'urls' in tweet["entities"]:
            for url in tweet["entities"]['urls']:
                if "media_key" in url:
                    text = text.replace(url['url'], '')

# Formats tweet text with HTML links for URLs, mentions, and hashtags
def format_entities(tweet, media_map):
    text = tweet["text"]

    if tweet.get("entities"):
        # URLs
        if 'urls' in tweet["entities"]:
            for url in tweet["entities"]['urls']:
                expanded_url = url.get('expanded_url', url['url'])
                display_url = url.get('display_url', expanded_url)
                if "media_key" not in url:
                    text = text.replace(url['url'], f'<a href="{expanded_url}" target="_blank">{display_url}</a>')
                else: # Replace media URLs with empty string
                    text = text.replace(url['url'], '')

        # Mentions
        if 'mentions' in tweet["entities"]:
            for mention in tweet["entities"]['mentions']:
                username = mention['username']
                text = text.replace(f"@{username}", f'<a href="https://x.com/{username}" target="_blank">@{username}</a>')

        # Hashtags
        if 'hashtags' in tweet["entities"]:
            for hashtag in tweet["entities"]['hashtags']:
                tag = hashtag['tag']
                text = text.replace(f"#{tag}", f'<a href="https://x.com/hashtag/{tag}?src=hashtag_click" target="_blank">#{tag}</a>')

        # Media attachments
        if "attachments" in tweet and "media_keys" in tweet["attachments"]:
            count = len(tweet["attachments"]['media_keys'])
            text += f'<div style="display:flex; flex-wrap:wrap; border-radius:16px; overflow: hidden; width: fit-content;">'
            if count > 1:
                width = 50
                aspect_ratio = 4/3
            else:
                width = 100
                aspect_ratio = 'auto'
            for media_key in tweet["attachments"]['media_keys']:
                media = media_map.get(media_key)
                if media:
                    if media["type"] == 'photo':
                        text += f'<img src="{media["url"]}" alt="" style="max-width:{width}%; max-height: 300px; height:auto; aspect-ratio:{aspect_ratio}; object-fit: cover;" />'
                    elif media["type"] in ['video', 'animated_gif']:
                        text += f'<img src="{media["preview_image_url"]}" alt="" style="max-width:{width}%; max-height: 300px; height:auto; aspect-ratio:{aspect_ratio}; object-fit: cover;" />'
            text += '</div>'
    return text

# Returns dictionary mapping media keys to media objects
def get_media_map(includes):
    media_map = {}
    for media in includes.get('media', []):
        media_map[media.get("media_key")] = media
    return media_map

# Generates the RSS feed from the tweets data
def create_rss_feed(tweets, username):
    rss = ET.Element('rss', version='2.0')
    channel = ET.SubElement(rss, 'channel')

    ET.SubElement(channel, 'title').text = f"Tweets by @{username}"
    ET.SubElement(channel, 'link').text = f"https://x.com/{username}"
    ET.SubElement(channel, 'description').text = f"Recent tweets posted by @{username}"
    ET.SubElement(channel, 'lastBuildDate').text = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')

    media_map = get_media_map(tweets.get("includes", {}))

    for tweet in tweets["data"]:
        tweet_text = tweet["text"]
        tweet_url = f'https://x.com/{username}/status/{tweet["id"]}'
        pub_date = date_parser.parse(tweet["created_at"]).strftime('%a, %d %b %Y %H:%M:%S GMT')

        description_html = format_entities(tweet, media_map)

        item = ET.SubElement(channel, 'item')
        # ET.SubElement(item, 'title').text = tweet_text
        ET.SubElement(item, 'title').text = description_html
        desc = ET.SubElement(item, 'description')
        desc.text = ET.CDATA(description_html)
        ET.SubElement(item, 'pubDate').text = pub_date
        ET.SubElement(item, 'guid').text = tweet_url
        ET.SubElement(item, 'link').text = tweet_url

    return ET.ElementTree(rss)

def save_rss(tree, filename):
    with open(filename, 'wb') as f:
        tree.write(f, pretty_print=True, xml_declaration=True, encoding='utf-8')

if __name__ == '__main__':
    tweets = get_user_tweets(USER_ID)
    rss_tree = create_rss_feed(tweets, USERNAME)
    save_rss(rss_tree, RSS_FILE)
    print(f"✅ RSS feed saved to {RSS_FILE}")