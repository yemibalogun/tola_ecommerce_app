from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, FileField, SelectField, BooleanField, PasswordField
from wtforms.validators import DataRequired, NumberRange, Length, Optional, Email, EqualTo, Regexp, ValidationError, URL
from flask_wtf.file import FileAllowed

IMAGE_TYPES = ["jpg", "jpeg", "png", "webp"]

# Slugs that would collide with platform routes or read as official
RESERVED_SLUGS = {
    "admin", "api", "static", "store", "stores", "signup", "login", "logout",
    "www", "app", "dashboard", "tola", "help", "support",
}

slug_validators = [
    DataRequired(),
    Length(min=3, max=40),
    Regexp(
        r"^[a-z0-9]+(?:-[a-z0-9]+)*$",
        message="Use lowercase letters, numbers and single dashes only.",
    ),
]


def not_reserved(form, field) -> None:
    if (field.data or "").lower() in RESERVED_SLUGS:
        raise ValidationError("That link is reserved. Please pick another.")


class SignupForm(FlaskForm):
    """
    Creates a new store (tenant) and its owner account in one step.
    """
    store_name = StringField("Store name", validators=[DataRequired(), Length(min=2, max=80)])
    slug = StringField("Store link", validators=slug_validators + [not_reserved])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8, max=128)])
    confirm = PasswordField(
        "Confirm password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match.")],
    )
    submit = SubmitField("Create my store")


class StoreSettingsForm(FlaskForm):
    """
    Everything a store owner can customise about their public storefront.
    """
    # Identity
    name = StringField("Store name", validators=[DataRequired(), Length(min=2, max=80)])
    slug = StringField("Store link", validators=slug_validators + [not_reserved])
    tagline = StringField("Tagline", validators=[Optional(), Length(max=255)])
    about = TextAreaField("About your store", validators=[Optional(), Length(max=4000)])
    logo = FileField("Logo", validators=[FileAllowed(IMAGE_TYPES + ["svg"], "Images only!")])
    remove_logo = BooleanField("Remove current logo")

    # Look & feel
    accent_color = StringField(
        "Accent colour",
        validators=[DataRequired(), Regexp(r"^#[0-9a-fA-F]{6}$", message="Use a hex colour like #6d5dfc.")],
    )
    hero_theme = SelectField(
        "Homepage theme",
        choices=[("dark", "Midnight (dark)"), ("light", "Daylight (light)")],
        validators=[DataRequired()],
    )
    currency_symbol = SelectField(
        "Currency",
        choices=[
            ("₦", "₦ Naira"),
            ("$", "$ Dollar"),
            ("£", "£ Pound"),
            ("€", "€ Euro"),
            ("GH₵", "GH₵ Cedi"),
            ("KSh", "KSh Shilling"),
            ("R", "R Rand"),
        ],
        validators=[DataRequired()],
    )

    # Homepage hero
    hero_title = StringField("Headline", validators=[Optional(), Length(max=255)])
    hero_subtitle = StringField("Sub-headline", validators=[Optional(), Length(max=255)])
    hero_image = FileField("Hero image", validators=[FileAllowed(IMAGE_TYPES, "Images only!")])
    remove_hero_image = BooleanField("Remove current hero image")

    # Contact
    contact_email = StringField("Contact email", validators=[Optional(), Email(), Length(max=255)])
    contact_phone = StringField("Phone / WhatsApp", validators=[Optional(), Length(max=50)])
    instagram_url = StringField("Instagram URL", validators=[Optional(), URL(), Length(max=255)])

    submit = SubmitField("Save changes")

class TestimonialForm(FlaskForm):
    author_name = StringField("Your Name", validators=[DataRequired()])
    content = TextAreaField("Testimonial", validators=[DataRequired()])
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField("Submit")


class BlogForm(FlaskForm):
    title = StringField(
        "Title",
        validators=[DataRequired(), Length(max=200)]
    )

    content = TextAreaField(
        "Content",
        validators=[DataRequired()]
    )

    image = FileField(
        "Featured Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ]
    )

    submit = SubmitField("Publish Blog")



class BillboardForm(FlaskForm):
    """
    Edits billboard settings stored directly on Tenant model.
    """

    hero_theme = SelectField(
        "Theme",
        choices=[("light", "Light"), ("dark", "Dark")],
        validators=[DataRequired()],
    )

    submit = SubmitField("Save Billboard Settings")


class TenantBannerForm(FlaskForm):

    title = StringField(
        "Title",
        validators=[DataRequired(), Length(max=255)],
    )

    subtitle = StringField(
        "Subtitle",
        validators=[Optional(), Length(max=255)],
    )

    # ✅ File uploads instead of text input
    image_file = FileField(
        "Banner Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ],
    )

    background_file = FileField(
        "Background Image",
        validators=[
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!")
        ],
    )

    hover_effect = SelectField(
        "Hover Effect",
        choices=[
            ("zoom", "Zoom"),
            ("lift", "Lift"),
            ("rotate", "Rotate"),
            ("fade", "Fade"),
        ],
    )

    cta_text = StringField("CTA Text", validators=[Optional(), Length(max=50)])
    cta_url = StringField("CTA URL", validators=[Optional(), Length(max=255)])

    bg_color = StringField("Background Color", validators=[Optional()])
    text_color = StringField("Text Color", validators=[Optional()])

    order = IntegerField("Display Order", default=0)
    is_active = BooleanField("Active")

    submit = SubmitField("Save Banner")