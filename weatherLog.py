#!/usr/bin/python

import EmonFeeder
import time

import serial
import traceback

class WeatherLogger():

	def __init__(self, portStr):
		self.port = serial.Serial(portStr, 115200, timeout=0)

		self.tmpStr = ""
		self.tmpLog = []
		self.presLog = []

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

	def procRx(self):
		self.tmpStr += self.port.read(50)
		if "\r" in self.tmpStr:
			out, self.tmpStr = self.tmpStr.split("\r", 1)
			out = out.rstrip().lstrip()
			if "AnemometerStation | " in out:
				self.procWind(out)
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
		avgTmp = sum(self.tmpLog)/float(len(self.tmpLog))
		avgPrs = sum(self.presLog)/float(len(self.presLog))
		self.tmpLog = []
		self.presLog = []
		return avgTmp, avgPrs


if __name__ == "__main__":
	print "Starting"


	apiKey = open("../emoncmsApiKey.conf", "r").read()
	print "Loaded APIKey as", apiKey

	monBuf = EmonFeeder.EmonFeeder(protocol = 'https://',
								   domain = '10.1.1.39',
								   path = '/emoncms',
								   apikey = apiKey,
								   period = 10)


	weatherInterface = WeatherLogger('/dev/ttyACM0')



	while 1:
		weatherInterface.procRx()
		if monBuf.check_time():

			print "Data transmission interval complete: Ready to send"
			avgTmp, avgPrs = weatherInterface.getThermBaroValues()
			if avgTmp != None and avgPrs != None:
				monBuf.add_data(["1", avgTmp, avgPrs])
			
			monBuf.send_data()
		time.sleep(0.05)
