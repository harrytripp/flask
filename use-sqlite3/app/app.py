import sqlite3
from flask import g, Flask

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

# create an application context
@app.route('/')
def index():
    cur = get_db().cursor()
    '...'

# query database - get cursor > execute query > fetch results (rows)
def query_db(query, args=(), one=False):
    cursor = get_db().execute(query, args)
    rows = cursor.fetchall()
    cursor.close()
    return (rows[0] if rows else None) if one else rows

# use query function and the row factory to get users from database
def main():
    # all results
    for user in query_db('select * from users'):
        print(user['username'], 'had the id', user['user_id'])

    #single result
    user = query_db('select * from users where username = ?',
                    [the_username], one=True)
    if user is None:
        print('No such user')
    else:
        print(the_username, 'has the id', user['user_id'])

# create database from schema
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as schema_file:
            db.cursor().executescript(schema_file.read())
        db.commit()

init_db()
