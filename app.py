from flask import Flask, session, request, render_template, redirect, url_for, flash, Response
from functools import wraps
from timing_attack import slow_compare, gen_password, good_pass
from data_race import RacyBalances
import yaml
import os
from redis import StrictRedis
from date_hash import date_hash

app = Flask(__name__)

config = yaml.load(open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.yml'), 'r'))

app.secret_key = config['SECRET_KEY']

USERS = config.get('users', {
    'marty_mcfly': 'Marty McFly',
    'biff_tannen': 'Biff Tannen'
})

PER_CHAR_DELAY = config.get('PER_CHAR_DELAY', 0.2)
STARTING_COINS = config.get('STARTING_COINS', 50)
SOLUTION_COST = config.get('SOLUTION_COST', 1000)
RACE_DELAY = config.get('RACE_DELAY', 1)
REDIS_URL = config.get('REDIS_URL', 'redis://')


the_redis = StrictRedis.from_url(REDIS_URL)
balances = RacyBalances(the_redis, STARTING_COINS, RACE_DELAY)

def authed(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        gh = session.get('gh', '')
        username = session.get('username', '')
        if kwargs['github'] == gh and username and username in USERS:
            return f(*args, **kwargs)
        else:
            return redirect(url_for('login', github=kwargs['github']))
    return decorated_function

@app.route('/')
def index():
    return render_template('intro.html')

RESPONSE_TIME_HEADER = 'X-Upstream-Response-Time'

@app.route('/u/<github>/login', methods=['GET', 'POST'])
def login(github):
    if session.get('gh') == github and session.get('username') in USERS:
        return redirect(url_for('store', github=github))
    if request.method == 'GET':
        resp = Response(render_template('login.html', github=github, users=USERS))
        resp.headers[RESPONSE_TIME_HEADER] = '0.01'
        return resp
    else:
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        response_time = 0.01
        if username in USERS:
            if not good_pass(password):
                flash('Invalid Password (must be alphanumeric 6-12 characters)')
            else:
                actual_password = gen_password(app.secret_key, github, username)
                print(actual_password)
                correct, compare_time = slow_compare(password, actual_password, PER_CHAR_DELAY)
                response_time += compare_time
                if correct:
                    session['gh'] = github
                    session['username'] = username
                    return redirect(url_for('store', github=github))
                else:
                    flash('Bad Password')
        else:
            flash('invalid user')
        resp = Response(render_template('login.html', github=github, users=USERS, username=username))
        resp.headers[RESPONSE_TIME_HEADER] = response_time
        return resp


@app.route('/u/<github>/')
@authed
def store(github):
    balance = balances.get(github, session['username'])
    solution = None
    if balance >= SOLUTION_COST:
        solution = date_hash(app.secret_key, github)
    transfer_users = {k : v for k, v in USERS.items() if k != session['username']}
    total = sum(map(lambda u: balances.get(github, u), transfer_users)) + balance
    if total == 0:
        balances.put(github, session['username'], 5)
        flash("You got lucky! We're giving you 5 HackCoins on this account.")
    name = USERS[session['username']]
    return render_template('store.html', transfer_users=transfer_users, github=github, balance=balance, solution=solution, solution_cost=SOLUTION_COST, name=name)

@app.route('/u/<github>/transfer', methods=['POST'])
@authed
def transfer(github):
    other_username = request.form.get('to', '')
    if other_username == session['username']:
        return "you can't transfer to yourself"
    if other_username not in USERS:
        return "user not found"
    balances.transfer(github, session['username'], other_username)
    return redirect(url_for('store', github=github))

@app.route('/u/<github>/logout')
@authed
def logout(github):
    session.clear()
    return redirect(url_for('login', github=github))

if __name__ == '__main__':
    app.run(debug=True, threaded=True)
