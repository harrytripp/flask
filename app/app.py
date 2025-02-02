import sqlite3
from datetime import datetime
import click
from flask import Flask, g, current_app
app = Flask(__name__)

DATABASE = './database.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

def init_db():
     db = get_db()
     with current_app.open_resource('schema.sql') as file:
          db.executescript(file.read().decode('utf8'))

@click.command('init-db')
def init_db_command():
     """clear the existing data and create new tables"""
     init_db()
     click.echo('Initialised the database.')

sqlite3.register_converter(
     "timestamp", lambda v: datetime.fromisoformat(v.decode())
)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
def hello():
	return "Hello World!"

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8000)