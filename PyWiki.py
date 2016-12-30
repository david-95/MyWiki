# all the imports
import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash

# configuration
DATABASE = './wiki.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'


# create our little application :)
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()
        

@app.route('/')
def show_entries():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    else:
        db = get_db()
        cur = db.execute('select topic, topicid,content from knowledge order by topicid desc')
        entries = cur.fetchall()
        return render_template('show_entries.html', entries=entries)

@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    tpIDTxt=request.form['topicID'].strip()
    topicTxt=request.form['topic'].strip()
    contentTxt=request.form['content'].strip()
    if tpIDTxt=="unicode:":
        if not(topicTxt == "unicode:" or contentTxt == "unicode:"):  # blank value
            db.execute('insert into knowledge (topicID,topic,content) values (null,?, ?)',
                       [request.form['topic'], request.form['content']])
            db.commit()
    else:
        if not(topicTxt == "unicode:" or contentTxt == "unicode:"):  # blank value
            db.execute('update knowledge set topic=?,content=?  where topicID=? ',
                       [request.form['topic'], request.form['content'],request.form['topicID']])
            db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
#     return redirect(url_for('show_entries'))  # origina 
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)