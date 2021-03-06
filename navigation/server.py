from flask import Flask, render_template, request, url_for, flash, redirect, jsonify
from werkzeug.datastructures import FileMultiDict
from numpy import add
from werkzeug.utils import secure_filename
import os
from algorithm.process_map import ProcessMap
from modules.helpers import allowed_file, get_new_filename
import config as ENV
from modules.database import DB
from modules.planner import SrcImage, Planner
from mem_db.memdb import MemDB
import json
import base64

# create the database
db = DB()
db.create_tables()

memRedis = MemDB()

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

    # get grid map and obstacles
    processMap = ProcessMap( entry )
    obstacle_pos = processMap.get_obstacle_pos_for_graph()
    grid_map_pos = processMap.get_grid_map_pos_for_graph()

    return render_template( 'map.html', map_uuid=file_uuid, obstacles=json.dumps( obstacle_pos ), grid_map=json.dumps( grid_map_pos )  )

@app.route("/set_robot_goals", methods=["POST"])
def set_robot_goals():
    ready = True
    if 'startx' not in request.form:
        ready = False
    if 'starty' not in request.form:
        ready = False
    if 'endx' not in request.form:
        ready = False
    if 'endy' not in request.form:
        ready = False
    if 'map_id' not in request.form:
        ready = False

    # if has a history of obstacle take descition to clear data or not
    clearObstacles = False

    if not ready:
        return jsonify(
                error=True,
                message='Data not ready'
        )

    file_uuid = request.form['map_id']

    entry = db.get_entry( file_uuid )
    
    start_node = ( int(request.form['startx']), int(request.form['starty']) )
    goal_node  = ( int(request.form['endx']), int(request.form['endy']) )

    if 'reset_obstacles' in request.form:
        clearObstacles = bool( int( request.form['reset_obstacles'] ) == 1 )

    additional_obstacles = []

    # reset obstacle postions
    if clearObstacles:
        db.reset_map_positions( file_uuid )
        db.reset_map_obstacles( file_uuid )
    else:
        additional_obstacles = db.get_obstacles( file_uuid )

    #print(additional_obstacles)

    # get the grid map and obstacles
    processMap = ProcessMap( entry, additional_obs=additional_obstacles )
    plannedPath= processMap.get_path( start_node, goal_node )
    planned_motion=processMap.get_planned_motion()

    #print(planned_motion)

    # save command to file
    command_file = file_uuid + ".txt"
    f = open(command_file, "w")
    for read in planned_motion:
        cmd = str(read['from'][0]) + "," + str(read['from'][1]) + "," + str(read['distance']) + "," + read['turn'] + "," + str(read['angle']) + "\n"
        f.write( cmd )
    f.close()

    return jsonify(
            success=True,
            path=plannedPath,
            motion=planned_motion,
            message='Path planned'
    )


@app.route("/set_robot_pos", methods=["POST"])
def set_robot_pos():
    ready = True
    if 'robot_x' not in request.form:
        ready = False
    if 'robot_y' not in request.form:
        ready = False
    if 'map_id' not in request.form:
        ready = False
    
    if not ready:
        return jsonify(
            error=True,
            message='Pos not recieved'
        )

    file_uuid = request.form['map_id']
    robot_pos = ( int( request.form['robot_x']), int( request.form['robot_y'] ) )
    db.reset_map_positions( file_uuid ) # remove current robot pos
    db.set_robot_position( file_uuid, robot_pos )

    has_obstacle = False
    if 'obs_x' in request.form and 'obs_y' in request.form:
        has_obstacle = True

    if has_obstacle:
        obstacle  = ( int( request.form['obs_x']), int( request.form['obs_y'] ) )
        db.set_obstacles( file_uuid, obstacle )

    return jsonify(
        error=False,
        message='Robot position set'
    )

@app.route("/robot_commands", methods=["POST"])
def robot_commands():
    pass

@app.route("/robot_status", methods=["GET"])
def robot_status():
    file_uuid = request.args['map_id']
    robot_pos = db.get_robot_position( file_uuid )
    obstacle_pos = db.get_obstacles( file_uuid )
    
    return jsonify(
        success=True,
        robot_pos=robot_pos,
        obstacle_pos=obstacle_pos
    )

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
