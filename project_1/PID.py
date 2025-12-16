import time
import math
import Adafruit_BBIO.GPIO as GPIO
import board
import busio
import adafruit_bno055

############################################
# PIN SETUP
############################################
STEP_PIN  = "P1_36"
DIR_PIN   = "P1_34"
STEP_PIN2 = "P1_32"
DIR_PIN2  = "P1_30"

GPIO.setup(STEP_PIN,  GPIO.OUT)
GPIO.setup(DIR_PIN,   GPIO.OUT)
GPIO.setup(STEP_PIN2, GPIO.OUT)
GPIO.setup(DIR_PIN2,  GPIO.OUT)

############################################
# PID CONFIGURATION
############################################
Kp = 2.0
Ki = 1.5
Kd = 0.0

target_angle = 2.75# Balance angle
integral = 0.0
last_error = 0.0
last_time = time.time()

# Initialize I2C bus (adjust if using a different bus or UART)
i2c = busio.I2C(board.SCL, board.SDA)

# Initialize BNO055 sensor
sensor = adafruit_bno055.BNO055_I2C(i2c)

############################################
# STEPPER FUNCTIONS
############################################
def step_both(num_steps):
    """
    speed = signed value
      - positive → forward
      - negative → backward
      - magnitude = speed of stepping
    """
    if num_steps == 0:
        return
    
    # Set direction
    if num_steps > 0:
        GPIO.output(DIR_PIN, 0)
        GPIO.output(DIR_PIN2, 1)
    else:
        GPIO.output(DIR_PIN, 1)
        GPIO.output(DIR_PIN2, 0)
    #delay = max(0.0005, 0.02 - min(abs(speed)/200.0, 0.019))

    step_delay = 0.0001  # 100 microseconds = 10kHz step rate
    
    # Execute steps
    abs_steps = abs(num_steps)
    for _ in range(abs_steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        GPIO.output(STEP_PIN2, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(STEP_PIN, GPIO.LOW)
        GPIO.output(STEP_PIN2, GPIO.LOW)
        time.sleep(step_delay)

############################################
# MAIN LOOP
############################################
print("Starting PID control... CTRL+C to exit")

LOOP_FREQ = 60  # 50Hz = 20ms per loop
LOOP_PERIOD = 1.0 / LOOP_FREQ

try:
    while True:
        loop_start = time.time()

        # -------- Read angle --------
        euler_angles = sensor.euler

        if euler_angles is not None:
            pitch = euler_angles
        else:
            print("Sensor data not available or not calibrated.")

        angle = pitch[2]
        now = time.time()
        dt = now - last_time
        last_time = now

        # -------- PID calculations --------
        error = target_angle - angle
        integral += error * dt
        MAX_INTEGRAL = 100.0
        integral = max(-MAX_INTEGRAL, min(integral, MAX_INTEGRAL))
        derivative = (error - last_error) / dt if dt > 0 else 0
        last_error = error

        # PID output
        output = Kp*error + Ki*integral + Kd*derivative

        # -------- Drive motors --------
        SCALE_FACTOR = 0.5  # Start conservative, tune as needed
        steps_to_take = int(output * SCALE_FACTOR)
        MAX_STEPS_PER_LOOP = 50
        steps_to_take = max(-MAX_STEPS_PER_LOOP, min(steps_to_take, MAX_STEPS_PER_LOOP))
        step_both(steps_to_take)

        # Debug print
        print("Angle: {:6.2f} | Error: {:6.2f} | PID: {:7.2f}".format(angle, error, output))

        # -------- Maintain loop timing --------
        elapsed = time.time() - loop_start
        sleep_time = LOOP_PERIOD - elapsed
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            print("Warning: Loop time exceeded target ({:.3f}s)".format(elapsed))

except KeyboardInterrupt:
    GPIO.cleanup()
    print("Stopped.")
