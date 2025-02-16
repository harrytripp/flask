import sqlite3
from flask import g, Flask, render_template

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
        with app.open_resource('schema.sql', mode='r') as schema_file:
            db.cursor().executescript(schema_file.read())
        
        # sample data insertion
        data = [
            {'user_id': 1, 'username': 'f.quintale'},
            {'user_id': 2, 'username': 'm.binotto'}
        ]
        sql = "INSERT INTO 'users' (user_id, username) VALUES (?, ?);"
        for user in data:
            db.cursor().execute(sql, (user['user_id'], user['username']))
        db.commit()

# create an application context
@app.route('/')
def index():
    # get all users from database
    users = query_db('SELECT * FROM users')
    return render_template('index.html', users=users)

# run the app with Docker configuration
if __name__ == '__main__':
    # initialize the database
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)