Python rewrite of the Hacklet tool.
=======

An Open Source client for the Modlet (smart) outlet

This is a ground-up rewrite of the hacklet tool for use in long-running data-collection applications, rather then IFTTT triggered-action situations. It's also not written in the abomination that is ruby, and is considerably faster as well (at least juding by startup-to-first-data times on a raspberry pi)!

The main modlet interface is in the `pyhacklet` directory. The scripts in the repo root are actually related to getting the data into an emoncms instance. `EmonFeeder.py` is a class that handles shoving data into emoncms cleanly. 

`modLog.py` is a script that uses `pyhacklet` and `EmonFeeder.py` to poll the modlet at 1 Hz for new data (probably faster then is warranted, but eh), and insert the returned power data into my emoncms instance.

`weatherLog.py` is a unrelated script that loads weather data received over a serial interface into the same emoncms instance. It's only here because it used to be part of the script that also loads the modlet data.

---

This was written using the original [hacklet](https://github.com/mcolyer/hacklet) code as reference for the modlet API. @mcolyer did all the hard reverse-engineering, I just wish he hadn't used ruby. 

---

Anyways, this is very alpha-release at this point. I don't know how the modlet hardware will deal with extremely-long-running open serial connections, and I haven't had it running long enough to see where it starts to break (and fix those places). Previously, my modlet data-logging had involved reinitializing the serial port once per read, as that was a limitation of the way I had to call the original hacklet script (as a subprocess). 

Keeping the connection open, as well as the fact that the whole ruby interpreter doesn't need to be called for EVERY reading means this is **dramatically** lighter with regard to resource usage, a particularly important consideration when running this tool on a Raspberry Pi, as I am.
