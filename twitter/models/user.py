from datetime import datetime
from hashlib import md5
import time

from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from flask import current_app
import jwt

from twitter import db,login_manager
from twitter.models.tweet import Tweet

#用來描述關係，都是外件的資料庫
followers = db.Table('followers',
	db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
	db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
)

class User(db.Model,UserMixin):
	id = db.Column(db.Integer(),primary_key=True)
	username = db.Column(db.String(64),unique=True,index=True)
	email = db.Column(db.String(64),unique=True,index=True)
	password_hash = db.Column(db.String(128),unique=True)
	about_me = db.Column(db.String(128))
	create_time = db.Column(db.DateTime,default=datetime.now().replace(microsecond=0))
	tweets = db.relationship('Tweet',backref='author',lazy='dynamic') # 設置關聯，relationship設置於一對多的『一』

	followed = db.relationship( # 多對多，一個user可以有多少人關注
		'User',secondary=followers,
		primaryjoin=(followers.c.follower_id == id),
		secondaryjoin=(followers.c.followed_id == id),
		backref=db.backref('followers',lazy='dynamic'),lazy='dynamic'
	)

	def __repr__(self):
		return f'id={self.id},username={self.username},email={self.email},password_hash={self.password_hash}'

	def set_password(self,password):
		self.password_hash = generate_password_hash(password)

	def check_password(self,password):
		return check_password_hash(self.password_hash,password)

	def avatar(self,size=80):  # 使用user email 經由md5 產生隨機大頭照
		md5_photo = md5(self.email.lower().encode('utf-8')).hexdigest()
		return f'https://www.gravatar.com/avatar/{md5_photo}?d=identicon&s={size}'

	def is_following(self,user): # 檢查用戶使否已經follow
		return self.followed.filter(
			followers.c.followed_id == user.id).count() > 0

	def follow(self,user):
		if not self.is_following(user):
			self.followed.append(user)

	def unfollow(self,user):
		if self.is_following(user):
			self.followed.remove(user)
	
	def own_and_followed_tweets(self):  # 自己與被follow的推文
		followed = Tweet.query.join(followers,(followers.c.followed_id == Tweet.user_id)).filter(followers.c.follower_id == self.id)
		own = Tweet.query.filter_by(user_id=self.id)
		return followed.union(own).order_by(Tweet.create_time.desc())

	def get_jwt(self,expire=7200):
		return jwt.encode(
			{
				'email' : self.email,
				'exp' : time.time() + expire
			},
			current_app.config['SECRET_KEY'],
			algorithm='HS256'
		)
	
	@staticmethod # 靜態方法
	def verify_jwt(token):
		try:
			email = jwt.decode(
				token,
				current_app.config['SECRET_KEY'],
				algorithms='HS256'
			)
			email =email['email']
		except:
			return
		return User.query.filter_by(email=email).first()

@login_manager.user_loader # 使login 根據資料庫存取的id找到用戶
def load_user(id): #出來為字串，故要轉int
    return User.query.get(int(id))