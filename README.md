
NetDIMM Tools is a modified Version of piforcetools by capane-us (https://github.com/capane-us/piforcetools)

NetDIMM Tools drives a Raspberry Pi with Adafruit LCD Plate and interfaces with debugmode's triforce tools to load a NetDIMM board with binaries for a Triforce, Naomi, or Chihiro arcade system.

New Features:
A config file is used for some parameters:
- path to bios for naomi1/2
- path to roms for each system
- ip adresses of used netdimm boards

Targets are scanned at startup - unavailable targets are purged
Some commands have been added
- Reset Target
- Restart System
- Shutdown System
