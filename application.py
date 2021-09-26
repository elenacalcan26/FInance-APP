import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask.helpers import url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # get logged user
    user_id = session["user_id"]

    stocks = db.execute("SELECT * FROM stocks WHERE id = ?", user_id)
    user_cash = (db.execute("SELECT cash FROM users WHERE id = ?", user_id))[0]["cash"]
    total_stocks = (db.execute("SELECT SUM(total) FROM stocks WHERE id = ?", session['user_id']))[0]["SUM(total)"]

    # check if user owns some stocks
    if total_stocks == None:
        total_stocks = 0

    return render_template("index.html", stocks=stocks, user_cash=user_cash, grand_total=user_cash + total_stocks)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""

    # user reached route via POST (by submitting buy form)
    if request.method == "POST":

        # check if the user submited the symbol and the number of shares
        if not request.form.get("symbol"):
            return apology("must complete the symbol field")
        elif not request.form.get("shares"):
            return apology("must complete the shares field")
        
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")
        
        # check if the number of shares is a valid integer
        if int(shares) < 0:
            return apology("the number of shares must be positive")
        if shares.find('.') != -1:
            return apology("the number must be a positive integer")

        stocks = lookup(symbol)

        # ensure symbol exits
        if stocks == None:
            return apology("no stock was found")

        user = db.execute("SELECT * FROM users WHERE id = ?", session['user_id'])

        curr_cash = user[0]["cash"]

        # check if user has enough money to buy the stock
        if stocks['price'] * int(shares) > curr_cash:
            return apology("you don't have enough cash")

        # calculate the total of the bought stock
        total = stocks['price'] * int(shares)

        # calculate user's cash after buyng the stock
        curr_cash -= total

        db.execute("UPDATE users SET cash = ? WHERE id = ?", curr_cash, session['user_id'])
        
        # add the action in user's history
        date = str(datetime.now().replace(microsecond=0))
        db.execute("INSERT INTO history (id, symbol, shares, price, action, date) VALUES (?, ?, ?, ?, ?, ?)",
                    session['user_id'], stocks['symbol'], int(shares), stocks['price'], "BUY", date)

        user_stocks = db.execute("SELECT * FROM stocks WHERE id = ? AND symbol = ?", session['user_id'], stocks['symbol'])

        # check if user owns the stock
        if user_stocks == None:
            
            # calculate the new number of shares
            curr_shares = user_stocks[0]['shares']
            new_shares = curr_shares + int(shares)

            # calculate the new total of stock
            curr_total = user_stocks[0]['total']
            new_total = curr_total + total

            db.execute("UPDATE stocks SET shares = ?, price = ?, total = ? WHERE id = ? AND symbol = ?",
                     new_shares, stocks['price'], new_total, session['user_id'], stocks['symbol'])
        
        else:

            # doesn't own the stock and it must be added into the database
            db.execute("INSERT INTO stocks (id, symbol, company, shares, price, total) VALUES (?, ?, ?, ?, ?, ?)",
                        session['user_id'], stocks['symbol'], stocks['name'], int(shares), stocks['price'], total),


        return redirect("/")

    # user reached route via GET (by clicking a link)
    else:
        return render_template("buy.html")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # extract logged user's action history from the database
    history = db.execute("SELECT * FROM history WHERE id = ? ORDER BY date DESC", session['user_id'])

    if history == None:
        history = []

    return render_template("history.html", stocks=history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    # reached route via POST (by submitting)
    if request.method == "POST":
    
        # check if user completed the form
        if not request.form.get("symbol"):
            return apology("must complete the symbol field")

        symbol = request.form.get("symbol")
        
        stocks = lookup(symbol)
        
        # ensure symbol exists
        if stocks == None:
            return apology("no stock was found")

        return render_template("quoted.html", stock=stocks)

    # reached route via GET (by clicking a link)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # route reached via POST (by submitting register form)
    if request.method == "POST":
        
        # ensure all the field were completed by the user
        if not request.form.get("username"):
            return apology("must complete username field" , 403)
        elif not request.form.get("pass"):
           return apology('must complete password field', 403)
        elif not request.form.get("confirmation"):
            return apology('must complete password confirmation field', 403)

        user = request.form.get("username")
        password = request.form.get("pass")
        conf = request.form.get("confirmation")

        # check if the password was correctly introduced
        if password != conf:
            return apology('passwords does not match')
        
        # ensure username is unique
        rows = db.execute("SELECT * FROM users WHERE username = ?", user)
        if rows != None:
            return apology('username taken')

        # add user into the database
        db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", user, generate_password_hash(password))

        return redirect("/login")
    
    # reached route via GET (by clicking a link)
    else:
        return render_template("register.html")
    

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    # reached route via POST (by submitting sell form)
    if request.method == "POST":

        # check if user completed all the field
        if not request.form.get('symbol'):
            return apology('must select a symbol')
        elif not request.form.get('share'):
            return apology('must complete the share filed')

        symbol = request.form.get('symbol')
        sold_shares = request.form.get('share')

        # check if the submitted number of shares is a valid integer
        if int(sold_shares) < 0 and sold_shares.find('.') != 1:
            return apology('number of shares must be a positive integer')

        stocks = lookup(symbol)
        user_stock = db.execute("SELECT * FROM stocks WHERE id = ? AND symbol = ?", session['user_id'], symbol)

        # ensure the number of shares is available to sell
        if int(sold_shares) > user_stock[0]['shares']:
            return apology("can't sell this number of shares")

        # calculate the number of shares after selling
        new_shares = user_stock[0]['shares'] - int(sold_shares)

        # calculate the total of the sold stock
        total_sold = int(sold_shares) * stocks['price']

        # updates the user cash after selling
        db.execute("UPDATE users SET cash = cash + ? WHERE id = ?", total_sold, session['user_id'])

        # add action in user's history
        date = str(datetime.now().replace(microsecond=0))
        db.execute("INSERT INTO history (id, symbol, shares, price, action, date) VALUES (?, ?, ?, ?, ?, ?)",
                    session['user_id'], stocks['symbol'], int(sold_shares), stocks['price'], "SELL", date)
        
        # update user's stock after selling
        db.execute("UPDATE stocks SET shares = ?, price = ?, total = total - ? WHERE id = ? and symbol = ?",
                    new_shares, stocks['price'], total_sold, session['user_id'], symbol)        

        return redirect("/")

    # reached the route via GET (by clicking a link)
    else:
        user_symbols = []

        # extract user's owned stocks symbols
        user_stocks = db.execute("SELECT * FROM stocks WHERE id = ?", session['user_id'])
        for sym in user_stocks:
            user_symbols.append(sym['symbol'])
    
        return render_template("sell.html", symbols=user_symbols)


@app.route('/change-password', methods = ['GET', 'POST'])
def change_pass():
    """Change user's password"""
    
    # route reached via POST (by submitting change-password form)
    if request.method == "POST":

        # ensure user has completed all the fields    
        if not request.form.get('username'):
            return apology('must complete the username field', 403)
        elif not request.form.get('old'):
            return apology('must complete the old password field', 403)
        elif not request.form.get('new'):
            return apology('must complete the new password field', 403)
        elif not request.form.get('conf'):
            return apology('must confirm the new password', 403)

        username = request.form.get('username')
        old_pass = request.form.get('old')
        new_pass = request.form.get('new')
        conf_pass = request.form.get('conf')

        # ensure new password confirmation
        if new_pass != conf_pass:
            return apology("passwords didn't match")

        user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # ensure user existence
        if user == None:
            return apology("user doesn't exits")

        # check user's old password
        if not check_password_hash(user[0]['hash'], old_pass):
            return apology("wrong password")

        # update user's password with the new one
        db.execute("UPDATE users SET hash = ? WHERE username = ?", generate_password_hash(new_pass), username)

        return redirect("/login")

    # reached route via GET (by clicking a link)
    else:

        return render_template("change_password.html")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run(debug=True)
