import requests

from flask import render_template,redirect,url_for,request,abort,current_app,flash
from flask_login import login_user,current_user,logout_user,login_required

from twitter import app,db
from twitter.forms import LoginForm,RegisterForm,EditProfileForm,TweetForm,PasswordResetRequestForm,PasswordResetForm,EditTweetForm,SearchForm,UserInfoForm
from twitter.email import send_email

from twitter.models.tweet import Tweet
from twitter.models.user import User

@app.route('/home',methods=['GET','POST'])
@app.route('/',methods=['GET','POST'])
@login_required
def home_page():
	form_search = SearchForm()
	searched = ""
	if form_search.validate_on_submit():
		searched = form_search.searched.data.strip()

	form=TweetForm()
	if form.validate_on_submit():
		t = Tweet(body=form.tweet.data,author=current_user)
		db.session.add(t)
		db.session.commit()
		return redirect(url_for('home_page'))
	
	current_user_user_id = current_user.id

	page_num = request.args.get('page',1,type=int) # 找出網址上 ?page=
	tweets = current_user.own_and_followed_tweets().filter(Tweet.body.like('%'+ searched  + '%'),(Tweet.status == 1)).paginate(page=page_num,per_page=current_app.config['TWEET_PER_PAGE'],error_out=False)# 顯示自己及關注用戶的推文,並限制推文一頁顯示5篇
	next_url = url_for('home_page',page=tweets.next_num) if tweets.has_next else None
	prev_url = url_for('home_page',page=tweets.prev_num) if tweets.has_prev else None

	# news API
	url = 'https://newsapi.org/v2/top-headlines?country=tw&apiKey=f2c3bfcff9534b6a9765a67c27e187ee'
	news_req_data = requests.get(url)
	news_data = news_req_data.json()
	return render_template('home.html',tweets=tweets.items,form=form,next_url=next_url,prev_url=prev_url,current_user_user_id=current_user_user_id,searched=searched,news_data=news_data)

@app.route('/login',methods=['GET','POST'])
def login_page():
	if current_user.is_authenticated: # 當前用戶驗證後已登入 直接進home_page
		return redirect(url_for('home_page'))
	form=LoginForm()
	if form.validate_on_submit():
		u = User.query.filter_by(username=form.username.data).first()
		if u is None or not u.check_password(form.password.data):
			flash('Invalid username or password',category='success')
			return redirect(url_for('login_page'))
		login_user(u,remember=form.remember_me.data) # 在session記住用戶

		next_page = request.args.get('next')
		if next_page: # 確認跳轉畫面正確 網址:...％2Fhome = .../home
			return redirect(next_page) # 登入後直接跳轉至點擊的那頁
		return redirect(url_for('home_page'))
	return render_template('login.html',title='Login',form=form)

@app.route('/logout')
def logout_page():
	logout_user()
	return redirect(url_for('login_page')) 

@app.route('/register',methods=['GET','POST'])
def register_page():
	if current_user.is_authenticated:
		return redirect(url_for('home_page'))
	form=RegisterForm()
	if form.validate_on_submit(): #若註冊與資料庫沒有相同的，就會存入資料庫中
		user = User(username = form.username.data,email=form.email.data)
		user.set_password(form.password.data) #存入資料庫中
		db.session.add(user)
		db.session.commit()
		return redirect(url_for('login_page'))
	return render_template('register.html',title='Register',form=form)

@app.route('/<username>',methods=['GET','POST'])
@login_required
def user_page(username):
	user_info_form = UserInfoForm()
	form_search = SearchForm()
	searched = ""
	if form_search.validate_on_submit():
		searched = form_search.searched.data.strip()
	
	u = User.query.filter_by(username=username).first()
	if u is None: # 如果沒有此用戶 顯示404頁面
		abort(404)

	current_user_user_id = current_user.id
	page_num = request.args.get('page',1,type=int)
	tweets = Tweet.query.filter_by(author=u).filter(Tweet.body.like('%'+ searched  + '%'),(Tweet.status == 1)).order_by(Tweet.create_time.desc()).paginate(
		page=page_num,
		per_page=current_app.config['TWEET_PER_PAGE'],
		error_out=False)
	next_url = url_for('user_page',username=username,page=tweets.next_num) if tweets.has_next else None
	prev_url = url_for('user_page',username=username,page=tweets.prev_num) if tweets.has_prev else None
	
	if user_info_form.validate_on_submit():
		request_btn = user_info_form.request_btn.data
		if request_btn == 'Follow':
			current_user.follow(u)
			db.session.commit()
		else:
			current_user.unfollow(u)
			db.session.commit()
	return render_template('user.html',title='Profile',tweets=tweets.items,user=u,next_url=next_url,prev_url=prev_url,current_user_user_id=current_user_user_id,username=username,searched=searched,form_search=form_search)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'),404

