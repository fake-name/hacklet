#!/usr/bin/python

import EmonFeeder
import time

import serial
import traceback


sensorDict = {
	"0x8855A50500": 100,
	"0x9CF3A40500": 101,
}

# Manual CRC, because it's interesting
class CRC():
	def __init__(self, crcPolynomial, crcLen=8):
		self.poly = crcPolynomial
		self.len = crcLen
		self.crc = 0
	def addByte(self, inByte):

		for x in xrange(self.len):
			mask = (inByte ^ self.crc) & 0x01
			self.crc >>= 1
			if mask:
				self.crc ^= self.poly
			inByte >>= 1

	def getResult(self):
		return self.crc

class WeatherLogger():

	dsCrcPoly = 0x8C

	def __init__(self, portStr):
		self.port = serial.Serial(portStr, 115200, timeout=0)

		self.tmpStr = ""
		self.tmpLog = []
		self.presLog = []

		self.resetArduino()

	def resetArduino(self):
		self.port.setDTR(False)
		self.port.setDTR(True)

	def __del__(self):
		print "Closing port"
		self.port.close()

	def procBaro(self, inStr):
		# print inStr
		header, content = inStr.split("|")
		# print "Header = ", "\"", header, "\""
		# print "Content = ", "\"", content, "\""
		content = content.split()
		temp = None
		pres = None
		for item in content:

			try:
				key, val = item.split(":")
				#print "key, val - ", key, float(val)

				if key == "Temperature":
					temp = float(val)
				if key == "Pressure":
					pres = float(val)
			except ValueError:
				traceback.print_exc()
				print "Started part-way through a packet"
				print "\"", item, "\""

		print "Temp:", temp, "Pres:", pres
		if pres < 90000.0:
			print "BAD PRESSURE VALUE. Ignoring readings!"
			return
		if not pres or not temp:
			print "BAD READING?. Ignoring readings!"
			return

		self.tmpLog.append(temp)
		self.presLog.append(pres)

	'''
	def procWind(self, inStr):
		print "Received Anemometer data = ", inStr
		header, content = inStr.split("|")
		# print "Header = ", "\"", header, "\""
		# print "Content = ", "\"", content, "\""

		windDir = None
		windVel = None
		extTemp = None
		extHumi = None

		content = content.split()

		for item in content:

			try:
				key, val = item.split(":")
				#print "key, val - ", key, float(val)

				if key == "Anemometer":
					windVel = float(val)
				if key == "WindDir":
					windDir = int(val)
				if key == "Temperature":
					extTemp = float(val)
				if key == "Temperature":
					extHumi = float(val)
			except ValueError:
				traceback.print_exc()
				print "Started part-way through a packet"
				print "\"", item, "\""

		#Anemometer:10160.00 WindDir:8 Humidity:39 Temperature:21
	'''

	def parseDS18B20Data(self, body):
		sensorPort = int(body[0], 16)
		devType = body[1]

		if devType != "28":
			print "This is not a DS18B20 sensor!"

		sensID = body[1:9]
		sensIdStr = "0x"

		crcCheck = CRC(crcPolynomial = self.dsCrcPoly)

		for item in sensID:
			inByte = int(item, 16)
			crcCheck.addByte(inByte)

		for item in sensID[1:-2]:	# JUST the unique ID bit
			if len(item) == 1:
				item = "0"+item
			sensIdStr += item

		if crcCheck.getResult() is not 0:
			print "Invalid Address CRC!"
			return

		sensDat = body[9:18]

		crcCheck = CRC(crcPolynomial = self.dsCrcPoly)
		for item in sensDat:
			inByte = int(item, 16)
			crcCheck.addByte(inByte)
		if crcCheck.getResult() is not 0:
			print "Invalid Data CRC!"
			return



		temp   = (int(sensDat[1], 16) << 8 | int(sensDat[0], 16))*0.0625

		if sensIdStr in sensorDict:
			sensorNo = sensorDict[sensIdStr]
			monBuf.add_data([sensorNo, temp])

		print "Temp = %f, Sensor Serial = %s, sensPort = %d" % (temp, sensIdStr, sensorPort)

	def handleRfReport(self, inStr):
		if not ("|" in inStr and ":" in inStr):
			print "Bad RF Report!", inStr
			return

		header, body = inStr.split("|")
		body, crcVal = body.split(":")
		headerNum = int(header.split(":")[-1])
		body = body.split()



		if len(body) != headerNum:
			print "Invalid packet length!"
			return
		if crcVal != "1":
			print "Bad CRC!"
			return

		if body[0] == "1" or body[0] == "2" or body[0] == "3":
			self.parseDS18B20Data(body)

		else:
			print "Don't know sensor ID!", inStr

	def procRx(self):
		self.tmpStr += self.port.read(50)
		if "\r" in self.tmpStr:
			out, self.tmpStr = self.tmpStr.split("\r", 1)
			out = out.rstrip().lstrip()
			if out.startswith("RxRf"):
				self.handleRfReport(out)
			elif "ServerBarometer | " in out:
				self.procBaro(out)
			else:
				print "Bad Data Chunk: \"", out, "\""


	def getThermBaroValues(self):
		if self.tmpLog == None and self.presLog == None:
			print "TempBaro logging not working? Wat?"
			return None, None
		if len(self.tmpLog) == 0 or len(self.presLog) == 0:
			print "TempBaro doesn't have any data?"
			return None, None

		print "Processing", len(self.tmpLog), "temperature samples,", len(self.presLog), "pressure samples."
		avgTmpRet = sum(self.tmpLog)/float(len(self.tmpLog))
		avgPrsRet = sum(self.presLog)/float(len(self.presLog))
		self.tmpLog = []
		self.presLog = []
		return avgTmpRet, avgPrsRet


if __name__ == "__main__":
	print "Starting"

	try:
		apiKey = open("../emoncmsApiKey.conf", "r").read()
		print "Loaded APIKey as", apiKey
		serverIP = '10.1.1.39'
		testMode = False
	except IOError:
		print "No API Key file. Running in test-mode"
		apiKey = "wat"
		serverIP = '127.0.0.1'
		testMode = True


	monBuf = EmonFeeder.EmonFeeder(protocol = 'https://',
								   domain = serverIP,
								   testMode = testMode,
								   path = '/emoncms',
								   apikey = apiKey,
								   period = 10)

	print "Opening serial port"
	weatherInterface = WeatherLogger('COM11')


	print "Setup complete."

	while 1:
		weatherInterface.procRx()
		if monBuf.check_time():

			print "Data transmission interval complete: Ready to send"
			avgTmp, avgPrs = weatherInterface.getThermBaroValues()
			if avgTmp != None and avgPrs != None:
				monBuf.add_data(["1", avgTmp, avgPrs])

			monBuf.send_data()
		time.sleep(0.05)
