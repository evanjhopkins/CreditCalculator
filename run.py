from flask import Flask, render_template, request, session
import logging
from logging.handlers import RotatingFileHandler
import hashlib
import MySQLdb
import pygal
import json
import urllib2
import re
from random import randint


#boolean for logging level
#  true = debug
#  false = info
debug= False
app = Flask(__name__)
app.secret_key = "sfsKG7*(*&)*LIJHGljhlkjhdk903"
#############
#  Web App  #
#############
@app.route('/')
@app.route('/index')
def index():
	app.logger.info('/index')
	response = api_college()
	response_obj = json.loads(response)
	#response_obj = {}
	return render_template('index.html', data = response_obj)

@app.route('/api/college')
def api_college():
	app.logger.info('/api/college')

	colleges = []
	results = query("SELECT * FROM college")
	for row in results:
		colleges.append({'id':row[0], 'name':row[1]})

	return prepare_for_departure(content={'colleges':colleges})

@app.route('/api/user/login', methods=['POST'])
def api_login():
	try:
		session['attempts'] += 1
	except:
		session['attempts'] = 1

	post_body_obj = request_data()

	results = query("SELECT * FROM user WHERE email='%s'" % post_body_obj['email'])

	if (not results):
		return prepare_for_departure(content={"attempts":session['attempts']}, alerts=[error("Invalid login credentials")], success=False)

	pass_on_record = results[0][4]
	pass_attempt = md5(str(post_body_obj['password']))

	if(pass_on_record!=pass_attempt):
		return prepare_for_departure(content={"attempts":session['attempts']}, alerts=[error("Invalid login credentials")], success=False)

	session['user_id'] = results[0][0]
	session['email'] = results[0][3]
	session['college_id'] = results[0][5]
	session['attempts'] = 0

	course_results = query("SELECT completed_course.course_id, course.name FROM completed_course, course WHERE transfer_id=%s AND course.id = completed_course.course_id" % session['user_id'])
	session['courses'] = []
	for course in course_results:
		session['courses'].append({'course_id': course[0], 'course_name': course[1]})

	return prepare_for_departure(success=True)


@app.route('/api/user/logout', methods=['POST', 'GET'])
def api_logout():
	session.clear()
	return prepare_for_departure(success=True)

def request_data():
	obj = request.form
	if(not request.form):
		try:
			obj = json.loads(request.data)
		except:
			obj = {}
	return obj

def loggedIn():
	if ('user_id' in session):
		return True
	return False

def query(stmt):
	try:
		db = MySQLdb.connect("localhost","root","bbemt","creditcalc")
		cur = db.cursor()
		cur.execute(stmt)
		results = cur.fetchall()
		db.commit();
		return results
	except:
		print "!! query failed"

def warn(msg):
	return {'level':'warn', 'msg':msg}
def error(msg):
	return {'level':'error', 'msg':msg}

# content: dictionary ex: {'classes':[{'id':1}, {'id':2}]}
# alerts:  array      ex: [{'level':1, 'msg':'a warning occured!'}, {'level':0, 'msg':'a severe error has occured!'}]
def prepare_for_departure(content={}, alerts=[], success=True):
	return_obj = {'content':content, 'alerts':alerts, 'success':success}
	return json.dumps(return_obj, ensure_ascii=False)

def md5(password):
	salt = "oi87f0987n1efnp9fs8d7bf9a8df"
	salted = salt + password
	hash = hashlib.md5(salted).hexdigest()
	return hash

if __name__ == '__main__':

	handler = RotatingFileHandler('temp.log',maxBytes=10*1024*1024,backupCount=2)
	if(debug):
		handler.setLevel(logging.DEBUG)
	else:
		handler.setLevel(logging.INFO)
	app.run("0.0.0.0", debug=True)
