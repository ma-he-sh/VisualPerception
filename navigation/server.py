from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os
import config as ENV
from modules.database import DB

# create the database
db = DB()
db.create_tables()

ALLOWED_EXTENSIONS = {'jpg', 'png'}

app = Flask( __name__ )
app.config['UPLOAD_FOLDER'] = ENV.UPLOAD_FOLDER

def allowed_file( filename ):
    return '.' in filename and \
            filename.rsplit( '.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def main():
    return render_template( 'index.html' );

@app.route("/upload_map", methods=["POST"])
def upload_map():
    if 'file' not in request.files:
        return jsonify( 
                error=True,
                message='File not selected',
        )
    file = request.files['file']
    if file.filename == '':
        return jsonify(
                error=True,
                message='File not selected',
        )
    if file and allowed_file( file.filename ):
        filename = secure_filename( file.filename )
        file.save( os.path.join( app.config['UPLOAD_FOLDER'], filename ) )
        return jsonify(
            error=False,
            message='File uploaded'
        )
    return jsonify(
        error=True,
        message='Something went wrong'
    )

if __name__ == '__main__':
    app.run( debug=True, host='0.0.0.0', port=8080 )
