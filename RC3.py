
import RPi.GPIO as GPIO
import time

# 핀 설정
steering_pin = 13  # 조향을 위한 PWM 핀 (노란색 선)
motor_pin = 18     # 구동을 위한 PWM 핀 (초록색 선)
frequency = 50     # PWM 주파수

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(steering_pin, GPIO.OUT)
GPIO.setup(motor_pin, GPIO.OUT)

# PWM 설정 (조향 및 구동)
steering_pwm = GPIO.PWM(steering_pin, frequency)
motor_pwm = GPIO.PWM(motor_pin, frequency)

# PWM 초기값 시작
steering_pwm.start(0)  # 조향: 듀티 사이클 0
motor_pwm.start(0)     # 구동: 듀티 사이클 0

def set_steering(angle):
    """
    입력 각도에 따라 서보 모터(조향)를 설정하는 함수
    angle: -90 ~ 90 (각도)
    """
    # 서보 모터는 일반적으로 0도에서 180도 각도 범위(듀티 사이클 2.5~12.5%)
    duty_cycle = 2.5 + (angle + 90) * (10 / 180)  # -90~90도에 따라 듀티사이클 계산
    
    steering_pwm.ChangeDutyCycle(duty_cycle)

def set_motor(speed):
    """
    구동 모터 속도를 설정하는 함수
    speed: 0 ~ 100 (듀티 사이클)
    """
    duty = 7.5 + (speed * 0.025)
    motor_pwm.ChangeDutyCycle(duty)

try:
    while True:
        # 사용자로부터 속도와 조향 각도 입력 받기
        speed = float(input("구동 속도를 입력하세요 (0 ~ 100): "))
        if speed < 0 or speed > 100:
            print("속도는 0에서 100 사이여야 합니다.")
            continue
        
        angle = float(input("조향 각도를 입력하세요 (-40 ~ 40): "))
        if angle < -90 or angle > 90:
            print("조향 각도는 -90도에서 90도 사이여야 합니다.")
            continue
        
        # 입력 받은 값을 바탕으로 PWM 신호 설정
        set_motor(speed)
        set_steering(angle)
        time.sleep(0.1)

except KeyboardInterrupt:
    pass

# 정리 작업
steering_pwm.stop()
motor_pwm.stop()
GPIO.cleanup()
