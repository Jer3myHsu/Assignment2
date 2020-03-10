from flask import Flask

app = Flask(__name__)

@app.route('/')
def welcome():
	return '''<html>
    	<head>
    	</head>
    	<body>
    	<b>Welcome, to my CSCB20 website!</b>
    	</body>
    	</html>'''
@app.route('/<string>')
def generateResponse(string):
	new = "".join(i for i in string if i.isalpha())
	if string.isalpha() == False: 
		final = new
	elif new.islower():
		final = new.upper()
	elif new.isupper():
		final = new.lower()
	else:
		final = new
	return '''<html>
    	<head>
    	</head>
    	<body>
    	<b>Welcome, {0}, to my CSCB20 website!</b>
    	</body>
    	</html>'''.format(final)

if __name__ == "__main__":
	app.run()
