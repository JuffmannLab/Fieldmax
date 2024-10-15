# imports

import  time
import numpy as np
import pandas as pd
import sys
# for FieldMax powermeter dll wrapper
from pyFieldMaxII.fieldmax import fieldmax
#import visa for device connection
import pyvisa
import pyvisa_py
import usb
import usb.core
import usb.util
import pathlib
import os
import time
import libximc.highlevel as ximc
#import Thorlabs powermeter script wrapper
from ThorlabsPM100 import ThorlabsPM100
import time
#--------ThorlabsPM100 powermeter connection ---
#https://github.com/clade/ThorlabsPM100/blob/master/ThorlabsPM100/ThorlabsPM100.py

#select python backend and get connected devices on the PC (basically)
rm = pyvisa.ResourceManager('@py')
#choose the powermeter !!the adress changes when switching USB connections, identifiable if opened in DevicesManager - Properties - Details - Location Information (or somewhere there, also not 1 to 1 the same adress - have to select from rm.list_resources())
#print(rm.list_resources())
inst = rm.open_resource('USB0::4883::32882::P2010300::0::INSTR') 
th100 = ThorlabsPM100(inst=inst)
inst.timeout = None

th100.configure.scalar.power() #choose power measurements
th100.sense.correction.wavelength = 1035 #set wavelength
print("Wavelength :", th100.sense.correction.wavelength)
print("Measurement type :", th100.getconfigure)

for i in range(10):
    th100.read
print("TH100 connected and initial reading: ", th100.read)


#connecting rotor
# # Devices search
# devices = ximc.enumerate_devices(
#     ximc.EnumerateFlags.ENUMERATE_NETWORK |
#     ximc.EnumerateFlags.ENUMERATE_PROBE
# )

# if len(devices) == 0:
#     print("The real devices were not found.")
# else:
#     # Print real devices list
#     print("Found {} real device(s):".format(len(devices)))
#     for device in devices:
#         print("  {}".format(device))

# # device_uri = "xi-emu:///{}".format(virtual_device_file_path)
# device_uri = r"xi-com:\\.\COM5" #for usb in our case
# # device_uri = r"xi-com:///dev/ttyACM29"
# # device_uri = "xi-tcp://172.16.131.140:1820"
# # device_uri = "xi-net://192.168.1.120/abcd"

# # making a rotor object 
# rotor = ximc.Axis(device_uri)
# To open the connection, you must manually call `open_device()` method

#--------------
#zeroing


# rotor.open_device()
# print('current position', rotor.get_position())
# print('moving rotor to reference zero', rotor.command_move(0,0))
# rotor.close_device()

# #FieldmaxII Zeroing
# fm2.zeroing()
# print('fm2 zeroed and reading:', fm2.get_dataPoint())

#Thorlabs zeroing, Performs zero adjustment routine 
# th100.sense.correction.collect.zero.initiate()
# print('th100 zeroed, ', th100.sense.correction.collect.zero.state)
# zero_data = th100.sense.correction.collect.zero.state
# print('th100 zero magnitude', th100.sense.correction.collect.zero.magnitude)

#globals for choosing the power meter type, 
N = 1000 #measurement points at each step

# function for measuring at a certain power meter type, flag is for noting down which steps need to be measured with th100 again
# !!! this needs to be redone if A) the get_dataArray works, B) if we want to get N only after stabilization
def measure(N = 10):
    #initialize measurements array
    measurements = np.zeros(N, dtype=float)
    n = 0 
    while n < N:
        measurements[n] = th100.read
        n += 1

    print(f'{N} datapoints measured on {th100}')
        
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
    time.sleep(2)
    step  = int(step)
    # rotor.command_move(step, 0)
    # print('measuring, rotor moved to ', rotor.get_position())
    raw_data = measure(N=N)
    export_data.loc[i, 'rotor_step'] = step
    export_data.at[i, 'raw_data'] = raw_data
    export_data.loc[i, 'averaged'] = np.average(raw_data)
    export_data.loc[i, 'stdev'] = np.std(raw_data)
    if 'n' == 'n':
        break
    

#exporting the csv with the naming acc. to laser intensity
laser_intensity = input('What is the laser setting: ')
export_data.to_csv(f'measurements/measured_rf{laser_intensity}.csv', index=False)

#close drivers
# fm2.closeDriver()
# rotor.close_device()

#close th100? i think it auto closes once the object is trashed, but cant find the mention in docs