@app.route('/edit_profile',methods=['GET','POST'])
@login_required
def editProfile_page():
	form_search = SearchForm()
	searched = ""
	if form_search.validate_on_submit():
		searched = form_search.searched.data.strip()

	form=EditProfileForm()
	if request.method == 'GET': # 顯示當前用戶的about_me內容
		form.about_me.data = current_user.about_me
	if form.validate_on_submit():
		current_user.about_me = form.about_me.data
		db.session.commit()
		return redirect(url_for('user_page',username=current_user.username))

	current_user_user_id = current_user.id
	page_num = request.args.get('page',1,type=int)
	tweets = Tweet.query.order_by(Tweet.create_time.desc()).filter(Tweet.body.like('%'+ searched  + '%'),(Tweet.status == 1)).paginate(
		page=page_num,
		per_page=current_app.config['TWEET_PER_PAGE'],
		error_out=False) 
	next_url = url_for('editProfile_page',page=tweets.next_num) if tweets.has_next else None
	prev_url = url_for('editProfile_page',page=tweets.prev_num) if tweets.has_prev else None
	return render_template('edit_profile.html',form=form,form_search=form_search,searched=searched,current_user_user_id=current_user_user_id,tweets=tweets.items,next_url=next_url,prev_url=prev_url)

@app.route('/password_reset_request',methods=['GET','POST'])
def password_reset_request():
	if current_user.is_authenticated: # 如果當前用戶已經登入，不用再重置密碼
		return redirect(url_for('home_page'))
	form=PasswordResetRequestForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			flash("You should soon receive an email allowing you to reset your password.Please make sure to check your spam and trash if you can't find the email.",category='success')
			token = user.get_jwt()
			url_password_reset = url_for('password_reset',token=token,_external=True)
			url_password_reset_request = url_for('password_reset_request',_external=True)
			send_email(subject='[Twitter] Please Reset Your Password',
			recipients=[user.email],
			text_body=render_template(
				'email/password_reset.txt',
				url_password_reset=url_password_reset,
				url_password_reset_request=url_password_reset_request
			))
		else:
			raise
		return redirect(url_for('login_page'))
	return render_template('password_reset_request.html',form=form)

@app.route('/password_reset/<token>',methods=['GET','POST'])
def password_reset(token):
	if current_user.is_authenticated: 
		return redirect(url_for('home_page'))
	user = User.verify_jwt(token)
	if not user:
		return redirect(url_for('login_page'))
	form=PasswordResetForm()
	if form.validate_on_submit():
		user.set_password(form.password.data) 
		db.session.commit()
		return redirect(url_for('login_page'))
	return render_template('password_reset.html',title='Password Reset',form=form)

@app.route('/explore',methods=['GET','POST'])
@login_required
def explore_page(): # 找到網站上所有推文的人
	form_search = SearchForm()
	searched = ""
	if form_search.validate_on_submit():
		searched = form_search.searched.data.strip()

	current_user_user_id = current_user.id
	page_num = request.args.get('page',1,type=int)
	tweets = Tweet.query.order_by(Tweet.create_time.desc()).filter(Tweet.body.like('%'+ searched  + '%'),(Tweet.status == 1)).paginate(
		page=page_num,
		per_page=current_app.config['TWEET_PER_PAGE'],
		error_out=False) 
	next_url = url_for('explore_page',page=tweets.next_num) if tweets.has_next else None
	prev_url = url_for('explore_page',page=tweets.prev_num) if tweets.has_prev else None
	return render_template('explore.html',tweets=tweets.items,next_url=next_url,prev_url=prev_url,current_user_user_id=current_user_user_id,form_search=form_search,searched=searched)

@app.route('/edit_tweet/<tweet_id>',methods=['GET','POST'])
@login_required
def edit_tweet_page(tweet_id):
	form_search = SearchForm()
	searched = ""
	if form_search.validate_on_submit():
		searched = form_search.searched.data.strip()

	form=EditTweetForm()
	tweet_data = Tweet.query.filter_by(id=tweet_id).first()
	if request.method == 'GET': # 顯示當前用戶的about_me內容
		form.edit_tweet.data = tweet_data.body
	if form.validate_on_submit():
		tweet_data.body = form.edit_tweet.data
		db.session.commit()
		return redirect(url_for('home_page'))

	current_user_user_id = current_user.id
	page_num = request.args.get('page',1,type=int)
	tweets = Tweet.query.order_by(Tweet.create_time.desc()).filter(Tweet.body.like('%'+ searched  + '%'),(Tweet.status == 1)).paginate(
		page=page_num,
		per_page=current_app.config['TWEET_PER_PAGE'],
		error_out=False)
	next_url = url_for('home_page',page=tweets.next_num) if tweets.has_next else None
	prev_url = url_for('home_page',page=tweets.prev_num) if tweets.has_prev else None
	return render_template('edit_tweet.html',form=form,form_search=form_search,searched=searched,current_user_user_id=current_user_user_id,tweets=tweets.items,next_url=next_url,prev_url=prev_url)

@app.route('/delete_tweet/<tweet_id>',methods=['GET','POST'])
@login_required
def delete_tweet_page(tweet_id):
	tweet_data = Tweet.query.filter_by(id=tweet_id).first()
	tweet_data.status = 0
	db.session.commit()
	return redirect(url_for('home_page'))

# 將內容傳遞到 navbar
@app.context_processor
def base():
	form=SearchForm()
	return dict(form=form)

