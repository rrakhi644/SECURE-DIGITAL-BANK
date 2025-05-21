from flask import Flask, render_template, request, redirect, url_for, flash
from database import DbTask
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Create database connection
db_task = DbTask()
db_connect = db_task.creating_connection()
cursor = db_connect.cursor()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        name = request.form.get('name')
        ph = request.form.get('mobile')
        city = request.form.get('city')
        pin = request.form.get('pin')
        pin2 = request.form.get('pin2')

        if not all([name, ph, city, pin, pin2]):
            flash('Please fill all fields', 'danger')
            return render_template('create_account.html')

        try:
            pin = int(pin)
            pin2 = int(pin2)
        except ValueError:
            flash('PIN must be a number', 'danger')
            return render_template('create_account.html')

        if pin != pin2:
            flash('PIN numbers do not match', 'danger')
            return render_template('create_account.html')

        cursor.execute("SELECT ACCOUNT_ID FROM ACCOUNTS")
        existing_ids = [row[0] for row in cursor.fetchall()]
        ac = random.randint(1000000, 9999999)
        while ac in existing_ids:
            ac = random.randint(1000000, 9999999)

        try:
            cursor.execute("INSERT INTO ACCOUNTS VALUES (%s, %s, %s, %s, %s, %s, NOW())",
                           (ac, name, ph, city, pin, 500))
            db_connect.commit()
            flash(f'Account created successfully with account number {ac}', 'success')
        except Exception as e:
            db_connect.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')

        return render_template('create_account.html')

    return render_template('create_account.html')

@app.route('/balance_enquiry', methods=['GET', 'POST'])
def balance_enquiry():
    if request.method == 'POST':
        ac = request.form.get('account_id')
        pin = request.form.get('pin')

        if not ac or not pin:
            flash('Please fill all fields', 'danger')
            return render_template('balance_enquiry.html')

        try:
            ac = int(ac)
            pin = int(pin)
        except ValueError:
            flash('Account ID and PIN must be numbers', 'danger')
            return render_template('balance_enquiry.html')

        cursor.execute("SELECT PIN, BALANCE FROM ACCOUNTS WHERE ACCOUNT_ID=%s", (ac,))
        result = cursor.fetchone()

        if result:
            if pin == result[0]:
                flash(f'Current Balance: ₹{result[1]:.2f}', 'success')
            else:
                flash('Incorrect PIN number', 'danger')
        else:
            flash('Account not found', 'danger')

    return render_template('balance_enquiry.html')

@app.route('/credit', methods=['GET', 'POST'])
def credit():
    if request.method == 'POST':
        ac = request.form.get('account_id')
        amount = request.form.get('amount')

        if not ac or not amount:
            flash('Please fill all fields', 'danger')
            return render_template('credit.html')

        try:
            ac = int(ac)
            amount = float(amount)
        except ValueError:
            flash('Account ID and amount must be valid numbers', 'danger')
            return render_template('credit.html')

        cursor.execute("SELECT ACCOUNT_ID FROM ACCOUNTS WHERE ACCOUNT_ID = %s", (ac,))
        if cursor.fetchone():
            try:
                cursor.execute("INSERT INTO TRANSACTIONS (AC_ID, AMOUNT, TRANS_DATE) VALUES (%s, %s, NOW())", (ac, amount))
                cursor.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE + %s WHERE ACCOUNT_ID = %s", (amount, ac))
                db_connect.commit()
                flash('Amount credited successfully', 'success')
            except Exception as e:
                db_connect.rollback()
                flash(f'Error crediting amount: {str(e)}', 'danger')
        else:
            flash('Account not found', 'danger')

    return render_template('credit.html')

