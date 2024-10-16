# imports

import  time
import numpy as np
import pandas as pd
# import sys
# for FieldMax powermeter dll wrapper
from pyFieldMaxII.fieldmax import fieldmax
#import visa for device connection
# import pyvisa
# import pyvisa_py
# import usb
# import usb.core
# import usb.util
# import pathlib
# import os
import libximc.highlevel as ximc

#-------FieldMaxII connection--------------
path_to_fm2 = r'C:\Program Files (x86)\Coherent\FieldMaxII PC\Drivers\Win10\FieldMax2Lib\x64\FieldMax2Lib.dll'
fm2 = fieldmax.FieldMax(path_to_fm2)
fm2.openDriver()
print(fm2.get_SerialNumber())
fm2.sync()
print('FM2 Connected and initial reading: ', fm2.get_dataPoint())


# connecting rotor
# Devices search
devices = ximc.enumerate_devices(
    ximc.EnumerateFlags.ENUMERATE_NETWORK |
    ximc.EnumerateFlags.ENUMERATE_PROBE
)

if len(devices) == 0:
    print("The real devices were not found.")
else:
    # Print real devices list
    print("Found {} real device(s):".format(len(devices)))
    for device in devices:
        print("  {}".format(device))

# device_uri = "xi-emu:///{}".format(virtual_device_file_path)
device_uri = r"xi-com:\\.\COM5" #for usb in our case
# device_uri = r"xi-com:///dev/ttyACM29"
# device_uri = "xi-tcp://172.16.131.140:1820"
# device_uri = "xi-net://192.168.1.120/abcd"

# making a rotor object 
rotor = ximc.Axis(device_uri)
# To open the connection, you must manually call `open_device()` method

#--------------
#zeroing of motor

rotor.open_device()
print('current position', rotor.get_position())
print('moving rotor to reference zero', rotor.command_move(0,0))
rotor.close_device()

#globals for choosing the power meter type, 
N = 200 #measurement points at each step

# function for measuring at a certain power meter type, flag is for noting down which steps need to be measured with th100 again
# !!! this needs to be redone if A) the get_dataArray works
def measure(N = 10):
    #initialize measurements array
    measurements = np.zeros(N, dtype=float)
    n = 0 
    while n < N:
        measurements[n] = fm2.get_dataPoint()
        n += 1

    print(f'{N} datapoints measured on {fm2}')
        
    return measurements #np array floats length N


#external csv where all is written; for each Laser Intensity 1 csv file
export_data = pd.DataFrame(columns= [
    'rotor_step',
    'raw_data',
    'averaged',
    'stdev'
])

#Measurement process

steps = np.arange(100, 100000, 100) #defined rotor steps

# rotor.open_device()
for i, step in enumerate(steps):
    time.sleep(1)
    step  = int(step)
    rotor.command_move(step, 0)
    print('measuring, rotor moved to ', rotor.get_position())
    raw_data = measure(N=N)
    export_data.loc[i, 'rotor_step'] = step
    export_data.at[i, 'raw_data'] = raw_data
    export_data.loc[i, 'averaged'] = np.average(raw_data)
    export_data.loc[i, 'stdev'] = np.std(raw_data)
    print(f'average power at step {step} is {np.average(raw_data)} with stdev {np.std(raw_data)}')
    if input('continue? (leave black to yes, enter anythign to not)') == '':
        break
    


#exporting the csv with the naming acc. to laser intensity
laser_intensity = input('What is the laser setting: ')
export_data.to_csv(f'measurements/measurements_after_HWP_fm2/measured_rf{laser_intensity}.csv', index=False)

#close drivers
fm2.closeDriver()
rotor.close_device()