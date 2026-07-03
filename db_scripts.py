import sqlite3
db_name = 'quiz.sqlite'
conn = None
cursor = None

def open():
    global conn, cursor
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

def close():
    if cursor:
        cursor.close()
    if conn:
        conn.close()

def do(query, data=None):
    if data:
        cursor.execute(query, data)
    else:
        cursor.execute(query)
    conn.commit()

def do_many(query, data_list):
    cursor.executemany(query, data_list)
    conn.commit()

def clear_db():
    """Удаляет все таблицы"""
    do('DROP TABLE IF EXISTS quiz_content')
    do('DROP TABLE IF EXISTS question')
    do('DROP TABLE IF EXISTS quiz')
    
def create():
    # 1. Создаём таблицы 
    do('''CREATE TABLE IF NOT EXISTS quiz (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )''')
    do('''CREATE TABLE IF NOT EXISTS question (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL UNIQUE,
        answer TEXT NOT NULL,
        wrong1 TEXT NOT NULL,
        wrong2 TEXT NOT NULL,
        wrong3 TEXT NOT NULL
    )''')
    do('''CREATE TABLE IF NOT EXISTS quiz_content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        quiz_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        FOREIGN KEY (quiz_id) REFERENCES quiz(id) ON DELETE CASCADE,
        FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE
    )''')

    #-------- 1 опрос: "Random opros"  --------
    do('INSERT INTO quiz (name) VALUES (?)', ('Random opros',))
    questions1 = [
        ('Столица России?', 'Москва', 'Санкт-Петербург', 'Казань', 'Новосибирск'),
        ('Сколько будет 5 * 6?', '30', '25', '36', '35'),
        ('Кто написал "Евгений Онегин"?', 'Пушкин', 'Лермонтов', 'Толстой', 'Достоевский'),
        ('Какой газ самый распространённый в атмосфере?', 'Азот', 'Кислород', 'Углекислый газ', 'Аргон'),
        ('√144 = ?', '12', '14', '10', '16')
    ]
    do_many('''INSERT INTO question (question, answer, wrong1, wrong2, wrong3) 
               VALUES (?, ?, ?, ?, ?)''', questions1)

    #Связываем вопросы с первым опросом
    cursor.execute('SELECT id FROM quiz WHERE name = "Random opros"')
    quiz_id1 = cursor.fetchone()[0]
    #Получаем ID вопросов по их тексту
    question_texts1 = [q[0] for q in questions1]
    placeholders1 = ','.join('?' for _ in question_texts1)
    cursor.execute(f'SELECT id FROM question WHERE question IN ({placeholders1})', question_texts1)
    question_ids1 = [row[0] for row in cursor.fetchall()]
    quiz_content_data1 = [(quiz_id1, qid) for qid in question_ids1]
    do_many('INSERT INTO quiz_content (quiz_id, question_id) VALUES (?, ?)', quiz_content_data1)

    #-------- 2 опрос: "О знании версии 6.7 Genshin Impact" --------
    do('INSERT INTO quiz (name) VALUES (?)', ('О знании версии 6.7 Genshin Impact',))
    questions2 = [
        ('Какой самый наилучший сет будет для Сандроне в версии 6.7?',
         'Застывшее в тени разочарование',
         'Позолоченные сны', 'Конец Гладиатора', 'Решимость временщика'),
        ('Скин на какого персонажа мы можем получить бесплатно?',
         'Шарлотта',
         'Сандроне', 'Ситлали', 'Нёвиллет'),
        ('Куда по сюжету мы отправимся в этот раз?',
         'На Луну',
         'В соседний регион', 'На море', 'В бездну'),
        ('Где пройдёт главное событие 6.7?',
         'Фонтейн',
         'Нод-край', 'Натлан', 'Мондшат'),
        ('Какое настоящие имя у чёрной кухенки их сюжета?',
         'Нин Нин',
         'Яйцо', 'Нин-Киггия', 'Нин Гуан')
    ]
    do_many('''INSERT INTO question (question, answer, wrong1, wrong2, wrong3) 
               VALUES (?, ?, ?, ?, ?)''', questions2)

    #Связываем вопросы со вторым опросом
    cursor.execute('SELECT id FROM quiz WHERE name = "О знании версии 6.7 Genshin Impact"')
    quiz_id2 = cursor.fetchone()[0]
    question_texts2 = [q[0] for q in questions2]
    placeholders2 = ','.join('?' for _ in question_texts2)
    cursor.execute(f'SELECT id FROM question WHERE question IN ({placeholders2})', question_texts2)
    question_ids2 = [row[0] for row in cursor.fetchall()]
    quiz_content_data2 = [(quiz_id2, qid) for qid in question_ids2]
    do_many('INSERT INTO quiz_content (quiz_id, question_id) VALUES (?, ?)', quiz_content_data2)

    cursor.execute('PRAGMA foreign_keys=on')

def show(table):
    '''query = 'SELECT * FROM ' + table
    cursor.execute(query)
    print(cursor.fetchall())'''

    cursor.execute(f'SELECT * FROM {table}')
    for row in cursor.fetchall():
        print(row)

def show_tables():
    show('question')
    show('quiz')
    show('quiz_content')

def get_questions(quiz_id=1):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    cur.execute('''
        SELECT q.id, q.question, q.answer, q.wrong1, q.wrong2, q.wrong3
        FROM question q, quiz_content qc
        WHERE q.id = qc.question_id
        AND qc.quiz_id = ?
        ORDER BY q.id
    ''', (quiz_id,))
    questions = cur.fetchall()
    cur.close()
    con.close()
    return questions

def main():
    open()
    clear_db()
    create()
    print(get_questions())
    close()

if __name__ == "__main__":
    main()
