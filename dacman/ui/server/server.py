# server.py
from flask import Flask, render_template, json
from astropy.io import fits
app = Flask(__name__, static_folder='../fits/build/static', template_folder='../fits/build')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/api/fitstest')
def api_fits_test():
	hdul = fits.open('../spCFrame-b1-00161868.fits')
	output = hdul[5].header[3]
	print(output)
	return json.jsonify({
		'output' : output
	})

@app.route('/api/fitsinfo')
def api_fits_info():
	hdul = fits.open('../spCFrame-b1-00161868.fits')
	output = hdul.info(output=False)
	#print("output is")
	#print(output)
	#return json.jsonify({
	#	'output' : output
	#})
	return json.jsonify(output)

@app.route('/hello')
def hello():
    return 'Hello World!'

if __name__ == '__main__':
    app.run()
