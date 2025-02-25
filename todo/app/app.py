import sqlite3
from flask import g, Flask, render_template, request, redirect, url_for

app = Flask(__name__)
DATABASE = './database.db'

# open database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        # return Row objects (namedtuple) instead of tuples
        db.row_factory = sqlite3.Row
    return db

# close database connection when application context dies
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# query database - get cursor > execute query > fetch results (rows)
def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return (rows[0] if rows else None) if one else rows

# create database from schema
def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        with app.open_resource('schema.sql', mode='r') as schema_file:
            cursor.executescript(schema_file.read())
        
        # sample data insertion
        data = [
            {'order_num': 1, 'title': 'frah quintale lyrics', 'details': 'Un giorno ero a casa che stavo<br/>Con il culo sopra il divano<br/>Mezza canna spenta in una mano<br/>Non ricordo a cosa pensavo<br/>Mi son detto: "Giuro, ora la chiamo"<br/>Sta già con un altro e che strano/Lei perfetta, lui uno sfigato<br/>Ingessato tipo Ferragamo', 'importance': 'medium'},
            {'order_num': 2, 'title': 'wash the car', 'details': '', 'importance': 'high'}
        ]
        sql1 = "INSERT INTO 'tasks' (order_num, title, details, importance) VALUES (?, ?, ?, ?);"
        for task in data:
            cursor.execute(sql1, (task['order_num'], task['title'], task['details'], task['importance'],))
        db.commit()

        sql2 = "INSERT INTO 'completed' (title, details, importance) VALUES (?, ?, ?);"
        for task in data:
            cursor.execute(sql2, (task['title'], task['details'], task['importance'],))
        db.commit()

# create an application context
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add():
    db = get_db()
    cursor = db.cursor()
    if request.method == 'POST':
        # get input from from fields on add.html
        order_num = request.form['order_num']
        title = request.form['title']
        details = request.form['details']
        importance = request.form['importance']
        # insert data as new row and return to index.html
        cursor.execute("INSERT INTO 'tasks' (order_num, title, details, importance) VALUES (?, ?, ?, ?);", [order_num, title, details, importance])
        db.commit()
        return render_template("index.html")
    else:
        return render_template('add.html')

@app.route('/list', methods=['GET', 'POST'])
def list():
    # get all users from database
    tasks = query_db('SELECT * FROM tasks')
    completed_tasks = query_db('SELECT * FROM completed')
    return render_template('list.html', tasks=tasks, completed = completed_tasks)

@app.route('/remove/<int:id>', methods=['POST'])
def remove(id):
    # delete row from tasks based on unique_id
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tasks WHERE unique_id = ?", [id])
    db.commit()
    return redirect(url_for('list'))

@app.route('/remove_completed/<int:id>', methods=['POST'])
def remove_completed(id):
    # delete row from completed tasks based on unique_id
    db = get_db()
    cursor = db.cursor()
    cursor.execute("DELETE FROM completed WHERE unique_id = ?", [id])
    cursor.commit()
    return redirect(url_for('list'))

@app.route('/completed/<int:id>', methods=['POST'])
def completed(id):
    # copy data from tasks and add to completed
    # then delete row from tasks
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO completed(title, details, importance) SELECT title, details, importance FROM tasks WHERE unique_id = ? ;", [id])
    cursor.execute("DELETE FROM tasks WHERE unique_id = ?", [id])
    db.commit()
    return redirect(url_for('list'))

@app.route('/restore/<int:id>', methods=['POST'])
def restore(id):
    db = get_db()
    cursor = db.cursor()
    # first get the next available order_num value
    cursor.execute("SELECT MAX(order_num) FROM tasks")
    result = cursor.fetchone()
    if result is None or result[0] is None:
        # if the table is empty it will return None, so set the max_order to 0
        max_order = 0
    else:
        max_order = result[0] + 1
    # copy data from completed into tasks, filling the order_num field with max_order. Then delete row from completed
    cursor.execute("INSERT INTO tasks (order_num, title, details, importance) SELECT ?, title, details, importance FROM completed WHERE unique_id = ?", (max_order, id))
    cursor.execute("DELETE FROM completed WHERE unique_id = ?", [id])
    db.commit()
    return redirect(url_for('list'))


# run the app with Docker configuration
if __name__ == '__main__':
    # initialize the database
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)