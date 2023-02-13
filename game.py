import mysql.connector

yhteys = mysql.connector.connect(
    host='localhost',
    port='3306',
    database='demogame',
    user='user1',
    password='sala1',
    autocommit=True)