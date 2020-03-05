from flask import FLASK

app = Flask(__name__)

@app.route('/<string>')
def generateResponse(string):
	new = "".join(i for i in string if i.isalpha())
	if new.islower():
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
