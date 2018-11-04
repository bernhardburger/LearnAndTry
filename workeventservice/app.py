from flask import Flask
from flask import session, redirect, url_for, escape, request
import os

app = Flask(__name__)
# define a new secret session key each start
app.secret_key = os.urandom(32)


@app.route('/')
def index():
    # try to receive the username from the cookie from session
    if 'username' in session:
        # print("logged in a {0}").format(session['username'])
        return 'logged in as %s' % escape(session['username'])
    return ' you are not logged in'


@app.route('/login', methods=['GET', 'POST'])
def login():
    # loging procedure
    if request.method == 'POST':
        try:
            login_result = authenticate(request.form['username'], request.form['password'])


        except:
            print('unexpected error')
        if login_result:
            return redirect(url_for('index'))
        return redirect(url_for('login'))
    return '''
            <form method="post">
                <p><input type=text name=username>
                <p><input type=password name=password>
                <p><input type=submit value=Login>
            </form>
             '''


def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect(url_for('index'))


def authenticate(user, passwd):
    # authenticate user pw from userpw
    if user == 'admin' and passwd == 'admin':
        session['username'] = user
        print('login Sucess')
        return True
    print('login Failure')
    return False


if __name__ == '__main__':
    app.run()
