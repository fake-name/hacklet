
import time

def hexify(inStr):
	return ":".join("{0:0>2X}".format(ord(c)) for c in inStr)



if __name__ == "__main__":
	print "lol"

	
	hak = hacklet.Hacklet()

	while 1:
		s1, s2 = hak.getReadings()
		if s1["samples"] and s2["samples"]:
			print "HAZ DATAZ"
			print s1, s2
		time.sleep(1)