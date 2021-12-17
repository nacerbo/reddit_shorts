from flask import Flask, request, render_template, send_from_directory
from flask_restful import Resource, Api
from praw.models.listing.mixins import submission
from reddit import get_subreddit, get_comment, get_submission
import json
import requests
import os
from flask_autoindex import AutoIndex

app = Flask(__name__, template_folder='templates')
AutoIndex(app, browse_root=os.path.curdir+"/videos")
api = Api(app)
# set up the json APIs for better controle later
# return the posts for subreddit
class SubRedditAPI(Resource):
    def get(self, subreddit, numb, top):
        posts = get_subreddit(subreddit, numb, top)
        return posts

api.add_resource(SubRedditAPI, '/<subreddit>/<top>/<int:numb>')

# return the comment by id
class CommentAPI(Resource):
    def get(self, id):
        comment = get_comment(id)
        return comment

api.add_resource(CommentAPI, '/comment/<id>')
# return section of commnet by id and index (pagination of the comment)
class CommentAPIPagenation(Resource):
    def get(self, id, index):
        comment = get_comment(id)
        if len(comment) >=  index:
            return {"error": "the index is too big try lower"}
        else:
            return comment[index]

api.add_resource(CommentAPIPagenation, '/comment/<id>/<int:index>')

# return the submission by id
class SubmissionAPI(Resource):
    def get(self, id):
        submission = get_submission(id)
        return submission

api.add_resource(SubmissionAPI, '/submission/<id>')
# return section of commnet by id and index (pagination of the submission)
class SubmissionAPIPagenation(Resource):
    def get(self, id, index):
        submission = get_submission(id)
        if len(submission) >=  index:
            return {"error": "the index is too big try lower"}
        else:
            return submission[index]

api.add_resource(SubmissionAPIPagenation, '/submission/<id>/<int:index>')


@app.route('/comments/<id>', methods=['GET','POST'])
def fullcomment(id=None):
    if request.method == 'GET':
        comment = get_comment(id)
        return render_template('fullcomment.html', comment=comment[-1])
        
    else:
        return "" # nothing here to see

@app.route('/comments/<id>/<int:index>', methods=['GET','POST'])
def comment(id=None, index=0):
    if request.method == 'GET':
        comment = get_comment(id)
        if len(comment) <=  index:
            return {"error": "the index is too big try lower"}
        else:
            return render_template('comment.html', comment=comment[index])
        
    else:
        return "" # nothing here to see
    
@app.route('/post/<id>', methods=['GET','POST'])
def question(id=None, stop=True):
    if request.method == 'GET':
        submission = get_submission(id)
        if submission['isTitleOnly']:
            return render_template('question.html', post=submission["submissions"])
        else:
            return render_template('fullquestion.html', post=submission['submissions'][0])
        
    else:
        return "" # nothing here to see
@app.route('/post/<id>/title', methods=['GET','POST'])
def question_title(id=None, stop=True):
    if request.method == 'GET':
        submission = get_submission(id)
        if submission['isTitleOnly']:
            return render_template('title.html', post=submission["submissions"])
        else:
           return render_template('title.html', post=submission["submissions"][0])
        
    else:
        return "" # nothing here to see

@app.route('/post/<id>/<int:index>', methods=['GET','POST'])
def seg_question(id=None, index=0):
    if request.method == 'GET':
        submission = get_submission(id)
        print(len(submission['submissions']), index)
        if len(submission['submissions']) <=  index:
            return {"error": "the index is too big try lower"}
        else:
            return render_template('question.html', post=submission['submissions'][index])
        
    else:
        return "" # nothing here to see

@app.route('/videos/<path:path>')
def send_js(path):
    return send_from_directory('videos', path)
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
