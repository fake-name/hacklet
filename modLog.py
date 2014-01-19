#!/usr/bin/python


import EmonFeeder
import time
from pyhacklet import hacklet

if __name__ == "__main__":
	print "Starting"



	monBuf = EmonFeeder.EmonFeeder(protocol = 'https://',
							  domain = '10.1.1.39',
							  path = '/emoncms',
							  apikey = "1c30034bd4ebd60f9c95a13decd0a3ce",
							  period = 15)



	hak = hacklet.Hacklet()

	# hacklet:
	# Found device 0x591a100000584f80 on network 0xe771
	# hacklet read -n 0x591a100000584f80 -s 1
	modletMac = "0x591a100000584f80"

	while 1:
		s1, s2 = hak.getReadings()
		if s1["samples"] and s2["samples"]:
			print "Have data! Ready to send"
			modletVal1, modletVal2 = s1["samples"][-1], s2["samples"][-1]

			monBuf.add_data(["2", modletVal1, modletVal2])
			monBuf.send_data()
		time.sleep(1)
