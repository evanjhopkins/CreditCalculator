from flask import Flask, render_template, request, session
import logging
from logging import Formatter
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
	app.logger.critical('/index')
	response = api_college()
	response_obj = json.loads(response)
	return render_template('index.html', data = response_obj)

@app.route('/overview')
def overview():
	scenarios = [
		{'major':'Math', 'minor':'Art' },
		{'major':'Computer Science', 'minor':'Math'},
		{'major':'Economics', 'minor':'Business Administration'}
	]
	return render_template('overview.html', data={'scenarios':scenarios})

@app.route('/majors')
def majors():
	response_obj = {'majors':[
		{'name':"Criminal Justice", 'percent':randint(0,99), 'id':1},
		{'name':"Computer Science", 'percent':randint(0,99), 'id':2},
		{'name':"Female Studies", 'percent':randint(0,99), 'id':3},
		{'name':"Biology", 'percent':randint(0,99), 'id':4}
	]}
	return prepare_for_departure(content=response_obj, success=True)

@app.route('/minors')
def minors():
	response_obj = {'minors':[
		{'name':"Criminal Justice", 'percent':randint(0,99), 'id':1},
		{'name':"Computer Science", 'percent':randint(0,99), 'id':2},
		{'name':"Female Studies", 'percent':randint(0,99), 'id':3},
		{'name':"Biology", 'percent':randint(0,99), 'id':4}
	]}
	return prepare_for_departure(content=response_obj, success=True)

@app.route('/user/new')
def user_new():
	app.logger.info('/user/new')
	response_obj = {}
	return render_template('user_new.html', data=response_obj)

@app.route('/user/login')
def user_login():
	response_obj = {}
	return render_template('user_login.html', data=response_obj)

@app.route('/admin')
@app.route('/admin/activity')
def recent_activity():
	#with open append x append y
	#if x[2] = /index
	#y = x[0] x = xcounter+1
	#else skip
	data= {}
	bar_chart = pygal.StackedLine()
	bar_chart.title= "User Activity"
	bar_chart.x_labels = map(str,range(11))
	bar_chart.add('Requested Courses', [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55])
	bar_chart.add('Added Users', [1, 1, 1, 2, 2, 3, 4, 5, 7, 9, 12])
	chart = bar_chart.render(is_unicode=True)
	return render_template('activity.html',data=data,chart =chart)

@app.route('/admin/users')
def admin_user_list():

	response_obj = api_users()
	response_obj=json.dumps(response_obj,ensure_ascii=False)
	response_obj=json.loads(response_obj)




	return render_template('admin_users.html',data=response_obj,alternate=10)#data= response_obj)


@app.route('/admin/user_info/delete/<user_id>')
def admin_delete_user(user_id):
	api_remove_user(user_id)

	return render_template('admin_remove_user.html',data=user_id)

@app.route('/admin/course_info/delete/<course_id>')
def admin_delete_course(course_id):
	api_remove_course(course_id)

	return render_template('admin_remove_course.html',data=course_id)
@app.route('/admin/user_info/<user_id>')
def admin_user_details(user_id):
	user_id=user_id.replace('%20','')
	user_id =user_id.encode('ascii','ignore')
	user_id=user_id.split('+')
	response_obj = api_user_courses(user_id[0])
	user_name = user_id[1]+" "+user_id[2]
	userid = user_id[0]
	# response_obj=json.dumps(response_obj,ensure_ascii=False)
	# #print response_obj
	response_obj=json.loads(response_obj)
	print response_obj
	return render_template('admin_users_details.html',data=response_obj,alternate=10,userid=userid,user_name=user_name)#data= response_obj)

@app.route('/admin/courses')
def admin_course_list():

	response_obj = api_course_list()
	response_obj=json.dumps(response_obj,ensure_ascii=False)
	response_obj=json.loads(response_obj)
	return render_template('admin_course.html',data=response_obj,alternate=10)#data= response_obj)
