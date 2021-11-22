from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.utils import secure_filename
import os
from modules.helpers import allowed_file, get_new_filename
import config as ENV
from modules.database import DB
from modules.planner import SrcImage, Planner
import base64

# create the database
db = DB()
db.create_tables()

app = Flask( __name__ )
app.config['UPLOAD_FOLDER'] = ENV.UPLOAD_FOLDER
 

@app.route("/")
def main():
    paths = db.get_paths()
    return render_template( 'index.html', maps=paths )

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
    if 'map_width' not in request.form:
        return jsonify(
            error=True,
            message='Map width not defined'
        )
    if 'map_height' not in request.form:
        return jsonify(
            error=True,
            message='Map height not defined'
        )
    if file and allowed_file( file.filename ):
        filename = secure_filename( file.filename )
        file_uuid, new_file_name, file_ext = get_new_filename( file.filename )
        file.save( os.path.join( app.config['UPLOAD_FOLDER'], new_file_name ) )

        db.insert_map_entry( file_uuid, new_file_name, file_ext, request.form['map_width'], request.form['map_height'] )

        return jsonify(
            error=False,
            message='File uploaded'
        )
    return jsonify(
        error=True,
        message='Something went wrong'
    )

@app.route("/get_grid_map", methods=["GET"])
def get_grid_map():
    if 'map_uuid' not in request:
        return jsonify(
            error=True,
            message='Map file not selected'
        )
    print( request.file_uuid )

@app.route("/get_map_url", methods=["GET"])
def get_map_url():
    if request.args.get('file_uuid') is not None:
        file_uuid = request.args.get('file_uuid')
        entry = db.get_entry( file_uuid )
        if not entry:
            return jsonify(
                error=True,
                message='File uuid not found'
            )

        file_ext = entry[4]
        return jsonify(
            success=True,
            url=url_for('static', filename=ENV.UPLOAD_DIR_DIRECT + '/' + file_uuid + file_ext)
        )
    else:
        return jsonify(
            error=True,
            message='File uuid invalid'
        )

@app.route("/get_maps", methods=["GET"])
def get_maps():
    paths = db.get_paths()
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

@app.route("/delete_map", methods=["POST"])
def delete_map():
    if 'file_uuid' not in request.form:
        return jsonify(
            error=True,
            message='File uuid invalid'
        )
    else:
        file_uuid = request.form['file_uuid']
        entry = db.get_entry(file_uuid)
        if not entry:
            return jsonify(
                error=True,
                message='File uuid not found'
            )

        file_ext = entry[4]
        db.delete_entry( file_uuid )

        file_dir = ENV.UPLOAD_FOLDER + '/' + file_uuid + file_ext
        if os.path.exists( file_dir ):
            os.remove( file_dir )

        return jsonify(
            success=True,
            message='File deleted'
        )

@app.route("/run_map/<file_uuid>")
def run_map(file_uuid):
    if file_uuid is None or len(file_uuid) != 36:
        return redirect('/?map_error=invalid_uuid', 302 )

    entry = db.get_entry(file_uuid)
    if not entry:
        return redirect('/?map_error=file_not_found', 302)

    return render_template( 'map.html' )

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
