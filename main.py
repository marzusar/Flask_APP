from flask import Flask, render_template, request, redirect, flash, url_for
import psycopg2
import os


app = Flask(__name__)



# Функция подключения к базе данных
def get_db_connection():
    
    conn = psycopg2.connect(
        database=os.environ["POSTGRES_DB"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"]
    )
    return conn

# Вывод главной страницы
@app.route('/')
def index1():
    return render_template('index.html')
    
# Вывод главной страницы с методом POST
@app.route('/index', methods=['POST', 'GET'])
def index2():
    name = request.form['nameLogin']
    id = request.form['idLogin']
    return render_template('index.html', name=name, id=id)


@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        name = request.form['name']
        phone = request.form['email']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if any(char in """.,:;"=!_*-+()/#¤%&)"""  for char in name) or any(char in """.,:;"=!_*-+()/#¤%&)""" for char in phone):
            flash (" Введите корректные данные. ")
            return redirect(url_for("reg"))

        if password1 != password2:
            flash (" Пароли не совпадают. ")
            return redirect(url_for("reg"))
        else:       
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO public."userss" (user_name, user_password)
                VALUES (%s, %s);
            """
            id = """
                SELECT Max(id_user) FROM public."userss"
            """
            data = (name, password1)
            cursor.execute(insert_query, data)

            # Committing the transaction
            conn.commit()

            cursor.close()
            conn.close()

            return render_template("index.html", name=name, id=id)

    else:
        return render_template("reg.html")

if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
