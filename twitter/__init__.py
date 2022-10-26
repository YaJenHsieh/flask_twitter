from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from twitter.config import Config
from flask_login import LoginManager
from flask_mail import Mail

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
Migrate(app,db)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page' # 未登入者若要造訪home會導向login頁面
mail = Mail(app)

from twitter import route