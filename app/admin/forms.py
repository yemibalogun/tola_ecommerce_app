from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    PasswordField,
    SubmitField,
    BooleanField,
)
from wtforms.validators import DataRequired, NumberRange, Length, Email
from flask_wtf.file import FileField, FileAllowed


class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")


class ProductForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    price = DecimalField(
        "Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
    )
    slug = StringField("Slug", validators=[DataRequired()])
    description = TextAreaField("Description")
    category_id = SelectField("Category", coerce=int)
    is_active = BooleanField("Active", default=True)
    image = FileField(
        "Product Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ]
    )