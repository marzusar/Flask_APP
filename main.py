from flask import Flask, render_template, request, redirect, flash, url_for
import psycopg2
import random
import os



app = Flask(__name__)
# app.secret_key = os.environ["SECRET_KEY"]
app.secret_key = '123bnasdjn234jinasd'

# Функция подключения к базе данных
def get_db_connection():
    
    conn = psycopg2.connect(
        database=os.environ["POSTGRES_DB"],
        user=os.environ["PGUSER"],
        password=os.environ["PGPASSWORD"],
        host=os.environ["PGHOST"],
        port=os.environ["PGPORT"]
        
    )
    # conn = psycopg2.connect(
    #     database='Tour',
    #     user='postgres',
    #     password='postgres',
    #     host='localhost'        
    # )
    return conn

# Вывод Главной страницы
@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        
        id = request.form['ID']
        try:            
            conn = get_db_connection()
            curr = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)
        list = []
        for i in range(4):
            rand = random.randint(1,7)
            curr.execute(f"""
                         select public.object.name_object, public.images.name_img from public.object
                         left join public.images on public.object.id_ing = public.images.id
                         where public.object.id = {rand};
                         """)
            list.insert(i, curr.fetchone())
            print(list)
            

        return render_template('index.html',objects=list, id=id)
    else:
        try:
            conn = get_db_connection()
            curr = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        list = []
        for i in range(4):
            rand = random.randint(1,7)
            curr.execute(f"""
                         select public.object.name_object, public.images.name_img from public.object
                         left join public.images on public.object.id_ing = public.images.id
                         where public.object.id = {rand};
                         """)
        
            list.insert(i, curr.fetchone())
            print(list)
            print (list)
    curr.close()
    return render_template('index.html',objects=list)
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
        select_name = cur.fetchone()
        

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
            id = cur.fetchone()[0]
            

            cur.execute(f'''select name_img from public."images" 
                        left join public."users" on public."images".id = public."users".id_img
                        where public."users".id = {id};''')
            name_img = cur.fetchone()
            if not name_img:
                ava = 'default.webp'
            elif name_img:
                ava= name_img[0]
                ava +='.webp'
            conn.close()
            conn.close()

            return render_template("index.html", ava=ava, id=id)
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
        id = clear_id


        if not id:
            flash(f"Такого пользователя c таким именем или паролем не существует. Пожалуйста, проверте введённые данные или зарегестрируйтесь.{id}")
            return redirect(url_for("aut"))
        
        elif id:
            cur.execute(f'''select name_img from public."images" 
                        left join public."users" on public."images".id = public."users".id_img
                        where public."users".id = {id};''')
            name_img = cur.fetchone()
            if name_img:
                ava = name_img[0]+'.webp'
            elif not name_img:
                ava = 'default.webp'
            conn.close()
            conn.close()

            return render_template("index.html", ava=ava, id=id)       
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

        id = request.form['ID']

        # Вывод названия изображения аватарки
        cur.execute(f'''
        select name_img from public."images"
        join left public."users" on public."images".id = public."users".id_img
        where public."users".id = {id};
        ''')
        clear_ava = cur.fetchone()

        # Вывод имя пользователя
        cur.execute(f'''
        select user_name from public."users"
        where id = {id};
        ''')
        user_name = cur.fetchone()

        # Вывод 
        cur.execute(f'''
        select data_add from public."users"
        where id = {id};
        ''')
        data_add = cur.fetchone()

        ava=clear_ava[0]
        if ava:
            ava+='.webp'
        elif not ava:
            ava = 'default.webp'
        
        return render_template('user.html',  id=id, ava=ava, clear_ava=clear_ava, user_name=user_name, data_add=data_add)

    else:
        return  render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
