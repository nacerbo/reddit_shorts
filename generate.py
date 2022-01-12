from reddit import get_comment, get_submission, get_subreddit, get_submissions_ids
from reddit import insert_vid, insert_post, insert_comment
from screenshots import take_screenshot
import ffmpeg
import glob
import os
import mysql.connector

mydb = mysql.connector.connect(
  host="",
  user="",
  password="",
  database=""
)

# generate submission video
def generate_submission(id):
    # make the png files and audio files
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT id FROM posts WHERE post_id = '{}'".format(id))
    row_count = mycursor.rowcount
    if row_count == 0:
        print('taking screenshot ', id)
        insert_post(id)
        take_screenshot('submission', id, id)
        # get all images and audio files from the submission folder
        images = glob.glob("./audio/post/{}/*.png".format(id))
        audio = glob.glob("./audio/post/{}/*.wav".format(id))
        # make sure the vid subfolder exists
        if not os.path.exists('./audio/post/{}/vid'.format(id)):
            os.makedirs('./audio/post/{}/vid'.format(id))

        images = [image.replace("./audio/post/{}/".format(id), '') for image in images]
        images = [image.replace('.png', '') for image in images]
        images.sort()
        if 'title' in images:
            images.sort()
            images.insert(0,'title')
            images.pop(-1)


        for image in images:
            audio_input = (ffmpeg.input("./audio/post/{}/{}.wav".format(id, image)))
            probe = ffmpeg.probe("./audio/post/{}/{}.wav".format(id, image))
            singlePart = probe["streams"][0]['duration']
            singlePart = round(float(singlePart))
            image_input = (ffmpeg.input("./audio/post/{}/{}.png".format(id, image), loop=1, t=singlePart).filter('scale', '800x1280'))
            (
                ffmpeg
                .output(audio_input, image_input, "./audio/post/{}/vid/{}.mp4".format(id, image), pix_fmt='yuv420p', format='mp4', s="800x1280")
                .run(overwrite_output=True)
            )


        videos = []
        for image in images:
            videos.append(ffmpeg.input("./audio/post/{}/vid/{}.mp4".format(id, image)))

        audios = []
        for image in images:
            audios.append(ffmpeg.input("./audio/post/{}/{}.wav".format(id, image)).audio)


        (
            ffmpeg.concat(*videos, v=1, a=0, unsafe=1)
            .output("./audio/post/{}/final.mp4".format(id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )


        (
            ffmpeg.concat(*audios, v=0, a=1, unsafe=1)
            .output("./audio/post/{}/final.wav".format(id))
            .run(overwrite_output=True)
        )


        (
            ffmpeg.concat(ffmpeg.input("./audio/post/{}/final.mp4".format(id)), ffmpeg.input("./audio/post/{}/final.wav".format(id)), v=1, a=1, unsafe=1)
            .output("./audio/post/{}/{}.mp4".format(id, id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )

# generate comment video 
def generate_comment(id, post_id):
    # make the png files and audio files
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT id FROM comments WHERE comment_id = '{}'".format(id))
    row_count = mycursor.rowcount
    if row_count == 0:
        print('taking screenshot {} - comment - {}'.format(post_id, id))
        insert_comment(id)
        take_screenshot('comment', post_id, id)
        # get all images and audio files from the comment folder
        images = glob.glob("./audio/post/{}/comment/{}/*.png".format(post_id, id))
        audio = glob.glob("./audio/post/{}/comment/{}/*.wav".format(post_id, id))
        # make sure the vid subfolder exists
        if not os.path.exists('./audio/post/{}/comment/{}/vid'.format(post_id, id)):
            os.makedirs('./audio/post/{}/comment/{}/vid'.format(post_id, id))

        images = [image.replace("./audio/post/{}/comment/{}/".format(post_id, id), '') for image in images]
        images = [image.replace('.png', '') for image in images]
        images.sort()
        if 'title' in images:
            images.sort()
            images.insert(0,'title')
            images.pop(-1)

        for image in images:
            audio_input = (ffmpeg.input("./audio/post/{}/comment/{}/{}.wav".format(post_id, id,image)))
            probe = ffmpeg.probe("./audio/post/{}/comment/{}/{}.wav".format(post_id, id, image))
            singlePart = probe["streams"][0]['duration']
            singlePart = round(float(singlePart))
            image_input = (ffmpeg.input("./audio/post/{}/comment/{}/{}.png".format(post_id, id, image), loop=1, t=singlePart).filter('scale', '800x1280'))
            (
                ffmpeg
                .output(audio_input, image_input, "./audio/post/{}/comment/{}/vid/{}.mp4".format(post_id, id, image), pix_fmt='yuv420p', format='mp4', s="800x1280")
                .run(overwrite_output=True)
            )


        videos = []
        for image in images:
            videos.append(ffmpeg.input("./audio/post/{}/comment/{}/vid/{}.mp4".format(post_id, id, image)))

        audios = []
        for image in images:
            audios.append(ffmpeg.input("./audio/post/{}/comment/{}/{}.wav".format(post_id, id, image)).audio)


        (
            ffmpeg.concat(*videos, v=1, a=0, unsafe=1)
            .output("./audio/post/{}/comment/{}/final.mp4".format(post_id, id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )


        (
            ffmpeg.concat(*audios, v=0, a=1, unsafe=1)
            .output("./audio/post/{}/comment/{}/final.wav".format(post_id, id))
            .run(overwrite_output=True)
        )


        (
            ffmpeg.concat(ffmpeg.input("./audio/post/{}/comment/{}/final.mp4".format(post_id, id)), ffmpeg.input("./audio/post/{}/comment/{}/final.wav".format(post_id, id)), v=1, a=1, unsafe=1)
            .output("./audio/post/{}/comment/{}/{}.mp4".format(post_id, id, id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )

def generate_vid(submission_id, comment_ids):
    video_id =  submission_id + " - " + " - ".join(comment_ids)
    mycursor = mydb.cursor(buffered=True)
    mycursor.execute("SELECT id FROM videos WHERE video = '{}'".format(video_id))
    row_count = mycursor.rowcount
    if row_count == 0:
        insert_vid(video_id)
        ffmpeg_audio_inputs = []
        ffmpeg_inputs = []
        ffmpeg_inputs.append(ffmpeg.input("./audio/post/{}/{}.mp4".format(submission_id, submission_id)))
        ffmpeg_audio_inputs.append(ffmpeg.input("./audio/post/{}/final.wav".format(submission_id)))
        for comment_id in comment_ids:
            ffmpeg_inputs.append(ffmpeg.input("./audio/post/{}/comment/{}/{}.mp4".format(submission_id, comment_id, comment_id)))
            ffmpeg_audio_inputs.append(ffmpeg.input("./audio/post/{}/comment/{}/final.wav".format(submission_id, comment_id)))
        # geenarete the vid with comments but without audio
        (
            ffmpeg.concat(*ffmpeg_inputs, v=1, a=0, unsafe=1)
            .output("./audio/post/{}/temp.mp4".format(submission_id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )
        # generate the final audio file without video
        (
            ffmpeg.concat(*ffmpeg_audio_inputs, v=0, a=1, unsafe=1)
            .output("./audio/post/{}/temp.wav".format(submission_id))
            .run(overwrite_output=True)
        )

        if not os.path.exists('./videos/{}'.format(submission_id)):
            os.makedirs('./videos/{}/'.format(submission_id))
        # generate the final video with comments audio and video 
        (
            ffmpeg.concat(ffmpeg.input("./audio/post/{}/temp.mp4".format(submission_id)), ffmpeg.input("./audio/post/{}/temp.wav".format(submission_id)), v=1, a=1, unsafe=1)
            .output("./videos/{}/{}.mp4".format(submission_id, submission_id), pix_fmt='yuv420p', format='mp4', s="800x1280")
            .run(overwrite_output=True)
        )
    return video_id


def generate_story(submission_ids, video_id):
    # list of temp files audio and videos
    ffmpeg_inputs = []
    ffmpeg_audio_inputs = []
    for submission_id in submission_ids:
        ffmpeg_inputs.append(ffmpeg.input("./audio/post/{}/temp.mp4".format(submission_id)))
        ffmpeg_audio_inputs.append(ffmpeg.input("./audio/post/{}/temp.wav".format(submission_id)))


    
    # geenarete the vid with comments but without audio
    (
        ffmpeg.concat(*ffmpeg_inputs, v=1, a=0, unsafe=1)
        .output("./videos/{}/temp.mp4".format(submission_id), pix_fmt='yuv420p', format='mp4', s="800x1280")
        .run(overwrite_output=True)
    )
    # generate the final audio file without video
    (
        ffmpeg.concat(*ffmpeg_audio_inputs, v=0, a=1, unsafe=1)
        .output("./videos/{}/temp.wav".format(submission_id))
        .run(overwrite_output=True)
    )
    
    (
        ffmpeg.concat(ffmpeg.input("./videos/{}/temp.mp4".format(submission_id)), ffmpeg.input("./videos/{}/temp.wav".format(submission_id)), v=1, a=1, unsafe=1)
        .output("./videos/{}.mp4".format(video_id), pix_fmt='yuv420p', format='mp4', s="800x1280")
        .run(overwrite_output=True)
    )



def generator(subreddit, posts_number, top, comments_numb):
    print("script started please wait ...")
    posts = get_submissions_ids(subreddit, posts_number, top, comments_numb)
    posts_ids = []
    for pid in posts:
        posts_ids.append(pid["submission_id"])

    # vid_id = " - ".join(posts_ids)
    vid_id = posts[0]["submission_title"][:99]
    ids = []
    for post in posts:
        # print(get_submission(post['submission_id']))
        ids.append(post['submission_id'])
        generate_submission(post['submission_id'])
        for comment in post['submission_comments_ids']:
            generate_comment(comment, post['submission_id'])

        generate_vid(post['submission_id'], post['submission_comments_ids'])

    generate_story(ids, vid_id)
