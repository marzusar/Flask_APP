from flask import Flask, render_template, request, redirect, flash, url_for
import psycopg2
import os


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
        name = request.form['nameLogin']
        id = request.form['idLogin']
        return render_template('index.html', name=name)
    else:
        return render_template('index.html')

#Вевеод страницы Регистрации
@app.route('/reg', methods=['POST', 'GET'])
def reg():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)
        cursor = conn.cursor()

        name = request.form['name']
        phone = request.form['phone']
        password1 = request.form['password1']
        password2 = request.form['password2']

        if any(char in """.,:;"=!_*-+()/#¤%&)"""  for char in name) or any(char in """.,:;"=!_*-+()/#¤%&)""" for char in phone):
            flash (" Введите корректные данные. ")
            return redirect(url_for("reg"))
        
        select_name = f"""
                SELECT user_name FROM public."users" where user_name = '{name}';
            """

        cursor.execute(select_name)
        select_name = cursor.fetchall()
        

        if password1 != password2:
            flash (" Пароли не совпадают. ")
            return redirect(url_for("reg"))
        elif select_name:
            flash (" Такое имя уже существует. ")
            return redirect(url_for("reg"))
        else:       
            #добавление пользователя в базу данных
            insert_query = """
                INSERT INTO public."users" (user_name, user_password, user_phone, data_add, id_role)
                VALUES (%s, %s, %s, NOW(), 2);
            """
            data = (name, password1, phone)
            cursor.execute(insert_query, data)

            #поиск id пользоватля
            select_id = """
                SELECT id FROM public."users" WHERE user_name = %s AND user_password = %s;
            """
            data = (name, password1)
            cursor.execute(select_id, data)
            id = cursor.fetchall()
            
            # Committing the transaction
            conn.commit()

            cursor.close()
            conn.close()

            return render_template("index.html", name=name, id=id)
    else:
        return render_template("reg.html")
   
#Вывод страници Авторизации
@app.route('/aut', methods=['POST', 'GET'])
def aut():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)

        name = request.form['name']
        password = request.form['password']

        if any(char in """.,:;"=!_*-+()/#¤%&)"""  for char in name) or any(char in """.,:;"=!_*-+()/#¤%&)""" for char in password):
            flash (" Введите корректные данные. ")
            return redirect(url_for("reg"))

        cursor = conn.cursor()

        select_query = """
        SELECT id FROM public."users" WHERE user_name = %s AND user_password = %s;
        """
        data = (name, password)

        cursor.execute(select_query, data)    
        user = cursor.fetchone()
        
        if not user:
            flash("Такого пользователя c таким именем или паролем не существует. Пожалуйста, проверте введённые данные или зарегестрируйтесь.")
            return redirect(url_for("aut"))
        else:
            return render_template('index.html', name=name, id=user)
       
    else:
        return render_template('aut.html')

@app.route("/user", methods=['POST', 'GET'])
def user():
    if request.method == 'POST':
        try:
            conn = get_db_connection()
        except Exception as ex:
            print('[INFO] Error while working with PostgreSQl', ex)
        cur = conn.cursor()

        id=1

        select_img=f"""
        Select name_img for public."images" 
        left join public."users" on public."images" .id = public."users".id_img
        where u.id = {id};
        """      
        cur.execute(select_img)

        selects_img = cur.fetchall()

        if not selects_img:
            img = 'default.webp'
            return  render_template('user.html', id=id, img=img)
        else:

            img = selects_img+'.webp'
            return  render_template('user.html', id=id, img=img)
        
    else:
        return  render_template('user.html')


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))
