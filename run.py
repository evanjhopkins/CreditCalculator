from flask import Flask, render_template, request, session
import logging
from logging.handlers import RotatingFileHandler
import hashlib
import MySQLdb
import json
import urllib2
import re

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
	return render_template('index.html', data = response_obj)

@app.route('/courses')
def classes():
	app.logger.info('/courses')
	response = api_course(None)
	response_obj = json.loads(response)
	return render_template('courses.html', data=response_obj)

@app.route('/user/new')
def user_new():
	app.logger.info('/user/new')
	response_obj = {}
	return render_template('user_new.html', data=response_obj)

@app.route('/user/login')
def user_login():
	response_obj = {}
	return render_template('user_login.html', data=response_obj)

#########
#  API  #
#########
@app.route('/api/course/', defaults={'course_id':None})
@app.route('/api/course/<int:course_id>')
def api_course(course_id):
	app.logger.info('/api/course/')

	# statement depends on if were looking for one class, or all classes
	if (course_id):
		results = query("SELECT * FROM course WHERE id="+str(course_id))
	else:
		results = query("SELECT * FROM course")

	courses = []
	for row in results:
		courses.append( { 'id':row[0], 'title':re.sub(r'[^\x00-\x7F]','', row[1]), 'subject':row[2], 'number':row[3]} )

	return prepare_for_departure(content={'courses':courses})

@app.route('/api/course/new', methods=['POST'])
def api_course_new():
	app.logger.info('/api/course/new')

	post_body = request.data
	post_body_obj = json.loads(post_body)

	course_name = post_body_obj['course']['name']
	course_subject = post_body_obj['course']['subject']
	course_number = post_body_obj['course']['course_number']
	course_college_id = post_body_obj['course']['college_id']

	query("INSERT INTO course (name, subject, course_number, college_id) VALUES ('%s', '%s', %s, %s)" % (course_name, course_subject, course_number, course_college_id))
	prepare_for_departure(success=True)


@app.route('/api/college')
def api_college():
	app.logger.info('/api/college')

	colleges = []
	results = query("SELECT * FROM college")
	for row in results:
		colleges.append({'id':row[0], 'name':row[1]})

	return prepare_for_departure(content={'colleges':colleges})

@app.route('/api/user/new',  methods=['POST'])
def api_user_new():
	app.logger.info('/api/user/new')
	post_body = request.data

	try:#invalid json will cause a crash
		post_body_obj = json.loads(post_body)
	except:
		return prepare_for_departure(alerts=[error("Invalid JSON")], success=False)

	user = post_body_obj['user']
	hashed_pass = md5(user['password_hash'])

	query("""INSERT INTO user (first_name, last_name, email, password_hash, college_id) 
			 VALUES('%s', '%s', '%s', '%s', %s)""" %
			 (user['first_name'], user['last_name'], user['email'], hashed_pass, user['college_id']))

	return prepare_for_departure(success=True)	

@app.route('/api/user/<int:user_id>/courses')
def api_user_courses(user_id):
	app.logger.info('/api/user/<int:user_id>/courses')
	result = query("SELECT course.* FROM completed_course, course WHERE completed_course.course_id = course.id AND transfer_id=%s" % user_id)
	courses = []
	for course in result:
		courses.append({'id':course[0], 'name':course[1], 'subject':course[2], 'course_number':course[3], 'college_id':course[4]})

	return prepare_for_departure(content={'courses':courses})

@app.route('/api/user/<int:user_id>/courses/add', methods=['POST'])
def api_user_courses_add(user_id):
	app.logger.info('/api/user/<int:user_id>/courses/add')
	post_body = request.data

	try:#invalid json will cause a crash
		post_body_obj = json.loads(post_body)
	except:
		return prepare_for_departure(alerts=[error("Invalid JSON")], success=False)

	for course in post_body_obj['courses']:
		query("INSERT INTO completed_course (transfer_id, course_id) VALUES(%s, %s)" % (user_id, course['course_id']))

	return prepare_for_departure(success=True)

@app.route('/api/user/<int:user_id>/courses/remove', methods=['POST'])
def api_user_courses_remove(user_id):
	app.logger.info('/api/user/<int:user_id>/courses/remove')
	post_body = request.data

	try:#invalid json will cause a crash
		post_body_obj = json.loads(post_body)
	except:
		return prepare_for_departure(alerts=[error("Invalid JSON")], success=False)

	for course in post_body_obj['courses']:
		query("DELETE FROM completed_course WHERE transfer_id=%s AND course_id=%s" % (user_id, course['course_id']))

	return prepare_for_departure(success=True)

@app.route('/api/user/login', methods=['POST'])
def api_login():
	try:
		session['attempts'] += 1
	except:
		session['attempts'] = 1

	post_body_obj = getData()
	
	results = query("SELECT * FROM user WHERE email='%s'" % post_body_obj['email'])

	if (not results):
		return prepare_for_departure(content={"attempts":session['attempts']}, alerts=[error("Invalid login credentials")], success=False)

	pass_on_record = results[0][4]
	pass_attempt = md5(str(post_body_obj['password']))

	if(pass_on_record==pass_attempt):
		session['email'] = results[0][3]
		session['college_id'] = results[0][5]
		session['attempts'] = 0
		return prepare_for_departure(success=True)
	else:
		return prepare_for_departure(content={"attempts":session['attempts']}, alerts=[error("Invalid login credentials")], success=False)

@app.route('/api/user/logout', methods=['POST', 'GET'])
def api_logout():
	session.clear()
	return prepare_for_departure(success=True)

def getData():
	obj = request.form
	if(not request.form):
		try:
			obj = json.loads(request.data)
		except:
			obj = {}
	return obj


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