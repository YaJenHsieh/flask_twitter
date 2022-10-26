import os

class Config:
	WTF_CSRF_ENABLED = False
	# SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host:port/database'
	SQLALCHEMY_DATABASE_URI = "postgresql://User:Password@Host:Port/Database"


	SQLALCHEMY_TRACK_MODIFICATIONS = False
	SECRET_KEY = 'xxx123456xxx'
	TWEET_PER_PAGE = 10

	MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER','noreply@twitter.com')
	MAIL_SERVER = os.environ.get('MAIL_SERVER','smtp.gmail.com')
	MAIL_PORT =os.environ.get('MAIL_PORT',465)
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS',False)
	MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL',True)
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME','twittor.jenny@gmail.com')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD','password')