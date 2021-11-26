from dotenv import dotenv_values

UPLOAD_FOLDER = './static/upload_dir'
UPLOAD_DIR_DIRECT = 'upload_dir'

ENV = dotenv_values(".env")

MOTOR_A_EN = int( ENV['MOTOR_A_EN'] )
MOTOR_A_PIN1 = int( ENV['MOTOR_A_PIN1'] )
MOTOR_A_PIN2 = int( ENV['MOTOR_A_PIN2'] )

MOTOR_B_EN = int( ENV['MOTOR_B_EN'] )
MOTOR_B_PIN1 = int( ENV['MOTOR_B_PIN1'] )
MOTOR_B_PIN2 = int( ENV['MOTOR_B_PIN2'] )

CAM_LT_SRC = int( ENV['CAM_LT_SRC'] )
CAM_RT_SRC = int( ENV['CAM_RT_SRC'] )

CAM_LT_ANGLE = int( ENV['CAM_LT_ANGLE'] )
CAM_RT_ANGLE = int( ENV['CAM_RT_ANGLE'] )

WHEEL_DIAMETER= float( ENV['WHEEL_DIAMETER'] )
ROBOT_SPEED   = float( ENV['ROBOT_SPEED'] )

TIME_FOR_REV = float( ENV['TIME_FOR_REV'] )
TIME_FOR_90  = float( ENV['TIME_FOR_90'] )
TIME_FOR_45  = float( ENV['TIME_FOR_45'] )
TIME_FOR_180 = float( ENV['TIME_FOR_180'] )

STEREO_VISION = bool( int(ENV['STEREO_VISION']) == 1 )

camera_config = {
    'left_cam_src' : CAM_LT_SRC,
    'left_cam_config' : {
        'angle' : CAM_LT_ANGLE
    },
    'right_cam_src': CAM_RT_SRC,
    'right_cam_config' : {
        'angle' : CAM_RT_ANGLE
    }
}

CAMERA_CONFIGS = "./configs"
CAMERA_CONFIGS_STEREO_MAP = CAMERA_CONFIGS + "/stereo_map.xml"
