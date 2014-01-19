#!/usr/bin/python

import EmonFeeder
import time

import serial


class ThermBaroLogger():

	def __init__(self, portStr):
		self.port = serial.Serial(portStr, 115200, timeout=0)

		self.tmpStr = ""
		self.tmpLog = []
		self.presLog = []

	def procRx(self):
		self.tmpStr += self.port.read(50)
		if "\r" in self.tmpStr:
			out, self.tmpStr = self.tmpStr.split("\r")
			out = out.split()
			temp = None
			pres = None
			for item in out:
				try:
					key, val = item.split(":")
					#print key, float(val)

					if key == "Temperature":
						temp = float(val)
					if key == "Pressure": 
						pres = float(val)
				except ValueError:
					print "Started part-way through a packet"

			print "Pres:", temp, "Pres:", pres
			if pres < 90000.0:
				print "BAD PRESSURE VALUE. Ignoring readings!"
				return
			if not pres or not temp:
				print "BAD READING?. Ignoring readings!"
				return
			
			self.tmpLog.append(temp)
			self.presLog.append(pres)

	def getValues(self):
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
	print "Loaded APIKey as ", apiKey

	monBuf = EmonFeeder.EmonFeeder(protocol = 'https://',
								   domain = '10.1.1.39',
								   path = '/emoncms',
								   apikey = apiKey,
								   period = 10)


	thermBaro = ThermBaroLogger('/dev/ttyUSB0')



	while 1:
		thermBaro.procRx()
		if monBuf.check_time():

			print "Ready to send"
			avgTmp, avgPrs = thermBaro.getValues()
			if avgTmp != None and avgPrs != None:
				monBuf.add_data(["1", avgTmp, avgPrs])
			
			monBuf.send_data()
		time.sleep(0.05)
