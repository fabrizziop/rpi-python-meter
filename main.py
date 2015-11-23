import RPi.GPIO as GPIO
import time
import math
import os
import multiprocessing

resistor_list = [8200,2000,1000,576]
default_resistor = 3
rc_constant = 1
max_voltage = 11.5
ref_voltage = 9
log_desired = math.log(1-(ref_voltage/max_voltage))

GPIO.setwarnings(False)
pin_p_mosfet=31
pin_n_mosfet=29
pin_detect=33
GPIO.setmode(GPIO.BOARD)
GPIO.setup(pin_p_mosfet, GPIO.OUT)
GPIO.setup(pin_n_mosfet, GPIO.OUT)
GPIO.setup(pin_detect, GPIO.IN, pull_up_down=GPIO.PUD_UP)

load_to_use = 0
cpu_cores = multiprocessing.cpu_count()


class single_measure(object):
	def __init__(self, pin_obj):
		self.pin_obj = pin_obj
	def initialize(self):
		self.end_time = False
		self.enabled = False
	def reset_time(self):
		self.init_time = time.time()
		self.enabled = True
	def store_time(self,_):
		#print("STORED:",time.time())
		if self.end_time == False and self.enabled == True:
			self.end_time = time.time()
	def is_valid(self):
		if self.end_time == False:
			return False
		else:
			return True
	def return_time(self):
		return self.end_time - self.init_time
#~ GPIO.output(pin_p_mosfet, GPIO.HIGH)
#~ GPIO.output(pin_n_mosfet, GPIO.LOW)
#~ time.sleep(0.5)
#~ GPIO.output(pin_p_mosfet, GPIO.LOW)
#~ GPIO.output(pin_n_mosfet, GPIO.LOW)
#~ time.sleep(4)
def discharge_capacitor(p1, p2):
	GPIO.output(p1, GPIO.HIGH)
	GPIO.output(p2, GPIO.HIGH)
def charge_capacitor(p1, p2):
	GPIO.output(p1, GPIO.LOW)
	GPIO.output(p2, GPIO.LOW)

#measuring
cap_sel = str(input("Enter maximum capacitance to measure (in microfarads) [1000] "))
if cap_sel.isdigit() == True:
	max_capacitance = int(cap_sel)* (10**-6)
	if int(cap_sel) <= 200:
		default_resistor = 0
else:
	max_capacitance = 1000 * (10**-6)
print("1: 8.2k")
print("2: 2k")
print("3: 1k")
print("4: 576")
res_sel = str(input("Select resistor (in ohms) ["+str(default_resistor+1)+"]"))
if res_sel.isdigit() == True and int(res_sel) <= len(resistor_list):
	resistor = resistor_list[int(res_sel)-1]
else:
	resistor = resistor_list[default_resistor]
max_time = -1 * resistor * max_capacitance * log_desired
time_to_discharge = max_time / 4
print("Please select the resistor #"+str(default_resistor+1)+" of "+str(resistor)+" ohm")
	
nm1 = single_measure(pin_detect)
GPIO.add_event_detect(pin_detect,GPIO.RISING, callback=nm1.store_time)
while True:
	nm1.initialize()
	discharge_capacitor(pin_p_mosfet, pin_n_mosfet)
	time.sleep(time_to_discharge)
	nm1.reset_time()
	charge_capacitor(pin_p_mosfet,pin_n_mosfet)
	time.sleep(max_time)
	if nm1.is_valid() == True:
		capacitor = (-1*nm1.return_time()/(resistor*log_desired))
		print("Capacitance measured is:",capacitor * 10**6, "uF")
	else:
		if GPIO.input(pin_detect) == True:
			print("Capacitance is below the detection threshold")
		else:
			print("Capacitance is above the detection threshold")
	#~ if nm1.is_valid() == True:
		#~ voltage = max_voltage*(1-(math.e**(-1*nm1.return_time()/rc_constant)))
		#~ print("Voltage measured is:",voltage)
	#~ else:
		#~ if GPIO.input(pin_detect) == True:
			#~ print("Voltage is under the detection threshold")
		#~ else:
			#~ print("Voltage is above the detection threshold")
