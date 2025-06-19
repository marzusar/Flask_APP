from flask import Flask, render_template, request, redirect
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# @app.route('/index', methods=['POST', 'GET']) # Вывод главной страницы
# def index():
#     name = request.form['nameLogin']
#     id = request.form['idLogin']
        
#     return render_template('index.html', name=name, id=id)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
