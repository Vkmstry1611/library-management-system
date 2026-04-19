from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Length


class book_form(FlaskForm):
    title = StringField(label='Title', validators=[DataRequired()])
    isbn = StringField(label='ISBN', validators=[DataRequired()])
    author = StringField(label='Author', validators=[DataRequired()])
    stock = IntegerField(label='Stock', validators=[DataRequired()])
    submit = SubmitField(label='Submit')


class member_form(FlaskForm):
    name = StringField(label='Name', validators=[DataRequired()])
    member_name = StringField(label='Member Name', validators=[DataRequired()])
    phone_number = StringField(label='Phone Number', validators=[DataRequired(), Length(min=7, max=15)])
    submit = SubmitField(label='Submit')
