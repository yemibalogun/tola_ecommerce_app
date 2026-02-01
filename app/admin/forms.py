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


class ProductForm(FlaskForm):
    name = StringField("Product Name", validators=[DataRequired(), Length(min=1, max=255),])
    description = TextAreaField("Description")
    price = DecimalField(
        "Price",
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
    )
    category_id = SelectField("Category", coerce=int, choices=[])
    is_active = BooleanField("Active", default=True)
    image = FileField(
        "Product Image",
        validators=[FileAllowed(["jpg", "jpeg", "png"])],
    )

class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Login")