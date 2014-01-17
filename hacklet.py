
import ftdi1

def hexify(inStr):
	return ":".join("{0:0>2X}".format(ord(c)) for c in inStr)

import hackletPackets as pkts

class Hacklet():

	def __init__(self):
		self.ftdic = ftdi1.new()
		print "usb_open ret = ", ftdi1.usb_open(self.ftdic, 0x0403, 0x8c81)
		print "set_bitmode ret = ", ftdi1.set_bitmode(self.ftdic, 0x00, ftdi1.BITMODE_RESET)		# Reset port to normal operation
		print "set_baudrate ret = ", ftdi1.set_baudrate(self.ftdic, 115200)		# 115200 baud
		print "setflowctrl ret = ", ftdi1.setflowctrl(self.ftdic, ftdi1.SIO_DISABLE_FLOW_CTRL)
		print "setdtr ret = ", ftdi1.setdtr(self.ftdic, 1)
		print "setrts ret = ", ftdi1.setrts(self.ftdic, 1)

	def write(self, inStr):
		print "writing", hexify(inStr), "length of", len(inStr)
		print "write ret = ", ftdi1.write_data(self.ftdic, inStr, len(inStr))
		
	def read(self):
		rx = pkts.RxPkt()
		ret = ""
		remaining = 500
		while remaining:
			readBytes, dat = ftdi1.read_data(self.ftdic, 1)
			if readBytes:
				remaining = rx.checkByte(dat)

		return ret

	def __del__(self):


		# close usb
		ret = ftdi1.usb_close(self.ftdic)
		if ret < 0:
			print('unable to close ftdi device: %d (%s)' % (ret, ftdi1.get_error_string(self.ftdic)))
		    

		print ('device closed')
		ftdi1.free(self.ftdic)


def lookN(inStr):
	for func in dir(ftdi1):
		if inStr in func:
			print func


if __name__ == "__main__":
	print "lol"

	
	hak = Hacklet()
	hak.write(pkts.BootRequestPkt().getPacketStr())
	hak.read()
	hak.write(pkts.BootConfirmRequestPkt().getPacketStr())
	hak.read()
	hak.write(pkts.LockRequestPkt().getPacketStr())
	hak.read()
	hak.write(pkts.SamplesRequestPkt(0).getPacketStr())
	hak.read()
	hak.read()