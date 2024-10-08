import sys
sys.path.append(r"C:\Users\thomas\Documents\GitHub\Fieldmax\pyFieldMaxII-main\fieldmax")

import fieldmax  # Now you can import the module


FMII = fieldmax.FieldMax(r'C:\Program Files (x86)\Coherent\FieldMaxII PC\Drivers\Win10\FieldMax2Lib\x64\FieldMax2Lib.dll')
FMII.openDriver()
print( FMII.get_SerialNumber() )
FMII.closeDriver()