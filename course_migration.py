'''
Evan Hopkins
Sept. 17 2105
BBEMT Capping Team
'''
import csv
import glob
import MySQLdb

db = MySQLdb.connect("localhost","root","bbemt","creditcalc")

def isSubjectValid(course_name):
	if (any(char.isdigit() for char in course_name) ):
		return False
	return True
marist_course=[]

with open('marist_classes.csv','rb') as b:
		marist_class_reader = csv.reader(b)
		for row in marist_class_reader:
			new_course = {
    		'name'          : row[5],
    		'subject'       : row[2],
    		'course_number' : row[3],
    		'college_id'    : 2,
    	}
			marist_course.append(new_course)
print marist_course
cur = db.cursor()
for i in marist_course:
	stmt = """INSERT INTO course (name, subject, course_number, college_id) VALUES ('%s', '%s', '%s', '%s')""" % (i['name'], i['subject'], i['course_number'], 2 )
	print stmt
	cur.execute(stmt)
	db.commit()

# this array will hold all courses
courses = []

with open('courses.csv', 'rb') as f:
    reader = csv.reader(f)

    # for each row in csv...
    for row in reader:
    	# parse course from csv into a dictionary
    	new_course = {
    		'school'                : row[0],
    		'foreign_course_subject' : row[1],
    		'foreign_course_number' : row[2],
    		'foreign_course_title'  : row[3],
    		'marist_course_subject' : row[5],
    		'marist_course_number'  : row[6],
    		'marist_course_title'   : row[7]
    	}
    	# add the dictionary to the array of all courses
        courses.append(new_course)

valids = 0
cur = db.cursor()
for course in courses:

	valid = True
	errors = ""

	# here we can add validation for each column

	# (validate subjects) this example is looking for courses that have a number as their subject instead of a string
	if (not isSubjectValid(course['foreign_course_subject'])):
		valid = False
		errors = errors + " invalid foreign subj,"

	# if all validations passed...
	if (valid):
		stmt = """INSERT INTO course (name, subject, course_number, college_id) VALUES ('%s', '%s', '%s', '%s')""" % (course['foreign_course_title'], course['foreign_course_subject'], course['foreign_course_number'], 1 )
		cur.execute(stmt)
		db.commit()
		valids = valids + 1

	# alert user of courses that failed validation (and thus were not added) so they can be added manually
	else:
		#remove last comma from error string
		errors = errors[:-1]
		print "[ERROR] "+course['foreign_course_title'] + " : "+errors


print ""
print "Finished!"
print str(valids) + "/" + str(len(courses)) + " courses added successfully"
