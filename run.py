from flask import Flask
from flask import render_template
from flask import request
import hashlib
import MySQLdb
import json
import urllib2
import re

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	response = api_college()
	response_obj = json.loads(response)
	return render_template('index.html', data = response_obj)

@app.route('/courses')
def classes():
	response = api_course(None)
	response_obj = json.loads(response)
	return render_template('courses.html', data=response_obj)

@app.route('/user/new')
def user_new():
	response_obj = {}
	return render_template('user_new.html', data=response_obj)

@app.route('/api/course/', defaults={'course_id':None})
@app.route('/api/course/<int:course_id>')
def api_course(course_id):

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
	colleges = []
	results = query("SELECT * FROM college")
	for row in results:
		colleges.append({'id':row[0], 'name':row[1]})

	return prepare_for_departure(content={'colleges':colleges})

@app.route('/api/user/new',  methods=['POST'])
def api_user_new():
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
	result = query("SELECT course.* FROM completed_course, course WHERE completed_course.course_id = course.id AND transfer_id=%s" % user_id)
	courses = []
	for course in result:
		courses.append({'id':course[0], 'name':course[1], 'subject':course[2], 'course_number':course[3], 'college_id':course[4]})

	return prepare_for_departure(content={'courses':courses})

@app.route('/api/user/<int:user_id>/courses/add', methods=['POST'])
def api_user_courses_add(user_id):
	post_body = request.data

	try:#invalid json will cause a crash
		post_body_obj = json.loads(post_body)
	except:
		return prepare_for_departure(alerts=[error("Invalid JSON")], success=False)

	user_id = post_body_obj['user_id']

	for course in post_body_obj['courses']:
		query("INSERT INTO completed_course (transfer_id, course_id) VALUES(%s, %s)" % (user_id, course['course_id']))

	return prepare_for_departure(success=True)

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
	app.run("0.0.0.0", debug=True)