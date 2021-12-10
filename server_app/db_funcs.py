import sqlite3
# from hashlib import sha256


def sign_in(conn, name, password, cur):
    req = cur.execute(f"""SELECT Name FROM Users
WHERE Name = '{name}' AND Password = '{password}'""").fetchone()
    # проверка на существование аккаунта
    if req:
        return 'ok'
    return 'Неверное имя или пароль'


def register(conn, name, password, email, cur):
    req = cur.execute(f"""SELECT Name FROM Users WHERE Name = '{name}'""").fetchall()  # занято имя?
    if req:
        return 'Имя уже занято'
    cur.execute(f"""INSERT INTO Users(Name, Password, Email, Rating) VALUES('{name}',
     '{password}', '{email}', 0)""")
    conn.commit()
    return 'ok'


def change_name(conn, old_name, new_name, cur):
    req = cur.execute(f"""SELECT Name FROM Users WHERE Name = '{old_name}'""").fetchall()
    new = cur.execute(f"""SELECT Name FROM Users WHERE Name = '{new_name}'""").fetchall()
    if new:
        return 'Имя уже занято'
    # проверка на существование имени
    if req:
        cur.execute(f"""UPDATE Users SET Name = '{new_name}' WHERE Name = '{old_name}'""")
        conn.commit()
        return 'ok'
    return 'такого имени не существует'


