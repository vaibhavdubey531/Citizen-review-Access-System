from flask import Flask, render_template, request, send_file,redirect,session
import sqlite3
import pandas as pd
from io import BytesIO
import os

# for passwords
from credentials import user_and_passwords

app = Flask(__name__)
app.secret_key = os.urandom(24)

def create_table():
    connection = sqlite3.connect('citizen_review.db',timeout=10)
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS citizen_review (
            sr_no INTEGER PRIMARY KEY AUTOINCREMENT,
            citizen_id INT UNIQUE,
            citizen_name TEXT,
            gender TEXT,
            scheme TEXT,
            review TEXT
        )
    ''')
    connection.commit()
    connection.close()

# to read the data
def read_data():
    connection = sqlite3.connect('citizen_review.db',timeout=10)
    cursor = connection.cursor()

    # Fetch all records from the citizen_review table
    cursor.execute('SELECT * FROM citizen_review')
    data = cursor.fetchall()

    connection.close()

    return data

@app.route('/delete_data')
def delete_data():
    if "username" in session:
        connection = sqlite3.connect('citizen_review.db',timeout=10)
        cursor = connection.cursor()

        # delete all records from the table
        cursor.execute('DELETE FROM citizen_review')
        connection.commit()
        cursor.close()

        # return "<h1>Records are deleted successfully</h1>"
        info="Records are deleted!!"
        return render_template("data.html",info=info)
    else:
        return redirect("/login")

@app.route('/get_data', methods=['GET'])
def get_data():
    if "username" in session:
        connection = sqlite3.connect('citizen_review.db',timeout=10)
        cursor = connection.cursor()

        # Fetch all records from the citizen_review table
        cursor.execute('SELECT * FROM citizen_review')
        data = cursor.fetchall()

        cursor.close()
        connection.close()

        return render_template('data.html', data=data)
    else:
        return redirect("/login")

@app.route('/download_excel', methods=['GET'])
def download_excel():
    if "username" in session:
        connection = sqlite3.connect('citizen_review.db',timeout=10)

        # Fetch all records from the citizen_reviews table
        query = 'SELECT * FROM citizen_review'
        df = pd.read_sql_query(query, connection)
        # df.to_excel("Citizen_Data.xlsx",index=False,engine="openpyxl")
        connection.close()

        # Convert DataFrame to Excel
        excel_output = BytesIO()
        df.to_excel(excel_output, index=False, engine='openpyxl')
        excel_output.seek(0)

        return send_file(excel_output, download_name='citizen_data.xlsx', as_attachment=True)
        # return "Data is stored in file"
    else:
        return redirect('/login')

@app.route('/', methods=['GET', 'POST'])
def citizen_review_form():
    if request.method == 'POST':
        citizen_id = request.form['citizenId']
        citizen_name = request.form['citizenName']
        gender = request.form['gender']
        scheme = request.form['schemes']
        review = request.form['review']

        connection = sqlite3.connect('citizen_review.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO citizen_review (citizen_id, citizen_name, gender, scheme, review)
            VALUES (?, ?, ?, ?, ?)
        ''', (citizen_id, citizen_name, gender, scheme, review))
        connection.commit()
        cursor.close()
        connection.close()

        # return 'Form submitted successfully!'
        warning="Form Submitted. Submit Another"
        return render_template("index.html",warning=warning)

    return render_template('index.html')

# login form
@app.route("/login",methods=['GET', 'POST'])
def login_form():
    if "username" not in session:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            # Replace with your actual authentication logic
            if username in user_and_passwords and user_and_passwords[username] == password:
                session['username'] = username
                # Example: Redirect to a dashboard or home page
                return redirect("/get_data")
            else:
                # Example: Display error message or redirect to login page\
                data="Try again with correct credentials!!"
                return render_template('login.html',data=data)
    else:
        # return render_template("data.html")
        return redirect("/get_data")

    # If GET request or login failed, render the login form
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop("username",None)
    return redirect("/")

# app.run(debug=True)
if __name__ == '__main__':
    try:
        create_table()
        app.run(debug=True)
        # result=read_data()
        # for row in result:
        #     print(row)
    except Exception as e:
        print(f"Error occurred {str(e)}")