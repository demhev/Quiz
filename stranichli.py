from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from db_scripts import db_name, get_questions
import random

app = Flask(__name__)

#Получить все опросы~~
def get_all_quizzes():
    conn = sqlite3.connect(db_name)
    cur = conn.cursor()
    cur.execute('SELECT id, name FROM quiz ORDER BY id')
    quizzes = cur.fetchall()
    conn.close()
    return quizzes   #(id, name)--

#Страничка 1: список викторин~~
@app.route('/')
def index():
    quizzes = get_all_quizzes()
    return render_template('index.html', quizzes=quizzes)

#Страничка 2: прохождение викторины~~
@app.route('/quiz/<int:quiz_id>')
def quiz(quiz_id):
    questions = get_questions(quiz_id)   #используем готовую функцию--
    #если опрос не найден вернём 404--
    if not questions:
        return "Такой викторины нет", 404

    #Перемешкиваем--
    quiz_data = []
    for q in questions:
        options = [q[2], q[3], q[4], q[5]]   #правильный + 3 неправильных-
        random.shuffle(options)              #перемешиваем-
        quiz_data.append({
            'id': q[0],
            'question': q[1],
            'options': options
        })
    return render_template('quiz.html', questions=quiz_data, quiz_id=quiz_id)

#Страничка 3: результат прохождения~~
@app.route('/quiz/<int:quiz_id>/check', methods=['POST'])
def check_quiz(quiz_id):
    questions = get_questions(quiz_id)
    correct = 0
    total = len(questions)
    for q in questions:
        user_answer = request.form.get(f'question_{q[0]}')
        if user_answer == q[2]:   #правильный ответ находится в индексе 2--
            correct += 1
    return render_template("result.html", correct=correct, total=total)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)