from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    DecimalField,
    SelectField,
    PasswordField,
    SubmitField,
    IntegerField,
    BooleanField,
)
from wtforms.validators import DataRequired, Optional, NumberRange, Email
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
        validators=[DataRequired(), NumberRange(min=0.01)],
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

class ProductVariantForm(FlaskForm):
    name = StringField(
        "Variant Name (e.g. Black / 128GB)",
        validators=[DataRequired()],
    )

    sku = StringField(
        "SKU",
        validators=[DataRequired()],
    )

    price_override = DecimalField(
        "Price Override",
        places=2,
        rounding=None,
        validators=[Optional()],
    )

    stock_quantity = IntegerField(
        "Stock Quantity",
        validators=[DataRequired(), NumberRange(min=0)],
        default=0,
    )

    # File upload for image
    image = FileField(
        "Variant Image",
        validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')]
    )

    submit = SubmitField("Save Variant")

class InventoryAdjustForm(FlaskForm):
    # Used for one-click inventory adjustments (+1,-1, +10).

    delta = IntegerField(validators=[DataRequired()])
    submit = SubmitField()