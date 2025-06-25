from flask import Flask, render_template, request, redirect, flash, url_for
from dotenv import load_dotenv
import psycopg2
import random
import os

load_dotenv()


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')

# Функция подключения к базе данных
def get_db_connection():
    
    conn = psycopg2.connect(
        database= os.getenv('POSTGRES_DB'),
        user= os.getenv('PGUSER'),
        password= os.getenv('PGPASSWORD'),
        host= os.getenv('SECREPGHOSTT_KEY')
    )
    return conn

def get_rand_object():
    conn = get_db_connection()
    curr = conn.cursor()
    list = random.sample(range(1, 8), 4)
    for i in range(4):
        rand = list[i]
        curr.execute(f"""
                     select public.object.name_object, public.images.name_img, public.object.id  from public.object
                     left join public.images on public.object.id_ing = public.images.id
                     where public.object.id = {rand};
                     """)    
        list[i] = curr.fetchone()
    conn.close()

    return list 

user_name=''
user_id=''
user_img=''
objects = []

# Вывод Главной страницы
@app.route('/index', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def index():
    global user_id, user_img, objects
    id = user_id
    img = user_img
    print ("USER_ID = "+str(id)+", USER_IMG = "+ str(img) +".")

    objects = get_rand_object()

    return render_template('index.html',objects=objects, user_id=id, user_img=img)

#Вевеод страницы Регистрации
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    global user_id, user_img, user_name
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
            user_name = select_name

            # Добавление пользователя в базу данных
            cur.execute(f''' 
                INSERT INTO public."users" (user_name, user_password, user_phone, data_add, id_role)
                VALUES ('{name}', '{password1}', {phone}, NOW(), 2);
            ''')
            conn.commit()
 
            # Ввод id пользователя
            cur.execute(f"""
                SELECT id FROM public."users" WHERE user_name = '{name}' AND user_password = '{password1}';
            """)
            user_id = cur.fetchone()[0]
            
            user_img = 'default.webp'
            conn.close()
            conn.close()

            objects = get_rand_object()

            return render_template('index.html', objects=objects, user_img=user_img, user_id=user_id)
    else:
        return render_template('reg.html')
   
#Вывод страници Авторизации
@app.route('/aut', methods=['POST', 'GET'])
def aut():
    global user_id, user_img, user_name
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
        user_id = cur.fetchone()

        if not user_id:
            flash(f"Такого пользователя c таким именем или паролем не существует. Пожалуйста, проверте введённые данные или зарегестрируйтесь.")
            return redirect(url_for("aut"))
        
        elif id:
            user_name = name
            user_id = user_id[0]

            cur.execute(f'''select name_img from public."images" 
                        left join public."users" on public."images".id = public."users".id_img
                        where public."users".id = {user_id};''')
            user_img = cur.fetchone()
            if user_img:
                user_img+=user_img[0]+'.webp'
            elif not user_img:
                user_img='default.webp'
            conn.close()
            conn.close()

            objects = get_rand_object()

            return render_template("/index.html", objects=objects, user_img=user_img, user_id=user_id)       
    else:
        return render_template('aut.html')

@app.route("/user", methods=['POST', 'GET'])
def user():
    global user_id, user_img, user_name
    id = user_id
    img = user_img
    name = user_name
    print ("USER_ID = "+str(id)+", USER_IMG = "+ str(img) +".")

    print('POST')
    try:
        conn = get_db_connection()
        cur = conn.cursor()
    except Exception as ex:
        print('[INFO] Error while working with PostgreSQl', ex)

    cur.execute(
        f'''select data_add from public.users
        where id = {id};'''
    )
    data_add = cur.fetchone()[0]
    
    return render_template('user.html', user_id = user_id, user_img=img, user_name=name, data_add=data_add,)

@app.route("/object",methods=['POST', 'GET'])
def object():
    global user_id, user_img
    id = user_id
    img = user_img


    if request.method == 'POST':

        try:
            conn = get_db_connection()
            cur = conn.cursor()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        id_object = request.form['object']

        cur.execute(
            f'''select * from public.desc
            where id_object = {id_object}'''
        )
        desc = cur.fetchone()
        
        cur.execute(f"""
                     select public.object.name_object, public.images.name_img from public.object
                     left join public.images on public.object.id_ing = public.images.id
                     where public.object.id = {id_object};
                     """)   
        objects = cur.fetchone()

        return render_template("object.html", objects=objects, desc=desc, user_id = id, user_img=img,)
    else:
       return render_template("index.html", user_id = id, user_img=img,)



@app.route("/exit", methods=['POST', 'GET'])
def exit():
    global user_id, user_img, user_name
    user_id = ''
    user_img = ''
    user_name = ''

    objects = get_rand_object()

    return render_template('index.html', objects = objects)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
