import csv
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
 
app.config['SECRET_KEY'] = 'hardsecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(50), unique=True)
    psw = db.Column(db.String(500), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    pr = db.relationship('Profiles', backref='users', uselist=False)
    # def __init__(self, email, psw):
    #     self.email = email
    #     self.psw = psw
    def __repr__(self):
        return f"<users {self.id}>"


class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer)
    city = db.Column(db.String(100))

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    # def __init__(self, name, old, city):
    #     self.name = name
    #     self.old = old
    #     self.city = city
    def __repr__(self):
        return f"<profiles {self.id}>"


@app.route("/")
def index():
    info = []
    try:
        info = Users.query.all()
        # print(type(info))
        print(info)
    except:
        print("Ошибка чтения из БД")

    return render_template("index.html", title="Главная", list=info)

@app.route("/tocsv")
def tocsv():
    info = []
    try:
        info = Profiles.query.all()
        # print(type(info))
        res = []
        for u in info:
            lst = []
            lst.append(u.id)
            lst.append(u.name)
            lst.append(u.old)
            lst.append(u.city)
            res.append(lst)
        print(res)
        with open('data_file.csv', mode='w') as data_file:
            data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            data_writer.writerow(["id","name","old","city"])
            for ls in res:
                data_writer.writerow(ls)
    except:
        print("Ошибка чтения из БД")

    return "Профили сохранены в файл csv"


@app.route("/register", methods=("POST", "GET"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            
            print(form.psw.data)
            hash = generate_password_hash(form.psw.data, method = 'sha256')
            print(hash)
            u = Users(email=form.email.data, psw=hash)
            print(u)
            db.session.add(u)
            db.session.flush()
            p = Profiles(name=form.name.data, old=form.old.data,
                         city=form.city.data, user_id = u.id)
            print(p)
            db.session.add(p)
            db.session.commit()
        except:
            db.session.rollback()
            print("Ошибка добавления в БД")

        return redirect(url_for('index'))

    return render_template("register.html", form=form, title="Регистрация")


if __name__ == "__main__":
    app.run(debug=True)
