from dotenv import dotenv_values

UPLOAD_FOLDER = './upload_dir'

ENV = dotenv_values(".env")

MOTOR_A_EN = int( ENV['MOTOR_A_EN'] )
MOTOR_A_PIN1 = int( ENV['MOTOR_A_PIN1'] )
MOTOR_A_PIN2 = int( ENV['MOTOR_A_PIN2'] )

MOTOR_B_EN = int( ENV['MOTOR_B_EN'] )
MOTOR_B_PIN1 = int( ENV['MOTOR_B_PIN1'] )
MOTOR_B_PIN2 = int( ENV['MOTOR_B_PIN2'] )

camera_config = {
    'left_cam_src' : 0,
    'left_cam_config' : {
        'angle' : 90
    },
    'right_cam_src': 2,
    'right_cam_config' : {
        'angle' : -90
    }
}