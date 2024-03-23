import flask
from flask import jsonify, make_response, request
from . import db_session
from .quezes import Quezes
from .questions import Questions

blueprint = flask.Blueprint(
    'questions_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/questions', methods=['POST'])
def create_question():
    if not request.json:
        return make_response(jsonify({'error': 'Empty request'}), 400)
    elif not all(key in request.json for key in
                 ['ask', 'question1', 'question2', 'question3', 'question4', 'is_private']):
        return make_response(jsonify({'error': 'Bad request'}), 400)
    db_sess = db_session.create_session()
    questions = Questions(
        ask=request.json['ask'],
        question1=request.json['question1'],
        question2=request.json['question2'],
        question3=request.json['question3'],
        question4=request.json['question4'],
        is_private=request.json['is_private'],
    )
    db_sess.add(questions)
    db_sess.commit()
    return jsonify({'id': questions.id})