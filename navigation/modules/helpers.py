import os
import uuid

ALLOWED_EXTENSIONS = {'jpg', 'png'}

def path_exists(path):
    return os.path.exists( path )

def create_paths(path):
    pathExists = os.path.exists( path )
    if not pathExists:
        os.makedirs( path )
        print( path + " PATH CREATED" )
    else:
        print( path + " PATH EXISTS" )

def allowed_file( filename ):
    return '.' in filename and \
            filename.rsplit( '.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_new_filename( filename ):
    file_name, file_ext = os.path.splitext( filename )
    new_file_name = str( uuid.uuid4() ) + file_ext
    return new_file_name, file_ext