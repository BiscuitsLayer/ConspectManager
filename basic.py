import sys
import platform
import time

# Open a log file to write to
#
f = open('C:/Users/Vinog/Desktop/MIPT/ConspectManager/basic.log', 'a')

# Write date/time
#
f.write(f"{time.strftime('%x %X')}\n")

# Python info
#
f.write(f"Python EXE : {sys.executable}\n")
f.write(f"Architecture : {platform.architecture()[0]}\n")
f.write(f"\n")
f.close()