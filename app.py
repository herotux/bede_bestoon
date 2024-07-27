import datetime
import json
import ast
from tkinter.messagebox import RETRY
from flask import Flask, render_template, redirect, url_for, request, flash, json
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
import jalali
from persiantools.jdatetime import JalaliDate
from persiantools import characters, digits
from sqlalchemy import UniqueConstraint
from flask_wtf import FlaskForm
from wtforms import DateField, SelectField
from wtforms.validators import DataRequired
from sqlalchemy.exc import IntegrityError
from persian_tools import separator
from datetime import datetime, timedelta, date

    
app = Flask(__name__)
app.config['SECRET_KEY'] = 'sooraneh'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sooraneh.sqlite3'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
migrate = Migrate(app, db)


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    persons = db.relationship('Persons', backref='user', lazy=True)
    income = db.relationship('Income', backref='user', lazy=True)
    expense = db.relationship('Expense', backref='user', lazy=True)
    tag = db.relationship('Tags', backref='user')
    categories = db.relationship("Category", backref="user")
    accounts = db.relationship("Account", backref="user")
    debts = db.relationship("Debt", backref="user")
    credites = db.relationship("Credit", backref="user")

class Persons(db.Model):
    __tablename__ = "persons"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=True)
    relation = db.Column(db.String(60), nullable=False)

class Income(db.Model):
    __tablename__ = "income"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    person = db.Column(db.Integer, db.ForeignKey('persons.id'), nullable=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(10), nullable=False)
    text = db.Column(db.String(30), nullable=False)
    tag = db.relationship('Tags', backref='income')
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

class Expense(db.Model):
    __tablename__ = "expense"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), db.ForeignKey('user.username'), nullable=False)
    person = db.Column(db.String(20), db.ForeignKey('persons.id'), nullable=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(10), nullable=False)
    text = db.Column(db.String(30), nullable=False)
    tag = db.relationship('Tags', backref='expense')
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    


class Tags(db.Model):
    __tablename__ = "tags"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    description = db.Column(db.String(100), nullable=True)


