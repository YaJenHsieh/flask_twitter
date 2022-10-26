from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,BooleanField,SubmitField,TextAreaField
from wtforms.validators import DataRequired,Email,EqualTo,ValidationError,Length
from twitter.models.user import User

class LoginForm(FlaskForm):
	username=StringField(label='Username:',validators=[DataRequired()])
	password=PasswordField(label='Password:',validators=[DataRequired()])
	remember_me=BooleanField(label='Remember Me')
	submit=SubmitField(label='Login')

class RegisterForm(FlaskForm):
	username=StringField(label='Username:',validators=[DataRequired()])
	email=StringField(label='Email Address:',validators=[DataRequired(),Email()])
	password=PasswordField(label='Password:',validators=[DataRequired()])
	password2=PasswordField(label='Password Repeat:',validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField(label='Register')

	def validate_username(self,username):
		user = User.query.filter_by(username=username.data).first()
		if user is not None: # user不能與資料庫內重複，不是None代表已經有了
			raise ValidationError('Please use different Username')

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if user is not None: # user不能與資料庫內重複，不是None代表已經有了
			raise ValidationError('Please use different Email Address')

class EditProfileForm(FlaskForm): # 編輯個人資訊欄位，可以新增添加文字
	about_me = TextAreaField('About Me',validators=[DataRequired(),Length(min=0,max=120)]) # TextAreaField 是 wtforms方法中，可以添加文字的方法。 Length 是 validators中的一種方法，validators(min=,max=)添加兩個參數
	submit = SubmitField('Save')

class TweetForm(FlaskForm):
	tweet = TextAreaField('Tweet',validators=[DataRequired(),Length(min=1,max=140)])
	submit = SubmitField('Tweet')

class PasswordResetRequestForm(FlaskForm):
	email=StringField(label='Email Address:',validators=[DataRequired(),Email()])
	submit = SubmitField('Reset Password')

	def validate_email(self,email):
		user = User.query.filter_by(email=email.data).first()
		if not user: # 如果沒有 代表還沒註冊過
			raise ValidationError

class PasswordResetForm(FlaskForm):
	password=PasswordField(label='Password:',validators=[DataRequired()])
	password2=PasswordField(label='Password Repeat:',validators=[DataRequired(),EqualTo('password')])
	submit=SubmitField(label='Submit')

class EditTweetForm(FlaskForm):
	edit_tweet = TextAreaField(validators=[DataRequired(),Length(min=0,max=120)]) 
	submit = SubmitField('Save')

class SearchForm(FlaskForm):
	searched = StringField('Search',validators=[DataRequired()])
	submit = SubmitField('Submit')

class UserInfoForm(FlaskForm):
	request_btn = StringField('Request Btn',validators=[DataRequired()])
	submit = SubmitField('Submit')
