#!/usr/bin/python


import EmonFeeder
import time
from pyhacklet import hacklet

if __name__ == "__main__":
	print "Starting"



	monBuf = EmonFeeder.EmonFeeder(protocol = 'https://',
							  domain = '10.1.1.39',
							  path = '/emoncms',
							  apikey = "[YOUR KEY HERE]",
							  period = 15)

	hak = hacklet.Hacklet()

	while 1:
		s1, s2 = hak.getReadings()
		if s1["samples"] and s2["samples"]:
			print "Have data! Ready to send"
			modletVal1, modletVal2 = s1["samples"][-1], s2["samples"][-1]

			monBuf.add_data(["2", modletVal1, modletVal2])
			monBuf.send_data()
		time.sleep(1)
