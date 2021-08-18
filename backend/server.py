from flask import abort, g, jsonify, request, Flask
import os
from sqlite3 import connect
import itertools

app = Flask(__name__)

DATABASE = os.getenv('DB_LOC', '../database/students.db')


def get_db():
    db = getattr(g, '_database', None)
    print("DB")
    if db is None:
        db = g._database = connect(DATABASE)
    return db


def jsonify_single_student(result):
    return {
        'i': result[0],
        'u': result[1],
        'n': result[2],
        'p': result[3],
        'd': result[4],
        'h': result[5],
        'r': result[6],
        'b': result[7],
        'g': result[8],
        'a': result[9]
    }


def jsonify_multiple_students(results):
    return list(map(lambda result: jsonify_single_student(result), results))


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/students')
def get_all_students():
    db = get_db()
    c = db.cursor()
    c.execute("SELECT * FROM students")
    results = c.fetchall()
    return jsonify(jsonify_multiple_students(results))


@app.route('/student')
def get_particular_student():
    username = request.args.get('username')

    nameSplit = username.split()    # Split the name into seperate words
    all_combinations = []

    # Generate all possible combinations of the name in a list
    for r in range(len(nameSplit) + 1):
        combinations_object = itertools.combinations(nameSplit, r)
        combinations_list = list(combinations_object)
        all_combinations += combinations_list

    # Concatenate all the seperate combinations into seperate strings for searching
    y = []
    for i in (all_combinations):
        s = ""
        if len(i) > 0:
            for j in i:
                s += str(j)
            y.append(s)
    searchNames = tuple(y)

    # making of the query
    lengthNamesList = len(searchNames)
    count = 0
    query = "SELECT * FROM students WHERE username IN "
    for i in searchNames:
        count += 1
        if count < lengthNamesList:
            query += "('" + i + "') OR username IN "
        elif count == lengthNamesList:
            query += "('" + i + "')"

    roll = request.args.get('roll')
    if((username == None or username == '') and (roll == None or roll == '')):
        abort(400)
    db = get_db()
    c = db.cursor()
    if username:
        print(username)
        c.execute(query)
    else:
        print(roll)
        c.execute("SELECT * FROM students WHERE roll IS ?", (roll, ))
    result = c.fetchone()
    if result is None:
        abort(404)
    return jsonify(jsonify_single_student(result))
