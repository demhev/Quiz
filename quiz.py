from flask import Flask, redirect, url_for, render_template
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'))

@app.route('/')
def index():
    """Перенаправляет на index.html"""
    ...
    return 'Привет, Мир!'

if __name__ == '__main__':
    app.run()