from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from .models import User, Account, Notification, Transaction
from . import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from schwifty import IBAN
import json

views = Blueprint("views", __name__)


@views.route("/")
@login_required
def home():
    return render_template("home.html", user=current_user)


@views.route("/my_accounts", methods=["GET", "POST"])
@login_required
def my_accounts():
    if request.method == "POST":
        iban_form = request.form.get("iban")
        notification = Notification(
            data="You just added a new Account with the iban -->>"+iban_form, user_id=current_user.id)
        try:
            iban = IBAN(iban_form)
            new_account = Account(
                iban=iban_form, user_id=current_user.id, cash=1000)
            db.session.add(new_account)
            db.session.add(notification)
            db.session.commit()
            flash("Account added correctly", category="succes")
        except:
            flash("Your IBAN is invalid", category="error")
            

    return render_template("my_accounts.html", user=current_user)


@views.route("/delete-account", methods=["POST"])
def delete_account():
    account = json.loads(request.data)
    accountId = account["accountId"]
    account = Account.query.get(accountId)
    if account:
        if account.user_id == current_user.id:
            db.session.delete(account)
            db.session.commit()
    return jsonify({})


@views.route("/transfers", methods=["GET", "POST"])
@login_required
def transfers():
    if request.method == "POST":
        your_iban_form = request.form.get("your_iban")
        destinatary_iban_form = request.form.get("destinatary_iban")
        transaction_cash = request.form.get("cash")
        your_account = Account.query.filter_by(
            iban=your_iban_form).first()
        destinatary_account = Account.query.filter_by(
            iban=destinatary_iban_form).first()
        notification = "You have a new Transfer,go check history for more details"

        if destinatary_account == None:
            flash("Destinatary account doesnt exists", category="error")
        elif your_account == None:
            flash("The iban you introduced is wrong", category="error")

        elif transaction_cash.isdigit():
            your_cash = your_account.cash
            your_account.cash = your_cash-int(transaction_cash)
            destinatary_cash = destinatary_account.cash
            destinatary_account.cash = destinatary_cash+int(transaction_cash)
            notifications = Notification(
                data=notification, user_id=current_user.id)
            data = transaction_cash+"$ got transfered from " + \
                your_iban_form + " to "+destinatary_iban_form
            transaction = Transaction(data=data, user_id=current_user.id)
            db.session.add(transaction)
            db.session.add(notifications)
            db.session.commit()
            flash("Transaction has been made succesfully", category="succes")
        else:
            flash("Cash amount must be a number", category="error")

    return render_template("transfers.html", user=current_user)


@views.route("/my_profile", methods=["GET", "POST"])
@login_required
def my_profile():

    id_surcolega = current_user.get_id()
    id = int(id_surcolega)
    info = User.query.filter_by(id=id).first()
    first_name = info.first_name
    email = info.email
    password = info.password

    return render_template("my_profile.html", user=current_user, info=info, first_name=first_name, email=email, password=password)


@views.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    id_surcolega = current_user.get_id()
    id = int(id_surcolega)
    info = User.query.filter_by(id=id).first()
    if request.method == "POST":
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if password == confirm_password:
            info.password = generate_password_hash(
                password, method="sha256")
            db.session.commit()
            flash("Password changed correctly!", category="succes")
            return redirect("/")
        else:
            flash("Both passwords must match", category="error")

    return render_template("change_password.html", user=current_user)


@views.route("/notifications")
@login_required
def notifications():

    return render_template("notifications.html", user=current_user)


@views.route("/transaction_history")
@login_required
def transaction_history():
    return render_template("transaction_history.html", user=current_user)


@views.route("/deposit_cash/<id>", methods=["GET", "POST"])
@login_required
def deposit_cash(id):
    account = Account.query.get(id)

    if request.method == "POST":
        deposit_amount = request.form["deposit"]
        account.cash = account.cash + int(deposit_amount)
        notification = Notification(
            data="You have a new deposit of " + deposit_amount + " $", user_id=current_user.id)
        db.session.add(notification)
        db.session.commit()
        flash("You have successfully made a deposit!", category="succes")
        return redirect("/my_accounts")
    return render_template("deposit_cash.html", user=current_user)


@views.route("/withdraw_cash/<id>", methods=["GET", "POST"])
@login_required
def withdraw_cash(id):
    account = Account.query.get(id)

    if request.method == "POST":
        withdraw_amount = request.form["withdraw"]
        account.cash = account.cash - int(withdraw_amount)
        notification = Notification(
            data="You have a new withdrawal of " + withdraw_amount + " $", user_id=current_user.id)
        db.session.add(notification)
        db.session.commit()
        flash("You have successfully made a withdrawal!", category="succes")
        return redirect("/my_accounts")
    return render_template("withdraw_cash.html", user=current_user)
