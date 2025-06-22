from flask import Flask, render_template, request, redirect, flash, url_for
import psycopg2
import os
import re


app = Flask(__name__)
app.secret_key = os.environ["SECRET_KEY"]

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

# Вывод Главной страницы
@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        id = id
        
        return render_template('index.html', id=id)
    else:
        return render_template('index.html')

#Вевеод страницы Регистрации
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        name = request.form['name']
        phone = request.form['phone']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if any(char in """.,:;"=!_*-+()/#¤%&)"""  for char in name) or any(char in """.,:;"=!_*-+()/#¤%&)""" for char in phone) or any(char in """.,("';:=!'")""" for char in password1):
            flash (" Введите корректные данные. ")
            return redirect(url_for("reg"))
        
        # Проверка наличия введённого имени в базе данных
        cur.execute ( f"""
                SELECT user_name FROM public."users" 
                where user_name = '{name}';
            """)
        select_name = cur.fetchall()
        

        if password1 != password2:
            flash (" Пароли не совпадают. ")
            return redirect(url_for("reg"))
        elif select_name:
            flash (" Такое имя  уже существует. ")
            return redirect(url_for("reg"))
        else:       
           
            cur.execute(f'''
                INSERT INTO public."users" (user_name, user_password, user_phone, data_add, id_role)
                VALUES ('{name}', '{password1}', {phone}, NOW(), 2);
            ''')
            conn.commit()
 
            # Ввод id пользователя
            cur.execute(f"""
                SELECT id FROM public."users" WHERE user_name = '{name}' AND user_password = '{password1}';
            """)
            id = cur.fetchall()
            
            
            cur.execute(f'''select name_img from public."images" 
                        left join public."users" on public."images".id = public."users".id_img
                        where public."users".id = {id};''')
            name_img = cur.fetchall()
            conn.close()
            conn.close()

            return render_template("index.html", name_img=name_img, id=id)
    else:
        return render_template("reg.html")
   
#Вывод страници Авторизации
@app.route('/aut', methods=['POST', 'GET'])
def aut():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        name = request.form['name']
        password = request.form['password']

        if any(char in """.,:;"=!_*-+()/#¤%&)"""  for char in name) or any(char in """.,:;"=!_*-+()/#¤%&)""" for char in password):
            flash (" Введите корректные данные. ")
            return redirect(url_for("reg"))

        cur.execute(f"""
        SELECT id FROM public."users" 
        WHERE user_name = '{name}' AND user_password = '{password}';
        """) 
        clear_id = cur.fetchone()
        id = clear_id[0]


        if not id:
            flash(f"Такого пользователя c таким именем или паролем не существует. Пожалуйста, проверте введённые данные или зарегестрируйтесь.{id}")
            return redirect(url_for("aut"))
        
        elif id:
            cur.execute(f'''select name_img from public."images" 
                        left join public."users" on public."images".id = public."users".id_img
                        where public."users".id = {id};''')
            name_img = cur.fetchall()
            conn.close()
            conn.close()

            return render_template("index.html",name=name, name_img=name_img, id=id)       
    else:
        return render_template('aut.html')

@app.route("/user", methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
            cur = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        id = id

        # Вывод названия изображения аватарки
        cur.execute(f'''
        select name_img from public."images"
        join left public."users" on public."images".id = public."users".id_img
        where public."users".id = {id};
        ''')
        ava = cur.fetchall()

        # Вывод имя пользователя
        cur.execute(f'''
        select user_name from public."users"
        where id = {id};
        ''')
        user_name = cur.fetchall()

        # Вывод 
        cur.execute(f'''
        select data_add from public."users"
        where id = {id};
        ''')
        data_add = cur.fetchall()

        if ava:
            ava+='.webp'
            return  render_template('user.html', id=id, ava=ava, user_name=user_name, data_add=data_add)
        elif not ava:
            ava = 'default.webp'
            return render_template('user.html',  id=id, ava=ava, user_name=user_name, data_add=data_add)

    else:
        return  render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
