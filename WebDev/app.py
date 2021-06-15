from flask import Flask, render_template, url_for, request, redirect
#from flask_sqlalchemy import SQLAlchemy
#from flask_mysqldb import MySQL
import mysql.connector


app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
#mydb = mysql.connector.connect(host='10.0.0.69',user='root',, password='pmwpmwpmw',database='tempLog')
#mycursor = self.mydb.cursor()
#app.config['MYSQL_HOST'] = '10.0.0.69'
#app.config['MYSQL_USER'] = 'root'
#app.config['MYSQL_PASSWORD'] = 'pmwpmwpmw'
#app.config['MYSQL_DB'] = 'flask'
#app.config['MYSQL_PORT'] = '3306'

#mysql = MySQL(app)

mydb = mysql.connector.connect(host='10.0.0.69',user='root',port='3306', password='pmwpmwpmw',database='tempLog')

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']

        try:
            return redirect('/login')
        except:
            return 'There was an issue adding your task'
    else:
        return 'test'#render_template('index.html', tasks=tasks)

@app.route('/form')
def form():
    return render_template('form.html')
 
@app.route('/login', methods = ['POST', 'GET'])
def login():
    if request.method == 'GET':
        return redirect('/form')
     
    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        cursor = mydb.cursor()
        sql = "INSERT INTO Furnace_Log_Test (date, time, status) VALUES (%s, %s, %s)"
        val = ('2021-05-13', '10:52:01', 0)
        cursor.execute(sql,val)
        mydb.commit()
        cursor.close()
        return 'Done!!'

#@app.route('/delete/<int:id>')
#def delete(id):
#    task_to_delete = Todo.query.get_or_404(id)

#    try:
#        db.session.delete(task_to_delete)
#        db.session.commit()
#        return redirect('/')
#    except:
#        return 'There was a problem deleting that task'

#@app.route('/update/<int:id>', methods=['GET', 'POST'])
#def update(id):
#    task = Todo.query.get_or_404(id)

#    if request.method == 'POST':
#        task.content = request.form['content'
#        try:
#            db.session.commit()
#            return redirect('/')
#        except:
#            return 'There was an issue updating your task'

#    else:
#        return render_template('update.html', task=task)


if __name__ == "__main__":
    app.run(port=6969, debug=True)