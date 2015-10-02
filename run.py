from flask import Flask
from flask import render_template
app = Flask(__name__)

@app.route('/')
@app.route('/index')
def index():
	return render_template('index.html')
#	return 'hello world'
@app.route('/classes')
def classes():
	return render_template('classes.html')

if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
