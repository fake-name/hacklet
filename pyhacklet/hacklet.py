
import struct
import bitstring

class TxPkt():

	def getPacketStr(self):
		ret = self.header
		chk = 0
		for part in self.fields:
			for byte in part:
				chk ^= ord(byte)
				ret += byte


		ret += chr(chk)
		return ret


class BootRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating BootRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x04"
		self.payLen = "\x00"

		self.fields = [self.command, self.payLen]
		

class BootConfirmRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating BootConfirmRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x00"
		self.payLen = "\x00"

		self.fields = [self.command, self.payLen]
		
class UnlockRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating UnlockRequestPkt packet"

		self.header = "\x02"
		self.command = "\xA2\x36"
		self.payLen = "\x04"
		self.data = "\xFC\xFF\x90\x01"

		self.fields = [self.command, self.payLen, self.data]
		

class LockRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating LockRequestPkt packet"

		self.header = "\x02"
		self.command = "\xA2\x36"
		self.payLen = "\x04"
		self.data = "\xFC\xFF\x00\x01"

		self.fields = [self.command, self.payLen, self.data]
		

class UpdateTimeRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating UpdateTimeRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x22"
		self.payLen = "\x04"
		self.data = "Time crap goes here" 
		# uint32le :time, :initial_value => lambda { Time.now.to_i }
		raise ValueError("Packet type not working yet")

		self.fields = [self.command, self.payLen, self.data]
		
class HandshakeRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating HandshakeRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x03"
		self.payLen = "\x04"
		self.data = "NetworkID crap goes here" 
		# uint16 :network_id
		# TODO: What is this?
		# uint16 :data, :initial_value => 0x0500
		raise ValueError("Packet type not working yet")

		self.fields = [self.command, self.payLen, self.data]
		
class SamplesRequestPkt(TxPkt):
	def __init__(self, socketId):
		# print "Creating SamplesRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x24"
		self.payLen = "\x06"

		self.data = struct.pack("!HHH", 0xE771, socketId, 0x0A00)

		# uint16 :network_id
		# uint16 :channel_id # Socket ID - 0/1
		# TODO: What is this?
		# uint16 :data, :initial_value => 0x0A00   # Value doesn't seem to matter much

		self.fields = [self.command, self.payLen, self.data]
		
class ScheduleRequestPkt(TxPkt):
	def __init__(self):
		# print "Creating ScheduleRequestPkt packet"

		self.header = "\x02"
		self.command = "\x40\x23"
		self.payLen = "\x59"
		self.data = "Scheduling crap goes here" 
		# uint16 :network_id
		# uint16 :channel_id
		# TODO: What is this?
		# uint16 :data, :initial_value => 0x0A00
		raise ValueError("Packet type not working yet")

		self.fields = [self.command, self.payLen, self.data]
		


def hexify(inStr):
	return ":".join("{0:0>2X}".format(ord(c)) for c in inStr)


