import pathlib
import os
import time
import libximc.highlevel as ximc

virtual_device_filename = "virtual_motor_controller_1.bin"
virtual_device_file_path = os.path.join(
    pathlib.Path().cwd(),
    virtual_device_filename
)

# Devices search
devices = ximc.enumerate_devices(
    ximc.EnumerateFlags.ENUMERATE_NETWORK |
    ximc.EnumerateFlags.ENUMERATE_PROBE
)

if len(devices) == 0:
    print("The real devices were not found. A virtual device will be used.")
else:
    # Print real devices list
    print("Found {} real device(s):".format(len(devices)))
    for device in devices:
        print("  {}".format(device))

device_uri = "xi-emu:///{}".format(virtual_device_file_path)

# the COM should be for usb on windows

# device_uri = r"xi-com:\\.\COM29" 
# device_uri = r"xi-com:///dev/ttyACM29"
# device_uri = "xi-tcp://172.16.131.140:1820"
# device_uri = "xi-net://192.168.1.120/abcd"

axis = ximc.Axis(device_uri)
# To open the connection, you must manually call `open_device()` method
axis.open_device()

# `close_device()` is optional. It's called automatically by the garbage
# collector
axis.close_device()

axis.open_device()

# ==== Set current position as zero ====
axis.command_zero()

# Object instances should be passed by reference
position = axis.get_position()
print("Initial position:", position.Position)


# ==== Move to the first absolute position (X = 100) ====
next_position = 100
print("Move to position:", next_position)
axis.command_move(next_position, 0)

print("Moving...")
axis.command_wait_for_stop(100)

position = axis.get_position()
print("Current position:", position.Position)


# ==== Move to the second absolute position (X = 50) ====
next_position = 50
print("Move to position:", next_position)
axis.command_move(next_position, 0)

print("Moving...")
axis.command_wait_for_stop(100)

position = axis.get_position()
print("Current position:", position.Position)


# ==== Perform a relative shift by 100 ====
relative_shift = 100
print("Perform a relative shift by", relative_shift)
print("So we are going to", position.Position, "+", relative_shift,
      " =", position.Position + relative_shift)
axis.command_movr(relative_shift, 0)

print("Moving...")
axis.command_wait_for_stop(100)

position = axis.get_position()
print("Current position:", position.Position)


# ==== Perform a relative shift by -150 ====
relative_shift = -150
print("Perform a relative shift by", relative_shift)
print("So we are going to", position.Position, "+ (", relative_shift,
      ") =", position.Position + relative_shift)
axis.command_movr(relative_shift, 0)

print("Moving...")
axis.command_wait_for_stop(100)

position = axis.get_position()
print("Current position:", position.Position)

axis.close_device()
print("Done")