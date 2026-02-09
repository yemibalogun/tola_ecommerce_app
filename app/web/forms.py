from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, FileField
from wtforms.validators import DataRequired, NumberRange, Length
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