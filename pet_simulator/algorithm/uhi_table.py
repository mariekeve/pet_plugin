import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime as dt
from datetime import timedelta as timedelta
import numpy as np

print('Set the date YYYY,M,D seperated by commas')
year = 2013#(input("year:"))
month = 4#(input("month:"))
day = 1#(input("day:"))

print("Date is: " , year, month, day)

d0 = dt(int(year), int(month), int(day))
print(d0)

#-----------------------------------------------------------------------------------------------------------------------
#UHI table

data = {
  "6/17": [0.748, 0.667, 0.602, 0.525, 0.449, 0.281, 0.127, 0.063, 0.019, -0.015, -0.020, 0.000, 0.030, 0.065, 0.117, 0.205, 0.335, 0.532, 0.747, 0.906, 0.975, 1.000, 0.931, 0.849],
  "5/17": [0.782, 0.640, 0.573, 0.490, 0.355, 0.150, 0.078, 0.025, -0.013, -0.020, -0.001, 0.025, 0.056, 0.090, 0.165, 0.270, 0.413, 0.600, 0.803, 0.920, 0.978, 1.000, 0.925, 0.830],
  "5/18": [0.807, 0.704, 0.617, 0.533, 0.435, 0.227, 0.095, 0.032, -0.009, -0.020, -0.003, 0.020, 0.048, 0.080, 0.136, 0.215, 0.325, 0.485, 0.662, 0.849, 0.932, 0.979, 1.000, 0.918],
  "5/19": [0.910, 0.780, 0.675, 0.590, 0.490, 0.320, 0.120, 0.040, -0.005, -0.020, -0.004, 0.016, 0.042, 0.071, 0.111, 0.176, 0.270, 0.386, 0.546, 0.716, 0.877, 0.941, 0.981, 1.000],
  "4/19": [0.900, 0.757, 0.710, 0.543, 0.413, 0.150, 0.057, 0.000, -0.020, -0.005, 0.013, 0.037, 0.063, 0.090, 0.150, 0.222, 0.318, 0.450, 0.600, 0.762, 0.890, 0.950, 0.982, 1.000],
  "4/20": [1.000, 0.888, 0.728, 0.609, 0.490, 0.256, 0.079, 0.007, -0.020, 0.006, 0.010, 0.033, 0.056, 0.082, 0.128, 0.184, 0.270, 0.366, 0.506, 0.651, 0.803, 0.901, 0.958, 0.983],
  "3/20": [1.000, 0.866, 0.690, 0.560, 0.380, 0.107, 0.015, -0.020, -0.007, 0.007, 0.029, 0.050, 0.074, 0.108, 0.161, 0.228, 0.312, 0.424, 0.556, 0.695, 0.838, 0.911, 0.964, 0.984],
}

#load data into a DataFrame object:
df_UHI = pd.DataFrame(data)
print(df_UHI.at[df_UHI.index[2], '5/18'])

filename = 'c:/Users/marie/Documents/thesisprep/weekprogressies/literatuur/0-1678305133663/scripts reference flowchart/scripts reference flowchart/wageningen/knmi/Herwijnen2013.csv'
mydateparser = lambda x: pd.datetime.strptime(x, '%Y%m%d%H')
df_KNMI = pd.read_csv(filename, skipinitialspace=True, parse_dates=['YYYYMMDD'])#, date_parser=mydateparser)
df_KNMI['H'] = df_KNMI['H'] - 1
datetime_strings = df_KNMI['YYYYMMDD'].dt.strftime('%Y-%m-%d') + ' ' + df_KNMI['H'].astype(str) + ':00:00'
df_KNMI['YYYYMMDDHH'] = datetime_strings.apply(lambda x: dt.strptime(x, '%Y-%m-%d %H:%M:%S'))
print(df_KNMI)


#-----------------------------------------------------------------------------------------------------------------------
# check the period

d1 = dt(2013, 4, 1)
d2 = dt(2013, 4, 13)

d3 = dt(2013, 4, 14)
d4 = dt(2013, 4, 19)

d5 = dt(2013, 4, 20)
d6 = dt(2013, 5, 19)

d7 = dt(2013, 5, 20)
d8 = dt(2013, 5, 25)

d9 = dt(2013, 5, 26)
d10 = dt(2013, 7, 10)

d11 = dt(2013, 7, 11)
d12 = dt(2013, 7, 30)

d13 = dt(2013, 7, 31)
d14 = dt(2013, 8, 21)

d15 = dt(2013, 8, 22)
d16 = dt(2013, 8, 30)

d17 = dt(2013, 8, 31)
d18 = dt(2013, 9, 24)

d19 = dt(2013, 9, 25)
d20 = dt(2013, 9, 27)

d21 = dt(2013, 9, 28)
d22 = dt(2013, 9, 30)

diurnal = np.zeros(len(df_KNMI.index))


df_KNMI.set_index(['YYYYMMDDHH'], inplace=True)


for i in range(len((df_KNMI.index))):
  hour = int(df_KNMI.index.hour[i])
  if (d1 <= df_KNMI.index[i] <= d2):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '5/18']
  if (d3 <= df_KNMI.index[i] <= d4):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '5/19']
  if (d5 <= df_KNMI.index[i] <= d6):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '4/19']
  if (d7 <= df_KNMI.index[i] <= d8):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '4/20']
  if (d9 <= df_KNMI.index[i] <= d10):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '3/20']
  if (d11 <= df_KNMI.index[i] <= d12):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '4/20']
  if (d13 <= df_KNMI.index[i] <= d14):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '4/19']
  if (d15 <= df_KNMI.index[i] <= d16):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '5/19']
  if (d17 <= df_KNMI.index[i] <= d18):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '5/18']
  if (d19 <= df_KNMI.index[i] <= d20):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '5/17']
  if (d21 <= df_KNMI.index[i] <= d22):
    diurnal[i] = df_UHI.at[df_UHI.index[hour], '6/17']

df_KNMI['Diurnal'] = diurnal

print("Date is: " , year, month, day)
print(df_KNMI.Diurnal[df_KNMI.index==dt(year, month, day)])

#Extract Maximum daily values
T_Max = df_KNMI['T'].resample('D').max()
print(T_Max)

#Extract Minimum daily values
T_Min = df_KNMI['T'].resample('D').min()
print(T_Min)

#dataframe.plot()
#plt.show()
#
# plt.figure()
# plt.plot(dataframe.Q)
# plt.show()




