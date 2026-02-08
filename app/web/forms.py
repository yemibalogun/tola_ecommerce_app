from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class TestimonialForm(FlaskForm):
    author_name = StringField("Your Name", validators=[DataRequired()])
    content = TextAreaField("Testimonial", validators=[DataRequired()])
    rating = IntegerField("Rating (1-5)", validators=[DataRequired(), NumberRange(min=1, max=5)])
    submit = SubmitField("Submit")
