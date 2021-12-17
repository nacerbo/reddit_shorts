from reddit import get_comment, get_submission, get_subreddit
from audio import generate_audio
from Naked.toolshed.shell import execute
import os


def take_screenshot_comment(post_id, id):
    if not os.path.exists("./audio/post/{}/comment/{}".format(post_id, id)):
        os.makedirs("./audio/post/{}/comment/{}".format(post_id, id))
    comment = get_comment(id)
    myrange = list(range(len(comment)))
    for i in myrange:
        index = str(i)
        generate_audio(comment[i]['sentence'], './audio/post/{}/comment/{}/{}.wav'.format(post_id, id, index.zfill(5)))
        url = 'http://localhost:5000/comments/{}/{}'.format(id, index.zfill(5))
        success = execute("/home/nacerbo/.nvm/versions/node/v16.6.1/bin/node screenshot.js '{}' post/{}/comment {} {}".format(url, post_id, id, index.zfill(5)))
        size = os.stat('./audio/post/{}/comment/{}/{}.wav'.format(post_id, id, index.zfill(5))).st_size
        if size < 600:
            os.remove('./audio/post/{}/comment/{}/{}.wav'.format(post_id, id, index.zfill(5)))
            os.remove('./audio/post/{}/comment/{}/{}.png'.format(post_id, id, index.zfill(5)))
            i = i -1
            myrange.pop(-1)
            pass

def take_screenshot_submission(id):
    if not os.path.exists('./audio/post/{}'.format(id)):
        os.makedirs('./audio/post/{}'.format(id))
        os.makedirs('./audio/post/{}/comment'.format(id))
    submission = get_submission(id)
    if submission['isTitleOnly']:
        generate_audio(submission['submissions']['title'], './audio/post/{}/title.wav'.format(id))
        url = 'http://localhost:5000/post/{}/title'.format(id)
        success = execute("/home/nacerbo/.nvm/versions/node/v16.6.1/bin/node screenshot.js '{}' post {} title".format(url, id))
        size = os.stat('./audio/post/{}/title.wav'.format(id)).st_size
        if size < 600:
            os.remove('./audio/post/{}/title.wav'.format(id))
    else:
        generate_audio(submission['submissions'][0]['title'], './audio/post/{}/title.wav'.format(id))
        url = 'http://localhost:5000/post/{}/title'.format(id)
        success = execute("/home/nacerbo/.nvm/versions/node/v16.6.1/bin/node screenshot.js '{}' post {} title".format(url, id))
        size = os.stat('./audio/post/{}/title.wav'.format(id)).st_size
        if size < 600:
            os.remove('./audio/post/{}/title.wav'.format(id))
        myrange = list(range(len(submission['submissions'])))
        for i in range(len(submission['submissions'])):
            index = str(i)
            generate_audio(submission['submissions'][i]['sentence'], './audio/post/{}/{}.wav'.format(id, index.zfill(5)))
            url = 'http://localhost:5000/post/{}/{}'.format(id, index.zfill(5))
            success = execute("/home/nacerbo/.nvm/versions/node/v16.6.1/bin/node screenshot.js '{}' post {} {}".format(url, id, index.zfill(5)))
            size = os.stat('./audio/post/{}/{}.wav'.format(id, index.zfill(5))).st_size
            if size < 600:
                os.remove('./audio/post/{}/{}.wav'.format(id, index.zfill(5)))
                os.remove('./audio/post/{}/{}.png'.format(id, index.zfill(5)))
                i = i -1
                myrange.pop(-1)
                

def take_screenshot(content_type, post_id, id):
    if content_type == "submission":
        take_screenshot_submission(id)
    elif content_type =="comment":
        take_screenshot_comment(post_id, id)

# debug
# post id
# id = "p1lqa1"
# comment id
# id = "h8cu5o7"
# content_type = 'comment'
# take_screenshot(content_type, id)