@app.route('/debit', methods=['GET', 'POST'])
def debit():
    if request.method == 'POST':
        ac = request.form.get('account_id')
        amount = request.form.get('amount')
        pin = request.form.get('pin')

        if not all([ac, amount, pin]):
            flash('Please fill all fields', 'danger')
            return render_template('debit.html')

        try:
            ac = int(ac)
            amount = float(amount)
            pin = int(pin)
        except ValueError:
            flash('Invalid input values', 'danger')
            return render_template('debit.html')

        cursor.execute("SELECT BALANCE, PIN FROM ACCOUNTS WHERE ACCOUNT_ID = %s", (ac,))
        result = cursor.fetchone()

        if result:
            balance, correct_pin = result
            if pin != correct_pin:
                flash('Incorrect PIN', 'danger')
            elif amount > balance:
                flash('Insufficient balance', 'danger')
            else:
                try:
                    cursor.execute("INSERT INTO TRANSACTIONS (AC_ID, AMOUNT, TRANS_DATE) VALUES (%s, %s, NOW())", (ac, -amount))
                    cursor.execute("UPDATE ACCOUNTS SET BALANCE = BALANCE - %s WHERE ACCOUNT_ID = %s", (amount, ac))
                    db_connect.commit()
                    flash('Amount debited successfully', 'success')
                except Exception as e:
                    db_connect.rollback()
                    flash(f'Error debiting amount: {str(e)}', 'danger')
        else:
            flash('Account not found', 'danger')

    return render_template('debit.html')

@app.route('/change_pin', methods=['GET', 'POST'])
def change_pin():
    if request.method == 'POST':
        ac = request.form.get('account_id')
        old_pin = request.form.get('old_pin')
        new_pin = request.form.get('new_pin')
        new_pin2 = request.form.get('new_pin2')

        if not all([ac, old_pin, new_pin, new_pin2]):
            flash('Please fill all fields', 'danger')
            return render_template('change_pin.html')

        try:
            ac = int(ac)
            old_pin = int(old_pin)
            new_pin = int(new_pin)
            new_pin2 = int(new_pin2)
        except ValueError:
            flash('All PINs and Account ID must be numbers', 'danger')
            return render_template('change_pin.html')

        if new_pin != new_pin2:
            flash('New PINs do not match', 'danger')
            return render_template('change_pin.html')

        cursor.execute("SELECT PIN FROM ACCOUNTS WHERE ACCOUNT_ID = %s", (ac,))
        result = cursor.fetchone()

        if result and old_pin == result[0]:
            try:
                cursor.execute("UPDATE ACCOUNTS SET PIN = %s WHERE ACCOUNT_ID = %s", (new_pin, ac))
                db_connect.commit()
                flash('PIN changed successfully', 'success')
            except Exception as e:
                db_connect.rollback()
                flash(f'Error changing PIN: {str(e)}', 'danger')
        else:
            flash('Incorrect old PIN or account not found', 'danger')

    return render_template('change_pin.html')

@app.route('/view_transactions', methods=['GET', 'POST'])
def view_transactions():
    if request.method == 'POST':
        ac = request.form.get('account_id')

        if not ac:
            flash('Please enter an account ID', 'danger')
            return render_template('view_transactions.html')

        try:
            ac = int(ac)
        except ValueError:
            flash('Account ID must be a number', 'danger')
            return render_template('view_transactions.html')

        cursor.execute("SELECT * FROM ACCOUNTS WHERE ACCOUNT_ID = %s", (ac,))
        if cursor.fetchone():
            cursor.execute("SELECT TRANSACTION_ID, AMOUNT, TRANS_DATE FROM TRANSACTIONS WHERE AC_ID = %s", (ac,))
            transactions = cursor.fetchall()

            transactions_list = [{
                'transaction_id': t[0],
                'amount': t[1],
                'trans_date': t[2].strftime('%Y-%m-%d %H:%M:%S')
            } for t in transactions]

            return render_template('view_transactions.html', transactions=transactions_list)
        else:
            flash('Account not found', 'danger')

    return render_template('view_transactions.html')

if __name__ == '__main__':
    app.run(debug=True)
