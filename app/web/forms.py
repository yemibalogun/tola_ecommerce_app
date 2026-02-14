from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, FileField, SelectField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Optional
from flask_wtf.file import FileAllowed

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