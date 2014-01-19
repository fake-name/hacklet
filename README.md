Python rewrite of the Hacklet tool.
=======

An Open Source client for the Modlet (smart) outlet

This is a ground-up rewrite of the hacklet tool for use in long-running data-collection applications, rather then IFTTT triggered-action situations. It's also not written in the abomination that is ruby, and is considerably faster as well (at least juding by startup-first-data times on a raspberry pi)!

The main modlet interface is in the `pyhacklet` directory. The scripts in the repo root are actually related to getting the data into an emoncms instance. `EmonFeeder.py` is a class that handles shoving data into emoncms cleanly. 

`modLog.py` is a script that uses `pyhacklet` and `EmonFeeder.py` to poll the modlet at 1 Hz for new data (probably faster then is warranted, but eh), and insert the returned power data into my emoncms instance.

`weatherLog.py` is a unrelated script that loads weather data received over a serial interface into the same emoncms instance. It's only here because it used to be part of the script that also loads the modlet data.

---

This was written using the original [hacklet](https://github.com/mcolyer/hacklet) code as reference for the modlet API. @mcolyer did all the hard reverse-engineering, I just wish he hadn't used ruby. 
