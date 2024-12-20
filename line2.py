import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FPS, 10)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 90)

# 핀 설정
steering_pin = 13  # 조향을 위한 PWM 핀
motor_pin = 18     # 구동을 위한 PWM 핀
frequency = 50     # PWM 주파수

# GPIO 핀 모드 설정
GPIO.setmode(GPIO.BCM)
GPIO.setup(steering_pin, GPIO.OUT)
GPIO.setup(motor_pin, GPIO.OUT)

# PWM 설정 (조향 및 구동)
steering_pwm = GPIO.PWM(steering_pin, frequency)
motor_pwm = GPIO.PWM(motor_pin, frequency)

# PWM 초기값 시작
steering_pwm.start(0)
motor_pwm.start(0)

def set_steering(angle):
    angle = max(-45, min(angle, 35))  # 각도를 -40도 이하 또는 40도 이상이 되지 않도록 제한
    angle += 5
    angle_adjusted = angle * 0.4
    duty_cycle = 2.5 + (angle_adjusted + 90) * (10 / 180)
    steering_pwm.ChangeDutyCycle(duty_cycle)

def set_motor(speed):
    duty = 7.5 + (speed * 0.025)
    motor_pwm.ChangeDutyCycle(duty)

set_motor(0)
try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # 관심 영역 설정 (이미지 하단 1/3)
        height, width = frame.shape[:2]
        roi = frame[height//3:, :]

        # HSV 색상 공간으로 변환
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 노란색 범위 정의
        lower_yellow = np.array([15, 30, 190])
        upper_yellow = np.array([55, 80, 180])

        # 노란색 마스크 생성
        mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        # 형태학적 연산으로 노이즈 제거 및 선 강화
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # 윤곽선 찾기
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 면적 기준 필터링
            min_area = 100
            filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

            if filtered_contours:
                max_contour = max(filtered_contours, key=cv2.contourArea)

                # 중앙 좌표 계산
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    # 중앙 기준 각도 계산 (각도를 반전)
                    offset = (cX - (width // 2))  # 중앙에서의 이탈 정도
                    angle = -(offset / (width // 2)) * 40  # -30 ~ 30 범위로 변환하여 반전

                    # 이탈 각도를 증폭시키기
                    amplification_factor = 2.0  # 증폭 계수
                    angle *= amplification_factor
                    # 조향 설정
                    set_steering(angle)
                    print(f"이탈 각도: {angle:.2f}도")
                    set_motor(10)  # 구동 모터 속도 설정

                # 선 그리기
                cv2.drawContours(roi, [max_contour], -1, (255, 0, 0), 2)  # 감지된 선 그리기

        # 화면 출력
        cv2.imshow('Frame', frame)
        cv2.imshow('Mask', mask)

        # 'q'를 누르면 종료
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    pass

# 정리 작업
cap.release()
cv2.destroyAllWindows()
steering_pwm.stop()
motor_pwm.stop()
GPIO.cleanup()
110, 21, 160