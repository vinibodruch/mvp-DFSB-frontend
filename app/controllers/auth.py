"""Authentication blueprint — register, login, logout."""

import logging

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf import FlaskForm
from wtforms import EmailField, PasswordField, StringField
from wtforms.validators import DataRequired, Email, EqualTo, Length

from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    UsernameAlreadyTakenError,
)

logger = logging.getLogger(__name__)

auth_bp = Blueprint("auth", __name__)

_user_repo = UserRepository()
_auth_service = AuthService(_user_repo)


# ---------------------------------------------------------------------------
# Forms
# ---------------------------------------------------------------------------


class RegistrationForm(FlaskForm):
    """WTForms form for user registration."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = EmailField(
        "Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8)]
    )
    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )


class LoginForm(FlaskForm):
    """WTForms form for user login."""

    email = EmailField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = _auth_service.register(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
            )
            login_user(user)
            flash("Registration successful! Welcome.", "success")
            return redirect(url_for("main.dashboard"))
        except EmailAlreadyRegisteredError:
            flash("That email is already registered.", "danger")
        except UsernameAlreadyTakenError:
            flash("That username is already taken.", "danger")

    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))

    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = _auth_service.authenticate(
                email=form.email.data,
                password=form.password.data,
            )
            login_user(user)
            next_page = request.args.get("next")
            flash("Logged in successfully.", "success")
            return redirect(next_page or url_for("main.dashboard"))
        except InvalidCredentialsError:
            flash("Invalid email or password.", "danger")
            logger.warning(
                "Failed login attempt for email: %s", form.email.data
            )

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log the current user out."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))
