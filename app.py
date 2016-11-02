import flask
from flask import Flask, Response, request, render_template, redirect, url_for, send_from_directory, session
from flaskext.mysql import MySQL
import flask.ext.login as flask_login
from flask_oauth import OAuth
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
import json
import os


#database setup
'''
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your database password'
app.config['MYSQL_DATABASE_DB'] = 'roundtable'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)
'''
from flask import Flask
app = Flask(__name__)

app.config.update(
    DEBUG = True,
)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'ico/favicon.ico')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

app.secret_key = 'super secret string'  # Change this!
app.config['GOOGLEMAPS_KEY'] = 'AIzaSyDPIxQ95g3W-PAd0WPy_PjM84-HtAKQp1U'
FACEBOOK_APP_ID = '1672494819728765'
FACEBOOK_APP_SECRET = 'f7e34d53d0c62215f2b8a92f59941a89'


oauth = OAuth()
facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=FACEBOOK_APP_ID,
    consumer_secret= FACEBOOK_APP_SECRET,
    request_token_params={'scope': 'email' 'picture'}
)

@facebook.tokengetter
def get_facebook_token():
    return session.get('facebook_token')

def pop_login_session():
    session.pop('logged_in', None)
    session.pop('facebook_token', None)

@app.route("/facebook_login")
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',next=request.args.get('next'), _external=True))

@app.route("/facebook_authorized")
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None or 'access_token' not in resp:
        return redirect(next_url)
    session['logged_in'] = True
    session['facebook_token'] = (resp['access_token'], '')
    return redirect(next_url)

@app.route("/logout")
def logout():
    pop_login_session()
    return redirect(url_for('index'))

#get information from facebook
def get_facebook_name():
	data = facebook.get('/me').data
	print data
	if 'id' in data and 'name' in data:
		user_id = data['id']
		user_name = data['name']
		return user_name


def get_facebook_friend_appuser():
	data = facebook.get('/me?fields=friends{first_name,last_name}').data
	print data
	return data


def get_all_facebook_friends():
	data = facebook.get('/me/taggable_friends?fields=first_name,last_name').data
	print data
	return data

def get_facebook_profile_url():
    data = facebook.get('/me?fields=picture{url}').data
    print data['picture']
    json_str = json.dumps(data['picture'])
    resp = json.loads(json_str)
    print "json object"
    user_picture_url = data['picture']
    return data['picture']['data']['url']






#This is for profile editing
@app.route("/Profile/<user_id>/edit", methods = ['GET','POST'])
def edit_profile(user_id):
	if request.method == 'POST':
		return render_template('profile_edit.html')
	else:
		return render_template('profile_edit.html')





GoogleMaps(app)
#google map testing
@app.route("/mapview")
def mapview():
    # creating a map in the view
    mymap = Map(
        identifier="view-side",
        lat=37.4419,
        lng=-122.1419,
        markers=[(37.4419, -122.1419)]
    )
    sndmap = Map(
        identifier="sndmap",
        lat=37.4419,
        lng=-122.1419,
        markers=[
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/green-dot.png',
             'lat': 37.4419,
             'lng': -122.1419,
             'infobox': "<b>Hello World</b>"
          },
          {
             'icon': 'http://maps.google.com/mapfiles/ms/icons/blue-dot.png',
             'lat': 37.4300,
             'lng': -122.1400,
             'infobox': "<b>Hello World from other place</b>"
          }
        ]
    )
    return render_template('map_test.html', mymap=mymap, sndmap=sndmap)

@app.route("/")
def index():
	name = get_facebook_name()
	#friends = get_facebook_friend_appuser()
	#all_friends = get_all_facebook_friends()
	return render_template('home_page_template.html', message = 'Welcome to RoundTable', user_name = get_facebook_name(), user_picture_url = get_facebook_profile_url())


if __name__ == "__main__":
	#this is invoked when in the shell  you run
	#$ python app.py
	app.run(port=5000, debug=True)