class Budget(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    monthly_budget = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    parent_id = db.Column(db.Integer, db.ForeignKey('category.id'), nullable=True)
    children = db.relationship("Category")

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

class Debt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person = db.Column(db.String(20), db.ForeignKey('persons.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    pay_date = db.Column(db.String(10), nullable=False)

class Credit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person = db.Column(db.String(20), db.ForeignKey('persons.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(30), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    pay_date = db.Column(db.String(10), nullable=False)


class Installments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    person = db.Column(db.String(20), db.ForeignKey('persons.id'), nullable=True)
    amount = db.Column(db.Integer, nullable=False)
    text = db.Column(db.String(30), nullable=True)
    inst_num = db.Column(db.Integer, nullable=False) #Number of installments
    inst_rate = db.Column(db.Integer, nullable=True) #نرخ سود به درصد
    first_date = db.Column(db.String(10), nullable=False)
    pay_period = db.Column(db.Integer, nullable=False) # 1 for month ,2 for 2 month , ...
    inst_data = db.Column(db.JSON, nullable=True)

#مدیریت اقساط
#نام وام مبلغ تعداد اقساط موعد قسط میانگین مبلغ مشاهده اقساط وام پرداخت قسط


    
def is_leap_year_modulo(year):
	if(year%400 == 0):
		result = True
	elif(year%100 == 0):
		result = False
	elif(year%4 == 0):
		result = True
	else:
		result = False

	return result


def is_leap(year):
        
        c = 0.24219858156028368  # 683 / 2820
        # return ((year + 2346) * 683) % 2820 < 683
        return ((year + 2346) * c) % 1 < c	

@app.route('/install', methods=['GET', 'POST'])
@login_required
def install():
    user_id = current_user.id
    username = current_user.username
    installments = Installments.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        return render_template('installments.html',user_id=user_id, installments=installments, persons =persons)
    else:
        person_id = request.form.get('person_id')
        amount = request.form.get('amount')
        inst_num = request.form.get('inst_num')
        text = request.form.get('text')
        inst_rate = request.form.get('inst_rate')
        date = request.form.get('first_date')
        payed_insts = request.form.get('payed_insts')
        first_date = gdate_str(date)
        pay_period = request.form.get('pay_period')
        date_for_loop = gdate_date(date)
        inst_list = []
        #this loop is for calculate date 30 days apart for each installments and save thems in a list 
        for i in range(int(inst_num)):
            amount_inst = calculate_inst(int(amount), int(inst_rate), int(inst_num))
            #amount_inst = gharzhsane_inst(amount, inst_rate, inst_num)
            jdate_in_loop = jalali.Gregorian(date_for_loop).persian_tuple()
            jmonth_inloop = jdate_in_loop[1]
            if jmonth_inloop < 7:
                days = 31
            elif jmonth_inloop > 6 and jmonth_inloop < 12:
                days = 30
            
            elif jmonth_inloop == 12 and is_leap(jdate_in_loop[0]):
                days = 30
            else:
                days = 29
            if payed_insts:
                pay_hist = compare_date_pay(date_for_loop)
            else:
                pay_hist = "notpayed"

            date_for_loop = date_for_loop + timedelta(days = days)
            installment_date = date_for_loop
            inst_list.append([i, pay_hist, installment_date.strftime("%Y-%m-%d"), round(amount_inst)])
        inst_list = json.dumps(inst_list)
            
        install = Installments(user_id=user_id, person=person_id, amount=amount, text=text, first_date=first_date,
                                    pay_period=pay_period, inst_data=inst_list, inst_rate=inst_rate, inst_num=inst_num)
        db.session.add(install)
        db.session.commit()
        flash('installment added successful!', 'success')
        return redirect(url_for('install'))

@app.route('/install_spec', methods=['GET', 'POST'])
@login_required
def install_spec():
    user_id = current_user.id
    username = current_user.username
    installments = Installments.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'POST':
        person_id = request.form.get('person_id')
        amount = request.form.get('amount')
        inst_num = request.form.get('inst_num')
        text = request.form.get('text')
        inst_rate = request.form.get('inst_rate')
        date = request.form.get('first_date')
        payed_insts = request.form.get('payed_insts')
        first_date = gdate_str(date)
        pay_period = request.form.get('pay_period')
        date_for_loop = gdate_date(date)
        inst_list = []
        amount_inst_list = gharzhsane_inst(amount, inst_rate, inst_num)
        #this loop is for calculate date 30 days apart for each installments and save thems in a list 
        i =1
        while i <= int(inst_num):
            #amount_inst = calculate_inst(int(amount), int(inst_rate), int(inst_num))
            for item in amount_inst_list:
                if item[0] == i:
                    amount_inst = item[1]
                    break
                else:
                    amount_inst = int(amount)/(int(inst_num) - int(inst_num)/12)

            jdate_in_loop = jalali.Gregorian(date_for_loop).persian_tuple()
            jmonth_inloop = jdate_in_loop[1]
            if jmonth_inloop < 7:
                days = 31
            elif jmonth_inloop > 6 and jmonth_inloop < 12:
                days = 30
            
            elif jmonth_inloop == 12 and is_leap(jdate_in_loop[0]):
                days = 30
            else:
                days = 29
            if payed_insts:
                pay_hist = compare_date_pay(date_for_loop)
            else:
                pay_hist = "notpayed"

            
            installment_date = date_for_loop
            inst_list.append([i, pay_hist, installment_date.strftime("%Y-%m-%d"), round(amount_inst)])
            date_for_loop = date_for_loop + timedelta(days = days)
            i+=1
        inst_list = json.dumps(inst_list)
            
        install = Installments(user_id=user_id, person=person_id, amount=amount, text=text, first_date=first_date,
                                    pay_period=pay_period, inst_data=inst_list, inst_rate=inst_rate, inst_num=inst_num)
        db.session.add(install)
        db.session.commit()
        flash('installment added successful!', 'success')
        return redirect(url_for('install'))


@app.route('/inst_page/<int:inst_id>')
@login_required
def inst_page(inst_id):
    installment = Installments.query.filter_by(user_id=current_user.id, id = inst_id).first()
    today = datetime.today()

    if installment:
        expired_amount = 0
        expired_count = 0
        payed_amount = 0
        amount = installment.amount
        inst_data = installment.inst_data
        list_data = ast.literal_eval(inst_data)
        first_inst = Installments.first_date
        for item in list_data:
            if item[1] == "payed":
                payed_amount += int(item[3])      
            else:
                date_object = datetime.strptime(item[2], '%Y-%m-%d')
                if date_object < today:
                    expired_amount += int(item[3])
                    expired_count += 1
        payed_precent = round((payed_amount/amount) *100)
        exp_precent = round((expired_amount/amount) *100)
        return render_template('installment_page.html', inst = installment, list_data=list_data, payed_amount=payed_amount,
         expired_amount=expired_amount, expired_count=expired_count, payed_precent=payed_precent, exp_precent=exp_precent)
    else:
        return render_template('404.html')



@app.route('/delete_inst/<int:inst_id>')
@login_required
def delete_inst(inst_id):
    installment = Installments.query.filter_by(id = inst_id).first()
    if installment:
        db.session.delete(installment)
        db.session.commit()
        print('installment deleted successfully')
        return redirect(url_for('install'))
    else:
        print('installment not found')
        return 'installment not found'


@app.route('/inst_status/<int:inst_id>/<int:inst_num>')
@login_required
def inst_status(inst_id, inst_num):
    installment = Installments.query.filter_by(id = inst_id).first()
    if installment:
        inst_data = installment.inst_data
        inst_data = ast.literal_eval(inst_data)
        print(type(inst_data))
        inst2 = installment
        inst_dataa = inst2.inst_data
        if inst_data[inst_num-1][1] == "notpayed":
           inst_data[inst_num-1][1] = "payed"
        else:
            inst_data[inst_num-1][1] = "notpayed"
        print(inst_data[inst_num-1][1])
        installment.inst_data = json.dumps(inst_data)  # Convert dictionary to JSON string
        db.session.commit()
        print('installment status changed successfully')
        return redirect(url_for('install'))
    else:
        print('installment not found')
        return 'installment not found'



#todo : CRUD for user

#todo : CRUD and routes for Category make html templates for it


@app.route('/category', methods=['GET', 'POST'])
@login_required
def category():
    user_id = current_user.id
    category = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        return render_template('category.html',user_id=user_id, category=category)
    else:
        name = request.form.get('name')
        parent_id = request.form.get('parent_id')
        category = Category(user_id=user_id, name=name, parent_id=parent_id)
        db.session.add(category)
        db.session.commit()
        flash('category added successful!', 'success')
        return redirect(url_for('category'))
    return render_template('category.html',user_id=user_id, category=category)


@app.route('/edit_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def edit_category(category_id):
    user_id = current_user.id
    category = Category.query.get(category_id)
    categories = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        
        if category:
            return render_template('edit_category.html', category=category, categories=categories)
        else:
            return "category not found", 404
    elif request.method == 'POST':
        if category:
            category.name = request.form['name']
            category.parent_id = request.form['parent_id']
            db.session.commit()
            print('category updated successfully')
            return redirect(url_for("category"))
        else:
            return 'category not found'

@app.route('/delete_category/<int:category_id>', methods=['GET', 'POST'])
@login_required
def delete_category(category_id):
    category = Category.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
        print('category deleted successfully')
        return redirect(url_for('category'))
    else:
        print('category not found')
        return 'category not found'

#todo : CRUD and routes for Account make html templates for it


# دیتابیس و .. برای صندوق ها
#نقد صندوق کیف پول منزل و ...
# نام صندوق و مقدار اولیه


#check تغییر وضعیت مبلغ تاریخ بانک وضعیت به کجا؟ شماره چک
#اسناد پرداختنی اسناد دریافتنی


#مدیریت اقساط
#نام وام مبلغ تعداد اقساط موعد قسط میانگین مبلغ مشاهده اقساط وام پرداخت قسط


#CRUD and routes for Debt
@app.route('/debt', methods=['GET', 'POST'])
@login_required
def debt():
    user_id = current_user.id
    username = current_user.username
    debts = Debt.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        return render_template('debt.html',user_id=user_id, debts=debts, persons=persons)
    else:
        person_id = request.form.get('person_id')
        amount = request.form.get('amount')
        text = request.form.get('text')
        jdate = equest.form.get('date')
        pay_date = jalali.Persian(request.form.get('pay_date')).gregorian_string()
        date = date_str(jdate)
        debt = Debt(user_id=user_id, person=person_id, amount=amount, text=text, date=date, pay_date=pay_date)
        db.session.add(debt)
        db.session.commit()
        flash('debt added successful!', 'success')
        return redirect(url_for('debt'))


@app.route('/edit_debt/<int:debt_id>', methods=['GET', 'POST'])
@login_required
def edit_debt(debt_id):
    username = current_user.username
    user_id = current_user.id
    debt = Debt.query.get(debt_id)
    debts = Debt.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        
        if debt:
            return render_template('edit_debt.html', debt=debt, debts=debts, persons = persons)
        else:
            return "debt not found", 404
    elif request.method == 'POST':
        if debt:
            debt.person = request.form['person_id']
            debt.amount = request.form['amount']
            debt.text = request.form['text']
            date = request.form['date']
            paydate = request.form['pay_date']
            gdate = gdate_str(date)
            gpdate = gdate_str(paydate)
            debt.date = gdate
            debt.pay_date = gpdate
            db.session.commit()
            print('debt updated successfully')
            return redirect(url_for("debt"))
        else:
            return 'debbt not found'

@app.route('/delete_debt/<int:debt_id>', methods=['GET', 'POST'])
@login_required
def delete_debt(debt_id):
    debt = Debt.query.get(debt_id)
    if debt:
        db.session.delete(debt)
        db.session.commit()
        print('debt deleted successfully')
        return redirect(url_for('debt'))
    else:
        print('debt not found')
        return 'debt not found'

#todo : CRUD and routes for Credit make html templates for it

@app.route('/credit', methods=['GET', 'POST'])
@login_required
def credit():
    user_id = current_user.id
    username = current_user.username
    credits = Credit.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        return render_template('credit.html',user_id=user_id, credits=credits, persons=persons)
    else:
        person_id = request.form.get('person_id')
        amount = request.form.get('amount')
        text = request.form.get('text')
        jdate = request.form.get('date')
        jpay_date = request.form.get('pay_date')
        date = date_str(jdate)
        pay_date = date_str(jpay_date)
        credit = Credit(user_id=user_id, person=person_id, amount=amount, text=text, date=date, pay_date=pay_date)
        db.session.add(credit)
        db.session.commit()
        flash('credit added successful!', 'success')
        return redirect(url_for('credit'))

@app.route('/edit_credit/<int:credit_id>', methods=['GET', 'POST'])
@login_required
def edit_credit(credit_id):
    username = current_user.username
    user_id = current_user.id
    credit = Credit.query.get(credit_id)
    credits = Credit.query.filter_by(user_id=user_id).all()
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        
        if Credit:
            return render_template('edit_credit.html', credit=credit, credits=credits, persons=persons)
        else:
            return "credit not found", 404
    elif request.method == 'POST':
        if credit:
            credit.person = request.form['person_id']
            credit.amount = request.form['amount']
            jdate = request.form.get('date')
            credit.date = gdate_str(jdate)
            paydate = request.form.get('pay_date')
            credit.pay_date = gdate_str(paydate)
            credit.text = request.form.get('text')
            db.session.commit()
            print('credit updated successfully')
            return redirect(url_for("credit"))
        else:
            return 'credit not found'

@app.route('/delete_credit/<int:credit_id>', methods=['GET', 'POST'])
@login_required
def delete_credit(credit_id):
    credit = Credit.query.get(credit_id)
    if credit:
        db.session.delete(credit)
        db.session.commit()
        print('credit deleted successfully')
        return redirect(url_for('credit'))
    else:
        print('credit not found')
        return 'credit not found'

#crud for person

@app.route('/persons', methods=['GET', 'POST'])
@login_required
def persons():
    username = current_user.username
    persons = Persons.query.filter_by(username=username).all()
    if request.method == 'GET':
        return render_template('persons.html',username=username, persons=persons)
    else:
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        relation = request.form.get('relation')
        person = Persons(username=username, first_name=first_name, last_name=last_name, relation = relation)
        db.session.add(person)
        db.session.commit()
        flash('person added successful!', 'success')
        return redirect(url_for('persons'))
    return render_template('persons.html',username=username, persons=persons)



@app.route('/person_page/<int:person_id>')
@login_required
def person_page(person_id):
    person = Persons.query.filter_by(id =person_id ).first()
    username = current_user.username
    user_id = current_user.id
    incoms = Income.query.filter_by(username=username, person=person_id).all()
    expenses = Expense.query.filter_by(username=username, person=person_id).all()
    debt = Debt.query.filter_by(user_id=user_id, person=person_id).all()
    credit = Credit.query.filter_by(user_id=user_id, person=person_id).all()
    if debt:
        if credit:
            return render_template('dashboard.html', incoms=incoms, username=username, expenses=expenses, person=person, debt=debt, credit=credit)
        else:
            return render_template('dashboard.html', incoms=incoms, username=username, expenses=expenses, person=person, debt=debt)
    else:
        if credit:
            return render_template('dashboard.html', incoms=incoms, username=username, expenses=expenses, person=person, credit=credit)
        else:
            return render_template('dashboard.html', incoms=incoms, username=username, expenses=expenses, person=person)



@app.route('/edit_person/<int:person_id>', methods=['GET', 'POST'])
@login_required
def edit_person(person_id):
    person = Persons.query.get(person_id)
    if request.method == 'GET':
        
        if person:
            return render_template('edit_person.html', person=person)
        else:
            return "User not found", 404
    elif request.method == 'POST':
        if person:
            person.username = request.form['username']
            person.first_name = request.form['first_name']
            person.last_name = request.form['last_name']
            person.relation = request.form['relation']
            
            db.session.commit()
            print('User updated successfully')
            return redirect(url_for("persons"))
        else:
            return 'User not found'



@app.route('/delete_person/<int:person_id>', methods=['GET', 'POST'])
@login_required
def delete_person(person_id):
    person = Persons.query.get(person_id)
    if person:
        db.session.delete(person)
        db.session.commit()
        print('person deleted successfully')
        return redirect(url_for('persons'))
    else:
        print('person not found')
        return 'person not found'


#CRUD for income

@app.route('/income', methods=['GET', 'POST'])
@login_required
def income():
    username = current_user.username
    user_id = current_user.id
    persons = Persons.query.filter_by(username=username).all()
    tags = Tags.query.filter_by(user_id=user_id).all()
    category = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        incoms = Income.query.filter_by(username=username).all()
        expenses = Expense.query.filter_by(username=username).all()
        return render_template('income.html',username=username, persons=persons, incoms=incoms, expenses=expenses, tags=tags, category=category)
    else:
        person = request.form.get('person')
        amount = request.form.get('amount')
        date = request.form.get('date')
        category = request.form.get('category')
        gdate = gdate_str(date)
        text = request.form.get('text')
        tag = request.form.get('tags')
        income = Income(username=username, person=person, amount=amount, date = gdate_str, text = text, tag_id=tag, category=category)
        
        db.session.add(income)
        db.session.commit()
        flash('income successful!', 'success')
        return redirect(url_for('income'))




@app.route('/edit_income/<int:income_id>', methods=['GET', 'POST'])
@login_required
def edit_income(income_id):
    user_id=current_user.id
    income = Income.query.get(income_id)
    tags = Tags.query.filter_by(user_id=user_id)
    category = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        if income:
            return render_template('edit_income.html', income=income, tags=tags, category=category)
        else:
            return "income not found", 404
    elif request.method == 'POST':
        if income:
            income.username = current_user.username
            income.person = request.form['person']
            date = request.form['date']
            gdate = gdate_str(date)
            income.date = gdate
            income.amount = request.form['amount']
            income.text = request.form['text']
            income.tag_id = request.form['tags']
            income.category = request.form['category']
            db.session.commit()
            print('income updated successfully')
            return redirect(url_for('income'))
        else:
            return 'income not found'


@app.route('/delete_income/<int:income_id>', methods=['GET', 'POST'])
@login_required
def delete_income(income_id):
    income = Income.query.get(income_id)
    if income:
        db.session.delete(income)
        db.session.commit()
        print('income deleted successfully')
        return redirect(url_for('income'))
    else:
        print('income not found')
        return 'income not found'



#CRUD for expense

@app.route('/expense', methods=['GET', 'POST'])
@login_required
def expense():
    username = current_user.username
    user_id=current_user.id
    persons = Persons.query.filter_by(username=username).all()
    tags = Tags.query.filter_by(user_id=user_id).all()
    category = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        incoms = Income.query.filter_by(username=username).all()
        expenses = Expense.query.filter_by(username=username).all()
        return render_template('expense.html',username=username, persons=persons, expenses=expenses, tags=tags,  category=category)
    else:
        person = request.form.get('person')
        amount = request.form.get('amount')
        date = request.form.get('date')
        gdate = gdate_str(date)
        category = request.form.get('category')
        text = request.form.get('text')
        tag_id = request.form.get('tags')
        expense = Expense(username=username, person=person, amount=amount, date = gdate, text = text, tag_id=tag_id,  category=category)
        db.session.add(expense)
        db.session.commit()
        flash('expense successful!', 'success')
        return redirect(url_for('expense'))


@app.route('/edit_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def edit_expense(expense_id):
    user_id=current_user.id
    expense = Expense.query.get(expense_id)
    tags = Tags.query.filter_by(user_id=user_id)
    category = Category.query.filter_by(user_id=user_id).all()
    if request.method == 'GET':
        
        if expense:
            return render_template('edit_expense.html', expense=expense, tags=tags, category=category)
        else:
            return "expense not found", 404
    elif request.method == 'POST':
        if expense:
            expense.tag_id = request.form.get('tags')
            expense.username = current_user.username
            expense.person = request.form['person']
            date = request.form['date']
            gdate = gdate_str(date)
            expense.category = request.form.get('category')
            expense.date = gdate
            expense.amount = request.form['amount']
            expense.text = request.form['text']
            db.session.commit()
            print('expense updated successfully')
            return redirect(url_for('expense'))
        else:
            return 'expense not found'

@app.route('/delete_expense/<int:expense_id>', methods=['GET', 'POST'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.get(expense_id)
    if expense:
        db.session.delete(expense)
        db.session.commit()
        print('expense deleted successfully')
        return redirect(url_for('expense'))
    else:
        print('expense not found')
        return 'expense not found'





@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        is_admin = request.form.get('is_admin') == 'on'
        user = User(username=username, password=password, is_admin=is_admin, first_name = first_name, last_name = last_name)
        db.session.add(User(username=username, password=password, is_admin=is_admin, first_name = first_name, last_name = last_name))
        db.session.commit()
        flash('Registration successful!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Login Unsuccessful. Please check personnel number and password', 'danger')
    return render_template('login.html')



@app.route('/')
@login_required
def index():
    today = date.today()
    jtoday = jalali.Gregorian(today).persian_tuple()
    the_day = jtoday[2]
    gfromdate = today - timedelta(days = the_day)
    username = current_user.username
    incoms = Income.query.filter_by(username=username).all()
    expenses = Expense.query.filter_by(username=username).all()




    cats = Category.query.filter_by(user_id=current_user.id).all()
    inc_dict = {}
    exp_dict = {}
    for cat in cats:
        cat_id = cat.id
        incoms_month = Income.query.filter_by(username=username, category=cat_id).filter(Income.date.between(gfromdate, today)).all()
        expense_month = Expense.query.filter_by(username=username, category=cat_id).filter(Expense.date.between(gfromdate, today)).all()
        cat_inc = sumit(incoms_month)
        cat_exp = sumit(expense_month)
        inc_dict[cat_id] = cat_inc
        exp_dict[cat_id] = cat_exp

    montinc = Income.query.filter(Income.date.between(gfromdate, today)).all()
    monthexp = Expense.query.filter(Expense.date.between(gfromdate, today)).all()
    allincs= sumit(montinc)
    allexps = sumit(monthexp)
    return render_template('dashboard.html', incoms=incoms, username=username,
     expenses=expenses, allincs=allincs, allexps=allexps, montinc=montinc, inc_dict=inc_dict, exp_dict = exp_dict,today=today)
    


@app.route('/sooraneh')
@login_required
def sooraneh():
    sumincdamad = 0
    sumincaroos = 0
    suminchd = 0
    username = current_user.username
    cat = Category.query.filter_by(user_id=current_user.id, name="سورانه").first()
    incoms = Income.query.filter_by(username=username, category=cat.id).all()
    expenses = Expense.query.filter_by(username=username).all()
    person_damad = Persons.query.filter_by(username=username, relation="damad").all()
    person_aroos = Persons.query.filter_by(username=username, relation="aroos").all()
    incoms_damad = Income.query.filter_by(username=username, category=cat.id).all()
    incoms_aroos = Income.query.filter_by(username=username, category=cat.id).all()
    for person in person_damad:
        incdamad= Income.query.filter_by(username=username, category=cat.id, person = person.id).first()
        if incdamad:
            sumincdamad += int(incdamad.amount)
    for person in person_aroos:

        inc_aroos= Income.query.filter_by(username=username, category=cat.id, person = person.id).first()
        if inc_aroos:
            sumincaroos += int(inc_aroos.amount)
    sumall = sumincdamad + sumincaroos
    
    return render_template('sooraneh.html', incoms=incoms, username=username, expenses=expenses, sumincdamad=sumincdamad, sumincaroos=sumincaroos, sumall=sumall)


#CRUD for tags

@app.route('/tags', methods=['GET', 'POST'])
@login_required
def tags():
    user_id = current_user.id
    if request.method == 'GET':
        tags = Tags.query.filter_by(user_id=user_id).all()
        return render_template('tags.html',user_id=user_id, tags=tags)
    else:
        name = request.form.get('name')
        description = request.form.get('description')
        tags = Tags(user_id=user_id, name=name, description=description)
        db.session.add(tags)
        db.session.commit()
        flash('tags successful!', 'success')
        return redirect(url_for('tags'))
    
    return render_template('tags.html',tags=tags)


@app.route('/edit_tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def edit_tag(tag_id):
    tag = Tags.query.get(tag_id)
    if request.method == 'GET':
        
        if tag:
            return render_template('edit_tag.html', tag=tag)
        else:
            return "Tag not found", 404
    elif request.method == 'POST':
        if tag:
            tag.name = request.form['name']
            tag.description = request.form['description']
            db.session.commit()
            print('tag updated successfully')
            return redirect(url_for("tags"))
        else:
            return 'tag not found'

@app.route('/delete_tag/<int:tag_id>', methods=['GET', 'POST'])
@login_required
def delete_tag(tag_id):
    tag = Tags.query.get(tag_id)
    if tag:
        db.session.delete(tag)
        db.session.commit()
        print('tag deleted successfully')
        return redirect(url_for('tags'))
    else:
        print('tag not found')
        return 'tag not found'


@app.route('/tag_page/<int:tag_id>')
@login_required
def tag_page(tag_id):
    allex = 0
    tag = Tags.query.filter_by(id =tag_id ).first()
    username = current_user.username
    incoms = Income.query.filter_by(username=username, tag_id=tag_id).all()
    expenses = Expense.query.filter_by(username=username, tag_id=tag_id).all()
    for expense in expenses:
        allex += expense.amount
    return render_template('tag_page.html', incoms=incoms, username=username, expenses=expenses, tag=tag, allex=allex)








#CRUD for budget

@app.route('/budget', methods=['GET', 'POST'])
@login_required
def budget():
    user_id = current_user.id
    category = Category.query.filter_by(user_id=user_id).all()
    username = current_user.username
    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    if request.method == 'GET':
        return render_template('budget.html', budgets=budgets, category=category)
    else:
        category = request.form.get('category')
        monthly_budget = request.form.get('monthly_budget')
        budget = Budget(user_id=current_user.id, monthly_budget=monthly_budget, category=category)   
        db.session.add(budget)
        db.session.commit()
        flash('budget successful!', 'success')
        return redirect(url_for('budget'))


@app.route('/edit_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def edit_budget(budget_id):
    user_id = current_user.id
    category = Category.query.filter_by(user_id = user_id).all()
    budget = Budget.query.get(budget_id)
    if request.method == 'GET':
        
        if budget:
            return render_template('edit_budget.html', budget=budget, category=category)
        else:
            return "budget not found", 404
    elif request.method == 'POST':
        if budget:
            budget.monthly_budget = request.form['monthly_budget']
            db.session.commit()
            print('budget updated successfully')
            return redirect(url_for("budget"))
        else:
            return 'budget not found'

@app.route('/delete_budget/<int:budget_id>', methods=['GET', 'POST'])
@login_required
def delete_budget(budget_id):
    budget = Budget.query.get(budget_id)
    if budget:
        db.session.delete(budget)
        db.session.commit()
        print('budget deleted successfully')
        return redirect(url_for('budget'))
    else:
        print('budget not found')
        return 'budget not found'












def sumit(items):
    sumit = 0
    for item in items:
        sumit += int(item.amount)
    return sumit

def gdate_str(date):
    gdate = jalali.Persian(date).gregorian_tuple()
    if len(str(gdate[1])) < 2:
        gmonth = "0" +  str(gdate[1])

    else:
        gmonth = str(gdate[1])
    if len(str(gdate[2]))<2:
        gday = "0" +  str(gdate[2])
    else:
        gday = str(gdate[2])
    gdate_str = str(gdate[0]) + '-' + gmonth + "-" + gday
    return gdate_str


def gdate_date(date):
    gdate = jalali.Persian(date).gregorian_datetime()
    return gdate


def compare_date_pay(date):
    today = date.today()
    #ate_object = datetime.strptime(date, '%Y-%m-%d')
    if (date <= today):
        return "payed"
    else:
        return "notpayed"

def calculate_inst(amount, rate, inst_num):
    inst = (amount * rate/1200 * (1+rate/1200)**inst_num)/(((1+rate/1200)**inst_num)-1)
    return inst

def gharzhsane_inst(amount, rate, inst_num):
    inst_num = int(inst_num)
    amount = int(amount)
    amount_lst = amount
    rate = int(rate)
    inst = amount/(inst_num - inst_num/12)
    karmozd_list = []
    k = 1
    while k <= int(inst_num/12) :
        if k ==1:
            j = 1
        else:
            j= k*12 - 11
        
        karmozd = round(amount_lst*rate*12/(100*12))
        amount_lst = round(amount - (11*k*inst))
        karmozd_list.append([j, karmozd])
        k+=1
    return karmozd_list

@app.template_filter()
def jalali_date(date):
    #date = dateutil.parser.parse(date)
    jalalidate = jalali.Gregorian(date).persian_string()

    return digits.en_to_fa(jalalidate)


@app.template_filter()
def jalali_date_monthname(date):
    #date = dateutil.parser.parse(date)
    jalalidate = jalali.Gregorian(date).persian_string_monthname()

    return digits.en_to_fa(jalalidate)

@app.template_filter()
def jalali_date_en(date):
    #date = dateutil.parser.parse(date)
    jalalidate = jalali.Gregorian(date).persian_string()

    return jalalidate

@app.template_filter()
def comparison(dateee):
    today = datetime.today()
    date_object = datetime.strptime(dateee, '%Y-%m-%d')
    delta = date_object - today
    if date_object < today:
        return "سررسید گذشته"
    elif date_object == today:
        return "امروز سررسید است"
    else:
        return ("{} روز به سررسید".format(delta.days))


@app.template_filter()
def en2fa(enchar):
    return separator.add(digits.en_to_fa(str(enchar)))

@app.template_filter()
def person_name(person_id):
    person = Persons.query.filter_by(id = person_id).first()
    firstname = person.first_name
    last_name = person.last_name
    return ('{0} {1}'.format(firstname, last_name))


@app.template_filter()
def tag_name(tag_id):
    tag = Tags.query.filter_by(id = tag_id).first()
    return tag.name

@app.template_filter()
def cat_name(cat_id):
    cat = Category.query.filter_by(id = cat_id).first()
    if cat:
        return cat.name
    else:
        return "بدون دسته بندی"



@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def init_db():
    db.create_all()
    username = "admin"
    first_name = "admin"
    last_name = "admin"
    password = "admin"
    is_admin = "1"
    user = User(username=username, password=password, is_admin=is_admin, first_name = first_name, last_name = last_name)
    db.session.add(user)
    db.session.commit()


if __name__ == '__main__':
    db.create_all()
    init_db()
    app.run()

    