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
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'wb') as f:
        tree.write(f, pretty_print=True, xml_declaration=True, encoding='utf-8')

if __name__ == '__main__':
    # tweets = get_user_tweets(USER_ID)
    tweets = {
    "data": [
        {
            "text": "🎓🎉 Congratulations, Dr. Zhao! We’re celebrating @Pengfei_Zhao_  on her successful dissertation defense. We’re so proud of you at the SML, and will miss you dearly! https://t.co/yr1mAuBOfd",
            "entities": {
                "annotations": [
                    {
                        "start": 24,
                        "end": 27,
                        "probability": 0.5404,
                        "type": "Other",
                        "normalized_text": "Zhao"
                    },
                    {
                        "start": 133,
                        "end": 135,
                        "probability": 0.6116,
                        "type": "Organization",
                        "normalized_text": "SML"
                    }
                ],
                "mentions": [
                    {
                        "start": 48,
                        "end": 62,
                        "username": "Pengfei_Zhao_",
                        "id": "1250120269978451968"
                    }
                ],
                "urls": [
                    {
                        "start": 164,
                        "end": 187,
                        "url": "https://t.co/yr1mAuBOfd",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1925546186385322257/photo/1",
                        "display_url": "pic.x.com/yr1mAuBOfd",
                        "media_key": "3_1925244185667399680"
                    },
                    {
                        "start": 164,
                        "end": 187,
                        "url": "https://t.co/yr1mAuBOfd",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1925546186385322257/photo/1",
                        "display_url": "pic.x.com/yr1mAuBOfd",
                        "media_key": "3_1925244198984294400"
                    },
                    {
                        "start": 164,
                        "end": 187,
                        "url": "https://t.co/yr1mAuBOfd",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1925546186385322257/photo/1",
                        "display_url": "pic.x.com/yr1mAuBOfd",
                        "media_key": "3_1925244206727024640"
                    },
                    {
                        "start": 164,
                        "end": 187,
                        "url": "https://t.co/yr1mAuBOfd",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1925546186385322257/photo/1",
                        "display_url": "pic.x.com/yr1mAuBOfd",
                        "media_key": "3_1925244217682501632"
                    }
                ]
            },
            "attachments": {
                "media_keys": [
                    "3_1925244185667399680",
                    "3_1925244198984294400",
                    "3_1925244206727024640",
                    "3_1925244217682501632"
                ]
            },
            "edit_history_tweet_ids": [
                "1925546186385322257"
            ],
            "id": "1925546186385322257",
            "author_id": "132922064",
            "created_at": "2025-05-22T13:36:00.000Z"
        },
        {
            "text": "🎉 Congratulations to SML Ph.D. student @bae_inhwan on receiving the 2024-25 PCCW Frank H.T. Rhodes Mission Grant! 🌟 Her project focuses on combating online toxicity against women and nonbinary persons with tailored persuasion messages using large language models.",
            "entities": {
                "annotations": [
                    {
                        "start": 21,
                        "end": 28,
                        "probability": 0.4394,
                        "type": "Organization",
                        "normalized_text": "SML Ph.D"
                    },
                    {
                        "start": 81,
                        "end": 111,
                        "probability": 0.6925,
                        "type": "Other",
                        "normalized_text": "Frank H.T. Rhodes Mission Grant"
                    }
                ],
                "mentions": [
                    {
                        "start": 39,
                        "end": 50,
                        "username": "bae_inhwan",
                        "id": "1533376662976745472"
                    }
                ]
            },
            "edit_history_tweet_ids": [
                "1910701874686144596"
            ],
            "id": "1910701874686144596",
            "author_id": "132922064",
            "created_at": "2025-04-11T14:30:00.000Z"
        },
        {
            "text": "SML members @bae_inhwan @isabellemcdaph @haesooheatherk and Julia Sebastien had a lovely meeting with the students @btf_bluetree about youth social media safety! It was great to chat, @ParkChanJun_ , thank you for inviting us! #bluetreefoundation",
            "entities": {
                "hashtags": [
                    {
                        "start": 227,
                        "end": 246,
                        "tag": "bluetreefoundation"
                    }
                ],
                "annotations": [
                    {
                        "start": 0,
                        "end": 2,
                        "probability": 0.5565,
                        "type": "Organization",
                        "normalized_text": "SML"
                    },
                    {
                        "start": 60,
                        "end": 74,
                        "probability": 0.6971,
                        "type": "Person",
                        "normalized_text": "Julia Sebastien"
                    }
                ],
                "mentions": [
                    {
                        "start": 12,
                        "end": 23,
                        "username": "bae_inhwan",
                        "id": "1533376662976745472"
                    },
                    {
                        "start": 24,
                        "end": 39,
                        "username": "isabellemcdaph",
                        "id": "253745895"
                    },
                    {
                        "start": 40,
                        "end": 55,
                        "username": "haesooheatherk",
                        "id": "1089674299861012486"
                    },
                    {
                        "start": 115,
                        "end": 128,
                        "username": "btf_bluetree",
                        "id": "237499826"
                    },
                    {
                        "start": 184,
                        "end": 197,
                        "username": "ParkChanJun_",
                        "id": "898837538747502593"
                    }
                ]
            },
            "edit_history_tweet_ids": [
                "1896556918576922773"
            ],
            "id": "1896556918576922773",
            "author_id": "132922064",
            "created_at": "2025-03-03T13:43:00.000Z"
        },
        {
            "text": "We are excited to welcome Han Li, @HanLi_1231  to SML! Han joined our collaborative project on \"Deterring Objectionable Behaviors Online,\" https://t.co/h4T2TGQS5B  She comes to us after her postdoc at the NUS where she worked with Dr. Renwen Zhang (@renwenzhang). Welcome, Han! https://t.co/SRhPmI1Nu4",
            "entities": {
                "annotations": [
                    {
                        "start": 26,
                        "end": 31,
                        "probability": 0.5897,
                        "type": "Person",
                        "normalized_text": "Han Li"
                    },
                    {
                        "start": 50,
                        "end": 52,
                        "probability": 0.4111,
                        "type": "Organization",
                        "normalized_text": "SML"
                    },
                    {
                        "start": 96,
                        "end": 135,
                        "probability": 0.7955,
                        "type": "Other",
                        "normalized_text": "Deterring Objectionable Behaviors Online"
                    },
                    {
                        "start": 235,
                        "end": 246,
                        "probability": 0.6203,
                        "type": "Other",
                        "normalized_text": "Renwen Zhang"
                    },
                    {
                        "start": 273,
                        "end": 275,
                        "probability": 0.5441,
                        "type": "Person",
                        "normalized_text": "Han"
                    }
                ],
                "mentions": [
                    {
                        "start": 34,
                        "end": 45,
                        "username": "HanLi_1231",
                        "id": "1580054223420432384"
                    },
                    {
                        "start": 249,
                        "end": 261,
                        "username": "renwenzhang",
                        "id": "2692945104"
                    }
                ],
                "urls": [
                    {
                        "start": 139,
                        "end": 162,
                        "url": "https://t.co/h4T2TGQS5B",
                        "expanded_url": "https://socialsciences.cornell.edu/deterring-objectionable-behavior-online",
                        "display_url": "socialsciences.cornell.edu/deterring-obje…",
                        "status": 200,
                        "title": "Deterring Objectionable Behavior Online | Cornell Center for Social Sciences",
                        "description": "People encounter all kinds of objectionable content online -- misinformation, hate speech, conspiracies, bullying -- things they wish another person wouldn’t say or repeat. They are thus inclined to “object.” But what is the effective way to do so, particularly with so many others watching? What kinds of objectio ns, or other behaviors, have the desired effect of reducing this kind of speech. Our project involves addressing this problem from multiple angles: from observation of the real world to experiment",
                        "unwound_url": "https://socialsciences.cornell.edu/deterring-objectionable-behavior-online"
                    },
                    {
                        "start": 278,
                        "end": 301,
                        "url": "https://t.co/SRhPmI1Nu4",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1894397692035416123/photo/1",
                        "display_url": "pic.x.com/SRhPmI1Nu4",
                        "media_key": "3_1892268894959616000"
                    }
                ]
            },
            "attachments": {
                "media_keys": [
                    "3_1892268894959616000"
                ]
            },
            "edit_history_tweet_ids": [
                "1894397692035416123"
            ],
            "id": "1894397692035416123",
            "author_id": "132922064",
            "created_at": "2025-02-25T14:43:00.000Z"
        },
        {
            "text": "Our Ph.D. student @haesooheatherk represented the SML at the UN’s 63rd Session of the Commission for Social Development! Invited by @btf_bluetree, she spoke on what academic research can do to build a safer online future. #BTF https://t.co/lnsgz4VDtM https://t.co/D9xwUNvC4m",
            "entities": {
                "hashtags": [
                    {
                        "start": 222,
                        "end": 226,
                        "tag": "BTF"
                    }
                ],
                "annotations": [
                    {
                        "start": 50,
                        "end": 52,
                        "probability": 0.4039,
                        "type": "Organization",
                        "normalized_text": "SML"
                    },
                    {
                        "start": 61,
                        "end": 62,
                        "probability": 0.4984,
                        "type": "Organization",
                        "normalized_text": "UN"
                    }
                ],
                "mentions": [
                    {
                        "start": 18,
                        "end": 33,
                        "username": "haesooheatherk",
                        "id": "1089674299861012486"
                    },
                    {
                        "start": 132,
                        "end": 145,
                        "username": "btf_bluetree",
                        "id": "237499826"
                    }
                ],
                "urls": [
                    {
                        "start": 227,
                        "end": 250,
                        "url": "https://t.co/lnsgz4VDtM",
                        "expanded_url": "https://webtv.un.org/en/asset/k1t/k1tbxblcyi",
                        "display_url": "webtv.un.org/en/asset/k1t/k…",
                        "images": [
                            {
                                "url": "https://pbs.twimg.com/news_img/1892203411858227200/cXH5ZdRq?format=jpg&name=orig",
                                "width": 564,
                                "height": 317
                            },
                            {
                                "url": "https://pbs.twimg.com/news_img/1892203411858227200/cXH5ZdRq?format=jpg&name=150x150",
                                "width": 150,
                                "height": 150
                            }
                        ],
                        "status": 200,
                        "title": "Beyond Access: Youth Online Safety and Digital Equity - CSocD63 Side Event",
                        "description": "This side event of the 63rd Session of the Commission For Social Development will explore concrete and practical solutions to bridge the digital divide that directly impacts youth safety, well-being, and rights.",
                        "unwound_url": "https://webtv.un.org/en/asset/k1t/k1tbxblcyi"
                    },
                    {
                        "start": 251,
                        "end": 274,
                        "url": "https://t.co/D9xwUNvC4m",
                        "expanded_url": "https://x.com/CUSocialMedia/status/1892203366509363475/photo/1",
                        "display_url": "pic.x.com/D9xwUNvC4m",
                        "media_key": "3_1892203358628282368"
                    }
                ]
            },
            "attachments": {
                "media_keys": [
                    "3_1892203358628282368"
                ]
            },
            "edit_history_tweet_ids": [
                "1892203366509363475"
            ],
            "id": "1892203366509363475",
            "author_id": "132922064",
            "created_at": "2025-02-19T13:23:32.000Z"
        }
    ],
    "includes": {
        "media": [
            {
                "url": "https://pbs.twimg.com/media/GrfXYvCXcAAxeJ3.jpg",
                "media_key": "3_1925244185667399680",
                "type": "photo"
            },
            {
                "url": "https://pbs.twimg.com/media/GrfXZgpXIAAcpHM.jpg",
                "media_key": "3_1925244198984294400",
                "type": "photo"
            },
            {
                "url": "https://pbs.twimg.com/media/GrfXZ9fX0AAy9ai.jpg",
                "media_key": "3_1925244206727024640",
                "type": "photo"
            },
            {
                "url": "https://pbs.twimg.com/media/GrfXamTXIAAkvgE.jpg",
                "media_key": "3_1925244217682501632",
                "type": "photo"
            },
            {
                "url": "https://pbs.twimg.com/media/GkKwiMeWwAAk1Us.jpg",
                "media_key": "3_1892268894959616000",
                "type": "photo"
            },
            {
                "url": "https://pbs.twimg.com/media/GkJ07enXAAAP8w6.jpg",
                "media_key": "3_1892203358628282368",
                "type": "photo"
            }
        ]
    },
    "meta": {
        "next_token": "7140dibdnow9c7btw4b3nqb5tsik6b7b1w65djxl05jqt",
        "result_count": 5,
        "newest_id": "1925546186385322257",
        "oldest_id": "1892203366509363475"
    }
}
    rss_tree = create_rss_feed(tweets, USERNAME)
    save_rss(rss_tree, RSS_FILE)
    print(f"✅ RSS feed saved to {RSS_FILE}")