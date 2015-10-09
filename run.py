from flask import Flask
from flask import render_template
from flask import request
import MySQLdb
import json
import urllib2
import re

app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	response = api_school()
	response_obj = json.loads(response)
	return render_template('index.html', data = response_obj)

@app.route('/courses')
def classes():
	response = api_course(None)
	response_obj = json.loads(response)
	return render_template('courses.html', data=response_obj)

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

@app.route('/api/college')
def api_school():
	colleges = []
	results = query("SELECT * FROM college")
	for row in results:
		colleges.append({'id':row[0], 'name':row[1]})

	return prepare_for_departure(content={'colleges':colleges})

@app.route('/api/user/new',  methods=['POST'])
def api_user_new():
	post_body = request.data
	post_body_obj = json.loads(post_body)
	user = post_body_obj['user']

	query("""INSERT INTO user (first_name, last_name, email, password_hash, college_id) 
		     VALUES('%s', '%s', '%s', '%s', %s)""" %
		     (user['first_name'], user['last_name'], user['email'], user['password_hash'], user['college_id']))

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

if __name__ == '__main__':
	app.run("0.0.0.0", debug=True)