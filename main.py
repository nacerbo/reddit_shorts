from generate import generator
import sys
from time import sleep

subreddit       = sys.argv[1]
posts_number    = int(sys.argv[2])
comments_numb   = int(sys.argv[3])
top             = "hot"
counter = 0

while True:
    try :
        generator(subreddit, posts_number, top, comments_numb)
        counter = counter + 1
        # if counter % 10 == 0:
        #     sleep(180) #1800 ,3600, 7200
    except:
        print("there was an error")
        # sleep(1800) #1800 ,3600, 7200