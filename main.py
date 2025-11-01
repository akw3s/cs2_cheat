import pymem
from pymem.memory import read_longlong, write_int
import pymem.process

pm = pymem.Pymem("cs2.exe") # Attach to the CS2 process

client = pymem.process.module_from_name(pm.process_handle, "client.dll") # Get the client.dll module
print("Base address:", hex(client.lpBaseOfDll)) # Print the base address of client.dll
print("Size of module:", hex(client.SizeOfImage)) # Print the size of client.dll

dwLocalPlayerController = pm.read_longlong(client.lpBaseOfDll + 0x1E16870) # Read the local player controller address
dwLocalPlayerPawn = pm.read_longlong(client.lpBaseOfDll + 0x1BE7DA0) # Read the local player pawn address

pm.write_int(dwLocalPlayerController +0x77C,120) # FOV
pm.write_float(dwLocalPlayerPawn +0x160C,150.0) # Flashbang duration