@app.route('/admin/course/mapping')
def admin_course_mapping():
	#thinking of having two text box lists and whateve is selected gets relation ships
	return render_template('mapping.html')
@app.route('/admin/course_info/<course_id>')
def admin_course_details(course_id):
	course_id=course_id.replace('%20','')
	course_id =course_id.encode('ascii','ignore')
	course_id=course_id.split('+')
	print course_id[0]
	response_obj = api_admin_course(course_id[0])
	course_name = course_id[1]
	course_id = course_id[0]
	# response_obj=json.dumps(response_obj,ensure_ascii=False)
	# #print response_obj
	response_obj=json.loads(response_obj)
	print response_obj


	return render_template('admin_course_details.html',data=response_obj,alternate=10,course_id=course_id,course_name=course_name)#data= response_obj)

#########
#  API  #
#########
@app.route('/api/admin/remove_user/<userid>')
def api_remove_user(userid):
	app.logger.critical('/api/remove_user/'+userid)
	query("DELETE FROM user WHERE id =%s" % userid)

@app.route('/api/admin/remove_course/<courseid>')
def api_remove_course(courseid):
	app.logger.critical('/api/remove_course/'+courseid)
	query("DELETE FROM course WHERE id =%s" % courseid)

@app.route('/api/admin/users')
def api_users():
	app.logger.info('/api/admin')
	results = query("SELECT user.id,user.first_name,user.last_name,user.college_id,user.email FROM user")
	users= []
	for row in results:
		users.append({'id':row[0],'first_name':row[1],'last_name':row[2],'college_id':row[3],'email':row[4]})
	return users

@app.route('/api/admin/course')
def api_course_list():
	results = query("SELECT * FROM course")
	courses= []
	for row in results:
		courses.append({'course_id':row[0], 'course_name':row[1], 'course_subject':row[2], 'course_number':row[3],'college_id':row[4]})

	return courses

@app.route('/api/admin/courses/<course_id>')
def api_admin_course(course_id):

	result = query("SELECT * FROM course WHERE course.id =%s" % course_id)
	courses = []
	for course in result:
		courses.append({'id':course[0], 'name':course[1], 'subject':course[2], 'course_number':course[3], 'college_id':course[4]})

	return prepare_for_departure(content={'courses':courses},success=True)

@app.route('/api/course/<int:course_id>')
def api_course(course_id):
	results = query("SELECT * FROM course WHERE course.id=%s" % course_id)
	course_obj = results[0]
	course = {'course':{'course_id':course_obj[0], 'course_name':course_obj[1], 'course_subject':course_obj[2], 'course_number':course_obj[3]}}
	return prepare_for_departure(content=course, success=True)

@app.route('/api/college/<int:college_id>/course')
def api_college_course(college_id):
	app.logger.info('/api/course/')

	# statement depends on if were looking for one class, or all classes
	results = query("SELECT * FROM course WHERE course.college_id=%s" % college_id)

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

#api v.02
@app.route('/api/user/college/<int:college_id>')
def api_user_setcollege(college_id):

	if (loggedIn()):
		query("UPDATE user SET college_id=%s WHERE id=%s" % (college_id, session['user_id']))

	session['college_id'] = college_id

	#since the college has just changed, we need to update session with courses
	#from the current college
	session['courses'] = []
	if(loggedIn()):
		course_results = query("SELECT completed_course.course_id, course.name FROM completed_course, course WHERE transfer_id=%s AND course.id = completed_course.course_id AND course.college_id=%s" % (session['user_id'], college_id))
		for course in course_results:
			session['courses'].append({'course_id': course[0], 'course_name': course[1]})

	return prepare_for_departure(success=True)

@app.route('/api/user/scenarios')
def api_user_scenarios():
	api.logger.info('/api/user/scenarios')
	scenarios = []
	sql = ""
	response_obj = [
		{'major':"Biology", 'minor':"Chemistry"}
	]
	return prepare_for_departure(content=response_obj, success=True)

