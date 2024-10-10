import  time
import numpy as np
import pandas as pd
# for FieldMax powermeter dll wrapper
from pyFieldMaxII.fieldmax import fieldmax
#import visa for device connection
import pyvisa
#import Thorlabs powermeter script wrapper
from ThorlabsPM100 import ThorlabsPM100

#----------------------------------
#connecting the powermeters

#-------FieldMaxII connection--------------
path_to_fm2 = r'C:\Program Files (x86)\Coherent\FieldMaxII PC\Drivers\Win10\FieldMax2Lib\x64\FieldMax2Lib.dll'
fm2 = fieldmax.FieldMax(path_to_fm2)
fm2.openDriver()
print(fm2.get_SerialNumber())
#sync??? what is this for
fm2.sync()
print('FM2 Connected and initial reading: ', fm2.get_dataPoint())

#--------ThorlabsPM100 powermeter connection ---
#https://github.com/clade/ThorlabsPM100/blob/master/ThorlabsPM100/ThorlabsPM100.py

#select python backend and get connected devices on the PC (basically)
rm = pyvisa.ResourceManager('@py')
#choose the powermeter !!the adress changes when switching USB connections, identifiable if opened in DevicesManager - Properties - Details - Location Information (or somewhere there, also not 1 to 1 the same adress - have to select from rm.list_resources())
#print(rm.list_resources())
inst = rm.open_resource('USB0::0x1313::0x8072::P2010300::0::INSTR') 
th100 = ThorlabsPM100(inst=inst)
inst.timeout = None

th100.configure.scalar.power() #choose power measurements
th100.sense.correction.wavelength = 1035 #set wavelength
print("Wavelength :", th100.sense.correction.wavelength)
print("Measurement type :", th100.getconfigure)
print("TH100 connected and initial reading: ", th100.read)

#--------------------------------
#Zeroing
#--------------------------------
#FieldmaxII Zeroing
fm2.zeroing()
print('fm2 zeroed and reading:', fm2.get_dataPoint())

#Thorlabs zeroing, Performs zero adjustment routine 
th100.sense.correction.collect.zero.initiate()
print('th100 zeroed, ', th100.sense.correction.collect.zero.state)
print('th100 zero magnitude', th100.sense.correction.collect.zero.magnitude)

#----------------
#spagetky

which_pwmeter = 'fm2'
power_meter_treshold = 300e-3 #Watts, the max range of TH100 and min working of FM2

def measure(which_pwmeter = which_pwmeter, N = 10, flag_for_th100 = False):
    power_meters = np.array([fm2, th100], dtype = object)
    if which_pwmeter == 'fm2':
        pw_meter = power_meters[0]
        pw_meter_type = 0
    else:
        pw_meter = power_meters[1]
        pw_meter_type = 1
    
    #set number of measurements
    measurements = np.zeros(N, dtype=float)
    n = 0 
    while n <= N:
        if pw_meter_type == 0: 
            measurements[n] = pw_meter.read
        elif pw_meter_type == 1:
            measurements[n] = pw_meter.getDataPoint()
    print(f'{N} datapoints measured on {which_pwmeter}')

    #check which steps should be measured again at higher precision, with the TH100
    here_should_be_TH100 = False
    if flag_for_th100:
        if measurements[-1] < power_meter_treshold:
            here_should_be_TH100 = True
            print(f'this step should be measured with the TH100 {measurements[-1]}')
            return (flag_for_th100, measurements)
        
    return measurements #np array floats length N



#spagetky
which_pwmeter = 'fm2'
N = 10 #measurement points at each step

#external csv where all is written; for each Laser Intensity 1 csv file
export_data = pd.DataFrame(columns= [
    'rotor_step',
    'raw_data',
    'averaged',
    'flag_for_th100'
])
laser_intensity = input('What is the laser setting: ')

#here measurement process

steps = np.array() #rotor steps

for i, step in enumerate(steps):
    #!!! rotor.move(step)

    flag, raw_data = measure(which_pwmeter=which_pwmeter, N=, flag_for_th100=True)
    export_data.loc[i, 'step'] = step
    export_data.loc[i, 'raw_data'] = raw_data
    export_data.loc[i, 'averaged'] = np.average(raw_data)
    export_data.loc[i, 'flag_for_th100'] = flag

#exporting the csv with the naming acc. to laser intensity
export_data.to_csv(f'measured_{laser_intensity}.csv', index=False)



#close drivers
fm2.closeDriver()
#close th100? i think it auto closes once the object is trashed, but cant find the mention in docs