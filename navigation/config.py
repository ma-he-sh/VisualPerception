from dotenv import dotenv_values

ENV = dotenv_values(".env")

MOTOR_A_EN = int( ENV['MOTOR_A_EN'] )
MOTOR_A_PIN1 = int( ENV['MOTOR_A_PIN1'] )
MOTOR_A_PIN2 = int( ENV['MOTOR_A_PIN2'] )

MOTOR_B_EN = int( ENV['MOTOR_B_EN'] )
MOTOR_B_PIN1 = int( ENV['MOTOR_B_PIN1'] )
MOTOR_B_PIN2 = int( ENV['MOTOR_B_PIN2'] )