@app.route('/api/user/scenarios/new', methods=['POST'])
def api_user_scenarios_new():
	post_body_obj = request_data()
	print post_body_obj['scenario']['major']
	#print(post_body_obj['scenario'])
	#query("INSERT INTO scenario (user_id) VALUES(%s)" % session['user_id'])
	scenario_id = -1
	try:
		db = MySQLdb.connect("localhost","root","bbemt","creditcalc")
		cur = db.cursor()
		cur.execute( "INSERT INTO scenario (user_id) VALUES(%s)" % session['user_id'])
		scenario_id = cur.lastrowid
		sql = "INSERT INTO scenario_program (scenario_id, program_id) VALUES(%s, %s)" % (scenario_id, post_body_obj['scenario']['major'])
		cur.execute("INSERT INTO scenario_program (scenario_id, program_id) VALUES(%s, %s)" % (scenario_id, post_body_obj['scenario']['major']))
		cur.execute("INSERT INTO scenario_program (scenario_id, program_id) VALUES(%s, %s)" % (scenario_id, post_body_obj['scenario']['minor']))
		results = cur.fetchall()
		db.commit();
		#return results
		return prepare_for_departure(success=True, content={})

	except:
		print "!! query failed"

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

@app.route('/api/user/courses')
def api_user_courses():
	app.logger.info('/api/user/<int:user_id>/courses')
	if(loggedIn()):
		result = query("SELECT course.* FROM completed_course, course WHERE completed_course.course_id = course.id AND transfer_id=%s" % session['user_id'])
		courses = []
		for course in result:
			courses.append({'id':course[0], 'name':course[1], 'subject':course[2], 'course_number':course[3], 'college_id':course[4]})
		return prepare_for_departure(content={'courses':courses}, success=False)
	return prepare_for_departure(success=False)

@app.route('/api/user/courses', methods=['POST'])
def api_user_courses_add():

	app.logger.info('/api/user/<int:user_id>/courses/add')
	post_body_obj = request_data()

	courses = []
	for course_id in post_body_obj['courses']:
		result = query("SELECT * FROM course WHERE course.id=%s" % course_id)
		course_name = result[0][1]
		courses.append({'course_id':course_id, "course_name":course_name})

	session['courses'] = courses

	if (loggedIn()):
		query("DELETE FROM completed_course WHERE transfer_id=%s" % session['user_id'])
		for course_id in post_body_obj['courses']:
			query("INSERT INTO completed_course (transfer_id, course_id) VALUES(%s, %s)" % (session['user_id'], course_id))

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

@app.route('/api/user/setmajor', methods=['POST'])
def api_user_setmajor():
	post_body_obj = request_data()

	session['majors'] = post_body_obj['majors']
	print "added majors to session"
	if loggedIn():
		print "added majors to account"

	return prepare_for_departure(success=True)

@app.route('/api/user/college')
def api_user_college():
	if(loggedIn()):
		college = query("SELECT college_id FROM user WHERE id='%s'" % session['user_id'])[0][0]
		response_obj = {'college_id': college}
		return prepare_for_departure(success=True, content=response_obj)
	return prepare_for_departure(success=False)

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

	logger = RotatingFileHandler('temp.log',maxBytes=10*1024*1024,backupCount=2)
	logger.setLevel(logging.DEBUG)
	logger.setFormatter(Formatter('%(asctime)s,''%(message)s'))
	app.logger.addHandler(logger)

	info_handler = RotatingFileHandler('info_temp.log',maxBytes=10*1024*1024,backupCount=2)
	info_handler.setLevel(logging.CRITICAL)
	info_handler.setFormatter(Formatter('%(asctime)s,''%(message)s'))
	app.logger.addHandler(info_handler)

	app.run("0.0.0.0", debug=True)