# This could probably be made a lot prettier through inheritance schenanigans. LAAAZZYYYY
# Plus, just doing conditional checks does work.
class RxPkt():

	packetLookups = \
	{ "\x40\x84" :{"len"          : 22,    		# BootResponse
					"decodeStr"   : "!"+"x"*12+"Q"+"x"*2,
					"data"        : None},

	  "\x40\x80" :{"len"          : 1,     		# BootConfirmResponse
	  				"decodeStr"   : None,
	  				"data"        : "\x10"},

	  "\xA0\x13" :{"len"          : 11,    		# BroadcastResponse
	  				"decodeStr"   : None,
	  				"data"        : None},

	  "\xA0\x58" :{"len"          : None,  		# Don't know
	  				"decodeStr"   : "overridden in constructor",
	  				"data"        : None},

	  "\xA0\xF9" :{"len"          : 1,     		# LockResponse
	  				"decodeStr"   : None,
	  				"data"        : "\x00"},

	  "\x40\x22" :{"len"          : 1,     		# UpdateTimeAckResponse
	  				"decodeStr"   : None,
	  				"data"        : "\x00"},

	  "\x40\xA2" :{"len"          : 3,     		# UpdateTimeResponse
	  				"decodeStr"   : None,
	  				"data"        : None},	# only partially specified. Needs more work

	  "\x40\x03" :{"len"          : 1,     		# HandshakeResponse
	  				"decodeStr"   : None,
	  				"data"        : "\x00"},

	  "\x40\x24" :{"len"          : 1,     		# AckResponse
	  				"decodeStr"   : None,
	  				"data"        : "\x00"},

	  "\x40\xA4" :{"len"          : None,  		# SamplesResponse
	  				"decodeStr"   : "overridden in constructor",
	  				"data"        : None},

	  "\x40\x23" :{"len"          : 1,     		# ScheduleResponse
	  				"decodeStr"   : None,
	  				"data"        : None}}


	#modletMac = "0x591a100000584f80"
	def processDataSamplePkt(self, dataIn):
		bs = bitstring.ConstBitStream(bytes=dataIn)
		network_id      = bs.read("uintbe:16")		# 2
		something1      = bs.read("uintbe:8")		# 2
		channel_id      = bs.read("uintbe:8")		# 2
		something2      = bs.read("uintbe:16")		# 2
		sampleTime      = bs.read("uintle:32")		# 4
		sampleCount     = bs.read("uintbe:8")		# 1
		availableCount  = bs.read("uintle:24")		# 3
		# Total header len = 14
		#print "Read Values = ", "network_id", network_id, 
		#print "something1",     something1, 
		#print "channel_id",     channel_id, 
		#print "something2",     something2, 
		#print "time",           sampleTime, 
		#print "sampleCount",    sampleCount, 
		#print "availableCount", availableCount

		samples = []
		for x in range(0, sampleCount):
			#print "Sample ", x
			samples.append(bs.read("uintle:16")/13.0)

		#print "Data len = ", (len(dataIn) - 14) / 2
		return {"channel" : channel_id, "samples" : samples, "time" : sampleTime, "nid" : network_id}

	def processDataUnknownPkt(self, dataIn):
		print "UNKNOWN PACKET?"

		print "Command = ", hexify(self.command)
		print "Data = ", hexify(dataIn)

		return None
	def __init__(self):

		self.header = "\x02"
		self.command = 0
		self.byteNo = 0
		self.payLen = 0
		self.data = ""
		self.checksum = 0

		self.packetLookups["\x40\xA4"]["decodeStr"] = self.processDataSamplePkt   # Haaaack
		self.packetLookups["\xA0\x58"]["decodeStr"] = self.processDataUnknownPkt   # Haaaack

	def checkCheckSum(self, checksum):
		fields = [self.command, chr(self.payLen), self.data]
		chk = 0
		for part in fields:
			for byte in part:
				chk ^= ord(byte)
		chk ^= ord(checksum)
		if chk:
			raise ValueError("INVALID CHECKSUM")

		self.checksum = checksum

	def processValidPacket(self):

		# Check against prefedined data values, if we have any
		if self.packetLookups[self.command]["data"]:
			if self.packetLookups[self.command]["data"] != self.data:
				raise ValueError("Packet data does not match! Expected", hexify(self.packetLookups[self.command]["data"]), "received", hexify(self.data))

		# Decode if decoder is specified
		ret = ""
		#print "Trying to decode",  hexify(self.command)
		lookup = self.packetLookups[self.command]["decodeStr"]
		if lookup:
			if callable(lookup):
				ret = lookup(self.data)
			else:
				ret = struct.unpack(self.packetLookups[self.command]["decodeStr"], self.data)
				print "Plug MAC:", hex(ret[0])

		#print "Received = ", hexify(self.command), hexify(chr(self.payLen)), hexify(self.data), hexify(self.checksum)
		return ret

	def check(self, wantVal, inVal):
		if wantVal != inVal:
			print "INVALID VALUE", hexify(wantVal), hexify(inVal), "at byte no", self.byteNo

	def checkLen(self):
		if self.command in self.packetLookups:
			if self.packetLookups[self.command]["len"]:
				if self.packetLookups[self.command]["len"] != self.payLen:
					raise ValueError("Bad Packet Length")
		return True

	def checkByte(self, byte):

		if self.byteNo == 0:				# Header byte
			self.check(byte, self.header)
			self.byteNo += 1
			return True, []

		if self.byteNo == 1:				# Command byte 1
			self.command = byte
			self.byteNo += 1
			return True, []

		if self.byteNo == 2:				# Command byte 2
			self.command += byte
			self.byteNo += 1
			if not self.command in self.packetLookups:
				raise ValueError("Invalid Packet Command", hexify(self.command))

			return True, []

		if self.byteNo == 3:				# data length byte
			self.payLen = ord(byte)
			self.byteNo += 1
			#print "Packet length = ", self.payLen,
			self.checkLen()
			return True, []

		if self.byteNo > 3 and self.byteNo <= 3+self.payLen:		# Data bytes
			self.data += byte
			self.byteNo += 1
			return True, []

		if self.byteNo >= 3+self.payLen:			# And the LRC checksum
			#print "On Checksum"
			self.checkCheckSum(byte)
			ret = self.processValidPacket()
			return False, ret



import ftdi1
import time

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
		#print "writing", hexify(inStr), "length of", len(inStr)
		ret = ftdi1.write_data(self.ftdic, inStr, len(inStr))
		#print "write ret = ", ret
		
	def read(self):
		rx = RxPkt()
		ret = ""
		remaining = 500

		#todo: TIMEOUTS
		start = time.time()
		while remaining:
			readBytes, dat = ftdi1.read_data(self.ftdic, 1)
			if readBytes:
				remaining, ret = rx.checkByte(dat)

			if time.time() > start+3:
				print "TIMED OUT!"
				break
				
		#if ret:
		#	print "ret", ret
		return ret

	def __del__(self):


		# close usb
		ret = ftdi1.usb_close(self.ftdic)
		if ret < 0:
			print('unable to close ftdi device: %d (%s)' % (ret, ftdi1.get_error_string(self.ftdic)))
		    

		print ('device closed')
		ftdi1.free(self.ftdic)


	def openConnection(self):
		self.write(BootRequestPkt().getPacketStr())
		self.read()
		self.write(BootConfirmRequestPkt().getPacketStr())
		self.read()
		self.write(LockRequestPkt().getPacketStr())
		self.read()

	def getReadings(self):
		socket1 = None
		socket2 = None
		
		self.write(SamplesRequestPkt(0).getPacketStr())
		while not socket1:
			socket1 = self.read()
		
		self.write(SamplesRequestPkt(1).getPacketStr())
		while not socket2:
			socket2 = self.read()

		return socket1, socket2