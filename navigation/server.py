from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os
from modules.helpers import allowed_file, get_new_filename
import config as ENV
from modules.database import DB
from modules.planner import SrcImage, Planner

# create the database
db = DB()
db.create_tables()

app = Flask( __name__ )
app.config['UPLOAD_FOLDER'] = ENV.UPLOAD_FOLDER
 

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
        new_file_name, file_ext = get_new_filename( file.filename )
        file.save( os.path.join( app.config['UPLOAD_FOLDER'], new_file_name ) )

        db.insert_map_entry( new_file_name, file_ext, '1920', '1080' )

        return jsonify(
            error=False,
            message='File uploaded'
        )
    return jsonify(
        error=True,
        message='Something went wrong'
    )

@app.route("/get_maps", methods=["GET"])
def get_maps():
    paths = db.get_paths()
    #print(paths)
    if not paths:
        return jsonify(
            error=True,
            paths=[],
        )
    else:
        return jsonify(
            error=False,
            paths=paths
        )

@app.route("/robot_commands", methods=["POST"])
def robot_commands():
    pass

@app.route("/test")
def test():
    path = Planner(  'b3898d0e-ea1c-434b-b9b5-f354cead4217.jpg', 1920, 1080 )
    path.process_image()



    # image = SrcImage( 'b3898d0e-ea1c-434b-b9b5-f354cead4217.jpg' )
    # imData = image.get_image()
    # print( imData )
    # print("test path")
    
    return jsonify(
        error=False
    )

if __name__ == '__main__':
    app.run( debug=True, host='0.0.0.0', port=8080 )
