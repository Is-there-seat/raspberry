import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import spidev, time

cred = credentials.Certificate("./isthereseat-ad7a5-firebase-adminsdk-b16hc-547c1e9770.json")
firebase_admin.initialize_app(cred, {"databaseURL" : "https://isthereseat-ad7a5-default-rtdb.firebaseio.com/"})

doc_ref = db.reference("sujung/")

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def analog_read(channel) :
	if channel > 7 or channel < 0:
		return -1
	r = spi.xfer2([1, (8 + channel) << 4, 0])
	adc_out = ((r[1] & 3) << 8) + r[2]
	return adc_out

mcp3008 = 0
temp = 0

flag = False
null_input_count = 0
input_count = 0

try:
	seat = doc_ref.child("0101").get()
	print("default seat : " + str(seat))
	while True:
		reading = analog_read(mcp3008)
		print("Readed data %d\t " % (reading))

		# 20분대기 1 사용중 0 

		input = reading 
		

		if input >= 780 and input_count < 6:
		# 새로 누가 앉았을때임 
			output = 0
			input_count += 1
			print("input_count1 : " + str(input_count))
			null_input_count = 0 
			print("null_input_count1 : " + str(null_input_count))
			flag = False

		elif input >= 780 and input_count >= 6:
		# 누가 앉은게 확정됨  
			output = 0
			flag = True
		
		elif input < 780 and null_input_count <40:
		# 누가 자리를 떠난지 얼마안됨. 현재는 자리에 없음 
			if flag == False :
				output = -1
				input_count = 0 
				print("input_count2 : " + str(input_count))
			else :
				null_input_count += 1
				print("null_input_count2 : " + str(null_input_count))
				output = 1
				input_count = 0

		elif input < 780 and null_input_count >= 40:
		# 누가 확실히 없음이 확인됨
			output = -1
			input_count = 0 
		
		
		if seat != output:
			db.reference("sujung/").update({"0101" : output})
			print("바뀜 " + str(output))
			seat = output

		temp = reading
		time.sleep(0.5)

except KeyboardInterrupt:
	pass

