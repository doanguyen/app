from flask import request, flash, render_template, redirect, url_for, session
from flask_login import login_user
from flask_wtf import FlaskForm
from wtforms import StringField, validators

from app.auth.base import auth_bp
from app.log import LOG
from app.models import User


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[validators.DataRequired()])
    password = StringField("Password", validators=[validators.DataRequired()])


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == "POST":
        if form.validate():
            user = User.filter_by(email=form.email.data).first()

            if not user:
                flash("No such email", "warning")
                return render_template("auth/login.html", form=form)

            if not user.activated:
                flash(
                    "You would need to validate your account, please check your inbox",
                    "warning",
                )
                return render_template("auth/login.html", form=form)

            if not user.check_password(form.password.data):
                flash("Wrong password", "warning")
                return render_template("auth/login.html", form=form)

            LOG.debug("log user %s in", user)
            login_user(user)

            # User comes to login page from another page
            if "next" in request.args:
                next_url = request.args.get("next")
                LOG.debug("redirect user to %s", next_url)
                return redirect(next_url)
            else:
                LOG.debug("redirect user to dashboard")
                return redirect(url_for("dashboard.index"))

    return render_template("auth/login.html", form=form)
