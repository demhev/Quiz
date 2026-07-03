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

@app.route('/create_quiz', methods=['GET', 'POST'])
def create_quiz():
    if request.method == 'POST':
        # Получаем название опроса
        quiz_name = request.form.get('quiz_name', '').strip()
        if not quiz_name:
            return "Название опроса обязательно", 400

        # Получаем списки полей (они приходят как массивы)
        questions = request.form.getlist('question[]')
        answers = request.form.getlist('answer[]')
        wrong1 = request.form.getlist('wrong1[]')
        wrong2 = request.form.getlist('wrong2[]')
        wrong3 = request.form.getlist('wrong3[]')

        # Проверяем, что есть хотя бы один вопрос
        if not questions or not questions[0]:
            return "Добавьте хотя бы один вопрос", 400

        # Подключаемся к БД и вставляем всё в транзакции
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()

        # 1. Вставляем новый опрос
        cur.execute('INSERT INTO quiz (name) VALUES (?)', (quiz_name,))
        quiz_id = cur.lastrowid

        # 2. Вставляем вопросы и связываем
        for i in range(len(questions)):
            q_text = questions[i].strip()
            if not q_text:
                continue  # пропускаем пустые
            ans = answers[i].strip()
            w1 = wrong1[i].strip()
            w2 = wrong2[i].strip()
            w3 = wrong3[i].strip()
            # Проверяем, что все поля заполнены
            if not (q_text and ans and w1 and w2 and w3):
                continue  # или можно вернуть ошибку
            cur.execute('''INSERT INTO question (question, answer, wrong1, wrong2, wrong3)
                           VALUES (?, ?, ?, ?, ?)''', (q_text, ans, w1, w2, w3))
            question_id = cur.lastrowid
            cur.execute('INSERT INTO quiz_content (quiz_id, question_id) VALUES (?, ?)',
                        (quiz_id, question_id))

        conn.commit()
        conn.close()

        # Перенаправляем на главную, где новый опрос уже в списке
        return redirect(url_for('index'))

    # GET – показываем форму
    return render_template('create_quiz.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)