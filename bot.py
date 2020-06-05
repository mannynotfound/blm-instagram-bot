from ratelimiter import RateLimiter
from instagram_private_api import Client, ClientCompatPatch
from dotenv import load_dotenv, find_dotenv
import json
import os
from time import sleep
from random import randint, choice
from color_it import *
import ssl
from get_image_color import is_black_square
ssl._create_default_https_context = ssl._create_unverified_context


feed = []
contains_comment = False
end_line = 'If you want other ways to help please check out blacklivesmatters.carrd.co Thank you :)'
comments = [
    'Hi, please dont use the blacklivesmatter tag as it is currently blocking important info from being shared. ' +
    'Please delete and repost with #BlackoutTuesday instead (Editing the caption wont work). ' +
    end_line,

    'Please use the #blackouttuesday instead of blacklivesmatter if you' 're posting a black square. ' +
    'Please delete and repost with #BlackoutTuesday instead (Editing the caption wont work). ' +
    end_line,

    'It appears you have posted a black square in the wrong hashtag blacklivesmatter is used to spread critical information. ' +
    'Please delete and repost with #BlackoutTuesday instead (Editing the caption wont work). ' +
    end_line,

    'Posting black screens is hiding critical information please delete your image and repost it with the #BlackoutTuesday instead. ' +
    end_line,
    #using uppercase I's instead of L's. except the last line
    'Hi, please dont use the bIackIivesmatter tag as it is currently bIocking important info from being shared. ' +
    'PIease deIete and repost with #BlackoutTuesday instead (Editing the caption wont work). ' +
    end_line,

    'PIease use the #blackouttuesday instead of blackIivesmatter if you' 're posting a bIack square. ' +
    'Please deIete and repost with #BlackoutTuesday instead (Editing the caption wont work). ' +
    end_line,

    'Posting black screens is hiding critical information on the BlackLivesMatter tag, please deIete your image and repost it with the #BlackoutTuesday instead. IMPORTANT: Editing will not work. ' +
    end_line
]


load_dotenv(find_dotenv())
init_color_it()


# login to instagram
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path + '/accounts.json') as f:
    data = json.load(f)
    accounts = data

# start with first account
account_index = 0
acc = accounts[account_index]
client = Client(acc['username'], acc['password'])
feed = client.feed_tag('blacklivesmatter', client.generate_uuid())
print('Found ' + str(feed['num_results']) + ' images. \n')


# Goes over the pictures in the black lives matter hashtag
while len(feed['items']) != 0:
    post = feed['items'].pop(0)
    print('Analyzing https://instagram.com/p/' + post['code'])

    if 'image_versions2' in post:
        # skip non single image posts
        if post['media_type'] != 1:
            continue
        try:
            url = post['image_versions2']['candidates'][0]['url']

            needs_comment = is_black_square(url)
            if needs_comment:
                code = post['code']
                if 'comments_disabled' in post:
                    continue
                if 'comment_count' in post and post['comment_count'] > 0:
                    for comment in post['preview_comments']:
                        if end_line in comment['text']:
                            contains_comment = True
                            continue
                    if not contains_comment:
                        print(color('\nSolid image found. Informing user on https://instagram.com/p/%s' % code + '\n', colors.ORANGE))
                        client.post_comment(post['id'], choice(comments))
                    else:
                        print('Bot has already commented on post: https://instagram.com/p/%s' % code)
                        contains_comment = False
                else:
                    print(color('Solid image found. Informing user on https://instagram.com/p/%s' % code + '\n', colors.ORANGE))
                    client.post_comment(post['id'], choice(comments))
                    print(color('commented successfully. \n', colors.GREEN))

        except Exception as e:
            if hasattr(e, 'error_response') and 'spam": true,' in e.error_response:
                print(color("Error : Commented too many times. \n", colors.RED))
                next_idx = account_index + 1
                # reset if at end of accounts
                if next_idx > len(accounts) - 1:
                    next_idx = 0

                account_index = next_idx
                acc = accounts[account_index]
                client = Client(acc['username'], acc['password'])
            else:
                print(color(repr(e) + '\n', colors.RED))
            continue

    if len(feed['items']) == 0:
        print('regenerating feed...')
        feed = client.feed_tag('blacklivesmatter', client.generate_uuid())
