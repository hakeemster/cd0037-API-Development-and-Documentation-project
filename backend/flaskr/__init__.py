import os
from unicodedata import category
from flask import Flask, request, abort, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Pagination method
def paginate_questions(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    # CORS(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories")
    def get_all_categories():

        # get all categories
        categories = Category.query.all()

        categories_collection = {}

        for category in categories:
            categories_collection[category.id] = category.type

        return jsonify({
            'success': True,
            'categories': categories_collection
        })



    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.
    """
    @app.route('/questions')
    def retrieve_questions():
        try:
            # get questions
            selection = Question.query.order_by(Question.id).all()

            current_questions = paginate_questions(request, selection)

            # get total num of questions
            num_of_questions = len(selection)

            if (len(current_questions) == 0):
                abort(404)

            # get all categories
            categories = Category.query.all()

            all_categories = {}

            for category in categories:
                all_categories[category.id] = category.type

            return jsonify(
                {
                    'success': True,
                    'questions': current_questions,
                    'total_questions': num_of_questions,
                    'categories': all_categories
                }
            )

        except Exception:
            abort(400)

    """
    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """


    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()

            selection = Question.query.order_by(Question.id).all()

            current_questions = paginate_questions(request, selection)

            return jsonify(
                {
                    "success": True,
                }
            )

        except:
            abort(422)

    """
    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        
        body = request.get_json()

        question = body.get('question', None)
        answer = body.get('answer', None)
        difficulty = body.get('difficulty', None)
        category = body.get('category', None)

        try:
            question = Question(question=question, answer=answer, difficulty=difficulty, category=category)
            question.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            
            return jsonify(
                {
                    "success": True,
                    "created": question.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all())
                }
            )

        except:
            abort(422)

    """
    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.
    """
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)

        if search_term:
            search_results = Question.query.filter(Question.question.ilike(f'%{search_term}%')).all()

            return jsonify(
                {
                    'success': True,
                    'questions': [question.format() for question in search_results],
                    'total_questions': len(search_results),
                    'current_category': None
                }
            )

        abort(404)

    """
    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:id>/questions")
    def questions_in_category(id):

        category = Category.query.filter_by(id=id).one_or_none()

        if category:
            questions_in_category = Question.query.filter_by(category=id).all()

            current_questions = paginate_questions(request, questions_in_category)

            return jsonify(
                {
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(questions_in_category),
                    'current_category': category.type
                }
            )
        
        else:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.
    """
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        
        # body = request.get_json()

        # quiz_category = body.get('quiz_category')
        # previous_questions = body.get('previous_questions')

        # try:
        #     if (quiz_category['id'] == 0):
        #         questions = Question.query.all()
        #     else:
        #         questions = Question.query.filter_by(category=quiz_category['id']).all()

        #     random_number = random.randint(0, len(questions)-1)

        #     next_question = questions[random_number]

        #     while next_question.id not in previous_questions:
        #         next_question = questions[random_number]

        #         return jsonify({
        #             'success': True,
        #             'question': {
        #                 "answer": next_question.answer,
        #                 "category": next_question.category,
        #                 "difficulty": next_question.difficulty,
        #                 "id": next_question.id,
        #                 "question": next_question.question
        #             },
        #             'previousQuestion': previous_questions
        #         })

        # except Exception:
        #     abort(404)

        
        body = request.get_json()

        quiz_category = body.get('quiz_category')
        previous_questions = body.get('previous_questions')
        category_id = quiz_category.get('id')

        try:
            if (category_id == 0):
                questions = Question.query.all()
            else:
                questions = Question.query.filter(Question.category == category_id).all()
            
            next_question = questions[random.randint(0, len(questions)-1)]

            while next_question.id:
                
                return jsonify(
                    {
                        'success': True,
                        'question': {
                            "answer": next_question.answer,
                            "category": next_question.category,
                            "difficulty": next_question.difficulty,
                            "id": next_question.id,
                            "question": next_question.question
                        },
                        'previousQuestion': previous_questions
                    }
                )

                # return len(questions)

        except Exception:
            abort(422)




    """
    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request_error(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "Bad request"
        }), 400

    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Question not found!"
        }), 404

    @app.errorhandler(422)
    def unprocessable_error(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "Request was unprocessable"
        }), 422

    @app.errorhandler(500)
    def server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Server Error"
        }), 500

    return app

