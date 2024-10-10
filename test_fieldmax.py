import sys

#path append is replaced by copying the module directly into this repository and importing it using 'from'
# sys.path.append(r"C:\Users\thomas\Documents\GitHub\Fieldmax\pyFieldMaxII-main\fieldmax")
# import fieldmax  # Now you can import the module

#importing pyFieldMaxII module
from pyFieldMaxII.fieldmax import fieldmax

#import visa
import pyvisa
from ThorlabsPM100 import ThorlabsPM100

FMII = fieldmax.FieldMax(r'C:\Program Files (x86)\Coherent\FieldMaxII PC\Drivers\Win10\FieldMax2Lib\x64\FieldMax2Lib.dll')
FMII.openDriver()
#print( FMII.get_SerialNumber() )


FMII.sync()

print(FMII.get_dataPoint())

FMII.closeDriver()



#https://pypi.org/project/ThorlabsPM100/
#https://github.com/clade/ThorlabsPM100/blob/master/ThorlabsPM100/ThorlabsPM100.py
rm = pyvisa.ResourceManager('@py')
#print(rm.list_resources())
inst = rm.open_resource('USB0::0x1313::0x8072::P2010300::0::INSTR')
power_meter = ThorlabsPM100(inst=inst)
inst.timeout = None

power_meter.configure.scalar.power()
power_meter.sense.correction.wavelength = 1035
print("Wavelength :", power_meter.sense.correction.wavelength)
print("Measurement type :", power_meter.getconfigure)
print("Current value    :", power_meter.read)

print(inst.query("*IDN?"))
print(rm)
print(inst)
