NetDIMM Tools

NetDIMM Tools is a modified Version of piforcetools by capane-us (https://github.com/capane-us/piforcetools)

NetDIMM Tools drives a Raspberry Pi with Adafruit LCD Plate and interfaces with debugmode's triforce tools to load a NetDIMM board with binaries for a Triforce, Naomi, or Chihiro arcade system.

New Features:
- Parameters stored in config file
- Path to bios for "Naomi 1/2"
- Path to roms for each system
- IP adresses of used netdimm boards

New Commands:
- Reset Target
- Restart Program
- Restart System
- Shutdown System

Commands:
- Ping Target-Test if selected NetDIMM is reachable
- Reset Target-Works on some Games, sometimes only in "Service Menu"
- Select Target-Select between all available targets from target list
- Restart Program-Restart NetDIMMTools
- Restart System-Restart "Raspberry Pi"
- Shutdown System-Shutdown "Raspberry Pi"

Usage:
Press <Cursor left><Cursor right> to switch between Game-Mode and Command-Mode.
(If no roms found, Game-Mode is not available)
(Ping/Reset/Select Target are not available if not targets found)
