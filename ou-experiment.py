import matplotlib.pyplot as plt
import pandas as pd
import json
import numpy as np
from haralyzer import HarParser, HarPage

datafile = 'exp_data.har'

wire_length = 61.0
wire_diameter = 140e-6
wire_area = np.pi*np.power((wire_diameter/2),2)
base_tempC = 30
base_tempK = base_tempC + 273.15
p0 = 1.631743e-8

#Create empty dataframe to store data
df = pd.DataFrame(columns=['Cycle','TemperatureC','TemperatureK','Resistance','Mode','deltaT','Resistivity'])

with open(datafile,'r') as f:
    har_page = HarPage('page_4', har_data=json.loads(f.read()))

error_count = 0
for idx, entry in enumerate(har_page.entries):
    try:
        data = json.loads(entry.response.text)
        resistance = data['ok']['sensor'][0]['value']
        temp = data['ok']['sensor'][1]['value']
        mode = data['ok']['sensor'][2]['value']
        cycle = data['ok']['sensor'][3]['value']
        df = df.append({'Cycle': cycle, 'TemperatureC': temp, "Resistance": resistance, "Mode": mode}, ignore_index=True)
    except KeyError:
        #Invalid check byte error (incomplete request most likely)
        error_count += 1
        continue
    except TypeError:
        #Cookie update request, just ignore it
        continue
print('Computed {} entries sucessfully, found {} errors.\n'.format(len(df.index),error_count))

#Convert string to numeric
df['Cycle'] = pd.to_numeric(df['Cycle'], errors='coerce')
df['TemperatureC'] = pd.to_numeric(df['TemperatureC'], errors='coerce')
df['Resistance'] = pd.to_numeric(df['Resistance'], errors='coerce')

#Calculate deltaT in Kelvin
df['TemperatureK'] = df['TemperatureC']+273.15
df['deltaT'] = df['TemperatureK']-base_tempK
df['Resistivity'] = df['Resistance']*(wire_area/wire_length)

#Plot data
df.plot(kind='scatter',y='Resistivity',x='deltaT', color='blue', alpha=0.5, figsize=(10, 7))

#Linear regression
fit = np.polyfit(df['deltaT'],df['Resistivity'],1)
print('p0: {}'.format(p0))
print('Slope: {}'.format(fit[0]))
print('Interception: {}'.format(fit[1]))
print('Alpha: {}'.format(fit[0]/p0))
#Plot fitted line
plt.plot(df['deltaT'], fit[0] * df['deltaT'] + fit[1], color='darkblue', linewidth=2)
plt.text(10, 1.64e-8, 'y = {:.3e}*x + {:.3e}'.format(fit[0], fit[1])+'\n'+'\u03B1= {:.3e} K\u207B\u00B9'.format(fit[0]/p0), color='darkblue', size=12)

# legend, title and labels.
plt.legend(labels=['Regression Line', 'Resistivity'])
plt.title('Cooper wire resistivity variation due temperature')
plt.xlabel(r'$\Delta$T [K]')
plt.ylabel(r'Resistivity [$\Omega$m]');

plt.show()
