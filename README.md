Python rewrite of the Hacklet tool.
=======

An Open Source client for the Modlet (smart) outlet

This rewrite is intended to be more for use as a monitoring tool, so long-running connections are the interest, rather then power control (which I frankly don't care about at all. My servers are plugged into my modlet. They almost NEVER get turned off, and someone better fucking be there when it happens).

Functionality to push power-use numbers into emoncms will also likely be added. See https://gist.github.com/fake-name/8350183 for a working script that executes the current hacklet version using subprocesses (note: SLOWWWW on a raspberry pi).
