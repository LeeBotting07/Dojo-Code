import sqlite3
from flask_bcrypt import Bcrypt


username = "test"
email = "test@test.ac.uk"
password = "password"
hashed_password = Bcrypt().generate_password_hash(password).decode('utf-8')
firstName = "test"
lastName = "test"
phoneNumber = "0123456789"
address = "test"

with sqlite3.connect("dojoproject.db") as con:
    cur = con.cursor()
    cur.execute("INSERT INTO accountInfo (username, email, password, firstName, lastName, phoneNumber, address) VALUES (?,?,?,?,?,?,?)",
                (username, email , hashed_password, firstName, lastName, phoneNumber, address))
            

