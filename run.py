from flask import Flask
from flask import render_template
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

@app.route('/classes')
def classes():
	response = api_classes(None)
	response_obj = json.loads(response)
	return render_template('classes.html', data=response_obj)

@app.route('/api/course/get', defaults={'course_id':None})
@app.route('/api/course/get/<int:course_id>')
def api_classes(course_id):
	db = MySQLdb.connect("localhost","root","bbemt","creditcalc")
	cur = db.cursor()

	# statement depends on if were looking for one class, or all classes
	if (course_id):
		stmt = "SELECT * FROM course WHERE id="+str(course_id)
	else:
		stmt = "SELECT * FROM course "

	classes = []
	try:
		cur.execute(stmt)
		results = cur.fetchall()
		for row in results:
			class_id = row[0]
			class_title = re.sub(r'[^\x00-\x7F]','', row[1])
			class_subject = row[2]
			class_number = row[3]
			classes.append( { 'id':class_id, 'title':class_title, 'subject':class_subject, 'number':class_number} )
	except:
		print "/api/couse/get request failed"
		return {}

	# if no results were found
	if (len(classes) < 1):
		return json.dumps(prepare_for_departure({}, [warn("No results found")]), ensure_ascii=False)
	# if fetching single class
	if (len(classes) == 1):
		return json.dumps(prepare_for_departure(classes[0]), ensure_ascii=False)
	# else, must be multiple classes
	return json.dumps(prepare_for_departure({'classes':classes}), ensure_ascii=False)

@app.route('/api/college/get')
def api_school():
	db = MySQLdb.connect("localhost","root","bbemt","creditcalc")
	cur = db.cursor()
	stmt = "SELECT * FROM college"
	colleges = []
	try:
		cur.execute(stmt)
		results = cur.fetchall()
		for row in results:
			college_id = row[0]
			college_name = row[1]
			colleges.append({'id':college_id, 'name':college_name})
	except:
		test = "/api/college/get request failed"
		return {}

	return json.dumps(prepare_for_departure({'colleges':colleges}) , ensure_ascii=False)

def warn(msg):
	return {'level':1, 'msg':msg}
def error(msg):
	return {'level':0, 'msg':msg}

# content: dictionary ex: {'classes':[{'id':1}, {'id':2}]}
# errors:  array      ex: [{'level':1, 'msg':'a warning occured!'}, {'level':0, 'msg':'a severe error has occured!'}] 
def prepare_for_departure(content, errors=[]):
	return_obj = {'content':content, 'errors':errors }
	return return_obj

if __name__ == '__main__':
	app.run("0.0.0.0", debug=True)
