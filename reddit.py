import praw
import json
from praw.reddit import Submission
import requests
from datetime import date
from audio import generate_audio
import os
from Naked.toolshed.shell import execute
import re

import mysql.connector


mydb = mysql.connector.connect(
  host="5.189.176.126",
  user="admin",
  password="CMFB8LXQG7ADF2b",
  database="reddit_shorts"
)

client_id  = ""
secret_key = ""
reddit = praw.Reddit(
    client_id=client_id,
    client_secret=secret_key,
    password="",
    user_agent="testbot/0.0.1-alpha",
    username="",
)

# Get subreddit posts in list 
def get_subreddit(subreddit, postnumb, top):
    posts = []
    # count sticky posts
    stickied_post = []
    stickied_comment = []
    sticky = reddit.subreddit(subreddit).hot(limit=postnumb)
    for post in sticky:
        if post.stickied:
            stickied_post.append(post.id)
    if top == "hot":
        hot_cat = reddit.subreddit(subreddit).hot(limit=postnumb+len(stickied_post))
    elif top == "top":
        hot_cat = reddit.subreddit(subreddit).top("all", limit=postnumb+len(stickied_post))
    else:
        hot_cat = reddit.subreddit(subreddit).hot(limit=postnumb+len(stickied_post))
    for cat in hot_cat:
        if cat.stickied:
            continue
        comments = []
        cat.comments.replace_more(limit=1)
        for commentold in cat.comments:
            if commentold.author is None :
                author   = "anonymous"
            else:
                author   = commentold.author.name
            if commentold.stickied:
                continue
            comments.append({
                'id':       commentold.id,
                'score':    commentold.score,
                'body':     commentold.body,
                'body_html':commentold.body_html,
                'author':   author
        })
        author = ""
        if cat.author is None:
            author = "anonymous"
        else: 
            author = cat.author.name
        posts.append({
            'id':           cat.id,
            'title':        cat.title,
            'content':      cat.selftext,
            'content_html': cat.selftext_html,
            'score':        cat.score,
            'subreddit':    cat.subreddit_name_prefixed,
            'author':       "u/{}".format(author),
            'comments':     comments
        })
    return posts

# get comment in list of sub sentences of the comment
def get_comment(id):
    comment = reddit.comment(id)
    author = ""
    if comment.author is None:
        author = "anonymous"
    else: 
        author = comment.author.name
    post_date = date.fromtimestamp(comment.created_utc)
    now = date.today()
    diff = now - post_date
    sentences = comment.body.strip()
    d = "."
    # sentences =  [e+d for e in sentences.split(d) if e]
    sentences =  [(e+d).strip() for e in sentences.split(d) if e]
    for s in sentences:
        # if not re.match("[a-zA-Z0-9]", s):
        #     sentences.remove(s)
        if len(s)<3:
            sentences.remove(s)
            continue
        if not any(c.isalpha() for c in s):
            sentences.remove(s)
            continue
    comment_content = []
    originals = []
    old = ""
    comments = []
    
    for sentence in sentences:
        comment_content.append("{} {}".format(old, sentence))
        originals.append(sentence)
        if len(old + sentence) > 700:
                old = ""
        else: 
            old = old + sentence
    count = 0
    for comment_line in comment_content:
        comments.append({
                'id':       comment.id,
                'score':    comment.score,
                'sentence': originals[count],
                'body':     comment_line,
                'fullcontent': comment.body,
                'author':   author, 
                'created':  diff.days,
                'ups':  comment.ups
        })
        count = count + 1
    return comments

# get post/submission 
def get_submission(id):
    posts = []
    submission = reddit.submission(id)
    title = submission.title
    author = ""
    if submission.author is None:
        author = "anonymous"
    else: 
        author = submission.author.name
    sentences = submission.selftext.strip()
    post_date = date.fromtimestamp(submission.created_utc)
    now = date.today()
    diff = now - post_date
    if sentences:
        d = "."
        sentences =  [(e+d).strip() for e in sentences.split(d) if e]
        for s in sentences:
            # if not re.match("[a-zA-Z0-9]", s):
            #     sentences.remove(s)
            if len(s)<3:
                sentences.remove(s)
                continue
            if not any(c.isalpha() for c in s):
                sentences.remove(s)
                continue
        submission_content = []
        old = ""
        originals = []
        submissions = []
        for sentence in sentences:
            submission_content.append("{} {}".format(old, sentence))
            
            originals.append(sentence)
            if len(old + sentence) > 700:
                old = ""
            else: 
                old = old + sentence
        count = 0
        for submission_line in submission_content:
            submissions.append({
                'id':               submission.id,
                'title':            submission.title,
                'sentence':         originals[count],
                'content':          submission_line,
                'fullcontent':      submission.selftext,
                'fullcontent_html': submission.selftext_html,
                'score':            submission.score,
                'subreddit':        submission.subreddit_name_prefixed,
                'created':          diff.days,
                'author':           "u/{}".format(author),
                
            })
            count = count + 1
        return {'isTitleOnly': False, "title":title ,"submissions": submissions}


    return {'isTitleOnly': True, "submissions":{
        'id':           submission.id,
        'title':        submission.title,
        'content':      submission.selftext,
        'score':        submission.score,
        'subreddit':    submission.subreddit_name_prefixed,
        'created':      diff.days,
        'author':       "u/{}".format(author),
    }}

# get post with limited number of comments
def get_submissions_ids(subreddit, postnumb, top, comment_num):
    submissions = get_subreddit(subreddit, postnumb+100, top)
    
    posts = []
    for submission in submissions:
        if len(posts) == postnumb:
            break
        mycursor = mydb.cursor(buffered=True)
        mycursor.execute("SELECT id FROM posts WHERE post_id = '{}'".format(submission['id']))
        row_count = mycursor.rowcount
        if row_count != 0:
            continue
        comments_id     = []
        for comment in submission['comments']:
            if len(comments_id) < comment_num :
                comments_id.append(comment['id'])
            else:
                break
        title = submission['title']
        title = title.replace('/', " ")
        title = title.replace('\\', " ")
        posts.append({
            "submission_id": submission['id'],
            "submission_comments_ids": comments_id,
            "submission_title": title
        })
    return posts   
            

def insert_vid(video_id):
    mycursor        = mydb.cursor()
    sql = "INSERT INTO videos (video) VALUES ('{}')".format(video_id)
    mycursor.execute(sql)
    mydb.commit()
    return mycursor.rowcount

def insert_comment(comment_id):
    mycursor        = mydb.cursor()
    sql = "INSERT INTO comments (comment_id) VALUES ('{}')".format(comment_id)
    mycursor.execute(sql)
    mydb.commit()
    return mycursor.rowcount

def insert_post(post_id):
    mycursor        = mydb.cursor()
    sql = "INSERT INTO posts (post_id) VALUES ('{}')".format(post_id)
    mycursor.execute(sql)
    mydb.commit()
    return mycursor.rowcount
