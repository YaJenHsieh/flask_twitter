from threading import Thread
from flask import current_app
from flask_mail import Message
from twitter import mail

def send_async_email(app,msg):
	with app.app_context():
		mail.send(msg)

def send_email(subject,recipients,text_body):
	msg = Message(
		subject=subject,
		recipients=recipients
	)
	msg.body = text_body

	#如果使用 mail.send(msg)會卡3-5秒左右，所以使用Thread
	Thread(   # 使用多線程
		target=send_async_email,
		args=(current_app._get_current_object(),msg)).start()
		
