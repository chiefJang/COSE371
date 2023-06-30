import psycopg2
from flask import Flask, render_template, request

app = Flask(__name__)
connect = psycopg2.connect("dbname=termproject5 user=postgres password=wkdwldbs980")
cur = connect.cursor()  # create cursor


def rating_update(value):
    if value >= 500000:
        return "gold"
    elif value < 500000 and value >= 100000:
        return "silver"
    elif value < 100000 and value >= 50000:
        return "bronze"
    elif value < 50000 and value >= 0:
        return "welcome"


@app.route("/")
def main():
    return render_template("main.html")


@app.route("/return", methods=["post"])
def re_turn():
    return render_template("main.html")


@app.route("/register", methods=["post"])
def register():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]

    if send == "login":
        cur.execute("select * from users;")
        result = cur.fetchall()

        if (id, password) in result:
            cur.execute(
                "select subject_name, lecture_name, tutor from enrollment, subject where enrollment.code = subject.code group by subject_name, tutor, lecture_name having count(tutee) >= all(select count(tutee) from enrollment group by code, tutor, lecture_name);"
            )
            popular = cur.fetchall()
            cur.execute("select * from account where id = '{}';".format(id))
            accounts = cur.fetchall()
            cur.execute(
                "select code, name, price, tutor from lecture where (code, name, price, tutor) not in (select code, lecture_name, lecture_price, tutor from enrollment where tutee = '{}');".format(
                    id
                )
            )
            lecs = cur.fetchall()
            print("lecs : ", lecs)
            return render_template(
                "login_success.html",
                popular=popular,
                accounts=accounts,
                lecs=lecs,
                ids=id,
                passwords=password,
            )
        else:
            return render_template("main.html")

    elif send == "sign up":
        return render_template("sign_up.html")


@app.route("/sign_up", methods=["post"])
def sign_up():
    id = request.form["id"]
    password = request.form["password"]
    role = request.form["role"]
    send = request.form["send"]

    if send == "sign up":
        cur.execute("select * from users;")
        result = cur.fetchall()
        for i in result:
            if id == i[0]:
                print("ERROR, ID already exists")
                return render_template("main.html")
        cur.execute("insert into users values('{}', '{}');".format(id, password))
        cur.execute(
            "insert into account values('{}', {}, '{}', '{}');".format(
                id, 10000, "welcome", role
            )
        )
        connect.commit()
        print("Success, Let's login")
        return render_template("main.html")


@app.route("/account_termination", methods=["post"])
def account_termination():
    return render_template("account_termination.html")


@app.route("/account_termination_real", methods=["post"])
def account_termination_real():
    id = request.form["id"]
    password = request.form["password"]
    cur.execute(
        "select id, password from users where id = '{}' and password = '{}';".format(
            id, password
        )
    )
    sel = cur.fetchall()
    if sel != [] and sel[0][0] == id and sel[0][1] == password:
        cur.execute(
            "delete from evaluation where tutee = '{}' or tutor = '{}';".format(id, id)
        )
        cur.execute(
            "delete from enrollment where tutee = '{}' or tutor = '{}';".format(id, id)
        )
        cur.execute("delete from lecture where tutor = '{}';".format(id))
        cur.execute("delete from account where id = '{}';".format(id))
        cur.execute(
            "delete from users where id = '{}' and password = '{}';".format(
                id, password
            )
        )
        connect.commit()
        return render_template("main.html")
    return render_template("main.html")


@app.route("/admin_function", methods=["post"])
def admin_function():
    send = request.form["send"]
    id = request.form["id"]
    password = request.form["password"]
    if id == "admin" and password == "0000":
        if send == "users info":
            cur.execute("select * from account;")
            users = cur.fetchall()
            return render_template(
                "admin_user_info.html", users=users, ids=id, passwords=password
            )
        elif send == "trades info":
            cur.execute("select * from enrollment;")
            enroll = cur.fetchall()
            return render_template(
                "admin_trades_info.html", enroll=enroll, ids=id, passwords=password
            )
    else:
        return render_template("main.html")


@app.route("/user_info", methods=["post"])
def user_info():
    send = request.form["send"]
    if send == "Logout":
        return render_template("main.html")


@app.route("/view_lecture", methods=["post"])
def my_info():
    send = request.form["send"]
    role = request.form["role"]
    id = request.form["id"]
    password = request.form["password"]
    if send == "my info":
        if role == "tutor":
            cur.execute(
                "select subject_name, lecture_name, tutee, lecture_price from subject, enrollment where subject.code = enrollment.code and tutor = '{}';".format(
                    id
                )
            )
            my_lecture = cur.fetchall()
            cur.execute(
                "select subject_name, lecture_name, tutor, lecture_price from subject, enrollment where subject.code = enrollment.code and tutee = '{}';".format(
                    id
                )
            )
            Registered_lecture = cur.fetchall()
            return render_template(
                "my_info_tutor.html",
                my_lecture=my_lecture,
                Registered_lecture=Registered_lecture,
                ids=id,
                passwords=password,
            )
        elif role == "tutee":
            cur.execute(
                "select subject_name, lecture_name, tutor, lecture_price from subject, enrollment where subject.code = enrollment.code and tutee = '{}';".format(
                    id
                )
            )
            my_lecture = cur.fetchall()
            return render_template(
                "my_info_tutee.html",
                my_lecture=my_lecture,
                ids=id,
                passwords=password,
            )


@app.route("/lectures", methods=["post"])
def lectures_():
    send = request.form["send"]
    role = request.form["role"]
    id = request.form["id"]
    password = request.form["password"]
    if send == "add":
        if role == "tutor":
            cur.execute("select * from subject;")
            subjects = cur.fetchall()
            return render_template(
                "add_lecture.html", subjects=subjects, ids=id, passwords=password
            )
        elif role == "tutee":
            return render_template("main.html")


@app.route("/add_lecture", methods=["post"])
def add_lecture():
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["id"]
    id = request.form["id"]
    password = request.form["password"]
    cur.execute("select * from subject;")
    code_exist = cur.fetchall()
    code_exist = [item[0] for item in code_exist]
    if code in code_exist:
        cur.execute(
            "insert into lecture values('{}', '{}', {}, '{}');".format(
                code, name, price, tutor
            )
        )
        connect.commit()
    return render_template("return.html", ids=id, passwords=password)


@app.route("/register_lecture", methods=["post"])
def register_lecture():
    send = request.form["send"]
    id = request.form["id"]
    password = request.form["password"]
    code = request.form["code"]
    name = request.form["name"]
    tutor = request.form["tutor"]
    price = int(request.form["price"])
    if send == "register":
        cur.execute(
            "select id, credit, rating, role from account where id = '{}';".format(id)
        )
        account = cur.fetchall()
        credit = account[0][1]
        rating = account[0][2]
        cur.execute(
            "select rating, condition, discount from rating_info where rating = '{}';".format(
                rating
            )
        )
        rating_info = cur.fetchall()
        discount = rating_info[0][2]

        lec = [code, name, price, tutor]
        discount_price = price * discount / (100)
        final_price = price * (100 - discount) / (100)
        return render_template(
            "Register_lecture.html",
            lec=lec,
            credit=credit,
            rating=rating,
            discount_price=discount_price,
            final_price=final_price,
            ids=id,
            passwords=password,
        )


@app.route("/register_confirm", methods=["post"])
def register_confirm():
    id = request.form["id"]
    password = request.form["password"]
    code = request.form["code"]
    name = request.form["name"]
    tutor = request.form["tutor"]
    final_price = float(request.form["final_price"])
    credit = int(request.form["credit"])
    price = int(request.form["price"])
    cur.execute(
        "select tutee from enrollment where tutor = '{}' and code = '{}' and lecture_name = '{}';".format(
            tutor, code, name
        )
    )
    enroll = cur.fetchall()
    if (id == tutor) or (final_price > credit) or (id in enroll):
        return render_template("main.html")
    else:
        cur.execute(
            "update account set credit = credit - {} where id = '{}';".format(
                final_price, id
            )
        )
        cur.execute(
            "update account set credit = credit + {} where id = '{}';".format(
                price, tutor
            )
        )

        cur.execute(
            "update account set rating = '{}' where id = '{}';".format(
                rating_update(credit - final_price), id
            )
        )
        cur.execute("select * from account where id = '{}';".format(tutor))
        tutor_credit = (cur.fetchall())[0][1]
        cur.execute(
            "update account set rating = '{}' where id = '{}';".format(
                rating_update(tutor_credit + price), tutor
            )
        )
        cur.execute(
            "insert into enrollment values('{}', '{}','{}', '{}', {});".format(
                id, tutor, code, name, price
            )
        )
        connect.commit()
        cur.execute("select * from enrollment where tutee = '{}';".format(id))
        enrolls = cur.fetchall()
        return render_template(
            "enrollment_confirm.html", ids=id, passwords=password, enrolls=enrolls
        )


@app.route("/evaluation", methods=["post"])
def evaluation():
    id = request.form["id"]
    password = request.form["password"]
    cur.execute(
        "select code, lecture_name, lecture_price, tutor from enrollment where tutee = '{}';".format(
            id
        )
    )
    lecs_enroll = cur.fetchall()
    cur.execute(
        "select code, name, price, tutor from lecture where (code, name, price, tutor) not in (select code, lecture_name, lecture_price, tutor from enrollment where tutee = '{}');".format(
            id
        )
    )
    lecs_not_enroll = cur.fetchall()
    return render_template(
        "eval.html",
        ids=id,
        passwords=password,
        lecs_enroll=lecs_enroll,
        lecs_not_enroll=lecs_not_enroll,
    )


@app.route("/lecture_eval", methods=["post"])
def lecture_eval():
    id = request.form["id"]
    password = request.form["password"]
    send = request.form["send"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["tutor"]
    # evaluation 이라는 schema (tutee, code, name, price, tutor, message)
    if send == "view":
        cur.execute(
            "select message from evaluation where code = '{}' and name = '{}' and price = {} and tutor = '{}';".format(
                code, name, price, tutor
            )
        )
        lecs = cur.fetchall()
        return render_template(
            "view_lecture_eval.html", lecs=lecs, ids=id, passwords=password
        )
    elif send == "write":
        cur.execute(
            "select tutee, code from evaluation where tutee = '{}' and code = '{}' and name = '{}' and price = {} and tutor = '{}';".format(
                id, code, name, price, tutor
            )
        )
        sel = cur.fetchall()
        if sel != [] and sel[0][0] == id:
            return render_template("return.html", ids=id, passwords=password)

        return render_template(
            "write_lecture_eval.html",
            ids=id,
            passwords=password,
            code=code,
            name=name,
            price=price,
            tutor=tutor,
        )


@app.route("/write_eval", methods=["post"])
def write_eval():
    id = request.form["id"]
    password = request.form["password"]
    code = request.form["code"]
    name = request.form["name"]
    price = request.form["price"]
    tutor = request.form["tutor"]
    message = request.form["message"]
    cur.execute(
        "insert into evaluation values('{}', '{}', '{}', {}, '{}', '{}');".format(
            id, code, name, price, tutor, message
        )
    )
    connect.commit()
    return render_template("return.html", ids=id, passwords=password)


if __name__ == "__main__":
    app.run()
