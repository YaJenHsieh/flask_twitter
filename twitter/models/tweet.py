from twitter import db
from datetime import datetime

class Tweet(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	body = db.Column(db.String(140))
	create_time = db.Column(db.DateTime,default=datetime.now().replace(microsecond=0))
	status = db.Column(db.Integer,default=1)
	user_id = db.Column(db.Integer,db.ForeignKey('user.id')) # 設置外來鍵，ForeignKey設置於一對多的『多』

	def __repr__(self):
		return f'id={self.id}, body={self.body}, create_time={self.create_time}, user_id={self.user_id},status={self.status}'