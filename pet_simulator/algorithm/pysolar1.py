# Importing packages

import pvlib
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import numpy as np

# ----------------------------------------------------------
# Loading in total knmi file
df_tot = pd.read_csv("D:/project/run10/Rotterdam_28juni_2023_knmi.csv", parse_dates=['YYYYMMDD'])
# substracting the last line
df_KNMI = df_tot[df_tot.HH < 24]
print(df_KNMI)

# ----------------------------------------------------------
# Setting date with hour values
date_time = []
solar_elevation = np.zeros(len(df_KNMI.index))
# calculating the solar altitude and the diffuse irradiation
# Location coordinates for Amsterdam (latitude, longitude)


for i in range(len(df_KNMI.index)):
    date_time.append(
        dt(df_KNMI['YYYYMMDD'].iloc[i].year, df_KNMI['YYYYMMDD'].iloc[i].month, df_KNMI['YYYYMMDD'].iloc[i].day,
           df_KNMI['HH'].iloc[i], 0, 0))

latitude = 52.3667
longitude = 4.8945

solar_position = pvlib.solarposition.get_solarposition(date_time, latitude, longitude)

# Extract solar elevation angle
solar_elevation = solar_position['elevation'].values

# ----------------------------------------------------------
# Calculating the average Watt per square meter from the Q
Qs_av = np.zeros(len(df_KNMI.index))

for i in range(len(df_KNMI.index) - 1):
    Qs_av[i] = 10000 / 3600 * ((df_KNMI['    Q'].iloc[i + 1] - df_KNMI['    Q'].iloc[i]) / 2 + df_KNMI['    Q'].iloc[i])

# Calculating atmospheric transmissivity (tau_a)
tau_a = Qs_av / (1367.0 * np.sin(solar_elevation * np.pi / 180))

# Calculating the diffuse irradiation
Qd = np.zeros(len(df_KNMI.index))

for i in range(len(df_KNMI.index)):
    if tau_a[i] < 0.3:
        Qd[i] = Qs_av[i]
    elif tau_a[i] > 0.7:
        Qd[i] = 0.2 * Qs_av[i]
    else:
        Qd[i] = (1.6 - 2 * tau_a[i]) * Qs_av[i]

df_KNMI['Qdif'] = Qd


# --------------------------------------------------------
# calulating the wind, WE and wind direction
def wind_direction(dd, FH):
    if FH >= 1.5:
        wind = True
    else:
        wind = False
    # wind = FH >= 1.5
    if dd < 45 or dd > 315:
        WE = False
        winddir = 'N'
    elif dd < 135:
        WE = True
        winddir = 'E'
    elif dd < 225:
        WE = False
        winddir = 'S'
    elif dd < 315:
        WE = True
        winddir = 'W'
    else:
        winddir = 'C'
    return wind, WE, winddir


# addind the wind, WE and wind direction into pandas series through lists
windlist = []
WElist = []
windirlist = []

for i in range(len(df_KNMI.index)):
    wind, WE, winddir = wind_direction(df_KNMI['   DD'].iloc[i], df_KNMI['   FH'].iloc[i] / 10)
    windlist.append(wind)
    WElist.append(WE)
    windirlist.append(winddir)

df_KNMI['wind'] = windlist
df_KNMI['WE'] = WElist
df_KNMI['winddir'] = windirlist

# --------------------------------------------------------
# Adding the station names
df_KNMI['station'] = ['Rotterdam'] * len(df_KNMI.index)
# drop unnecessary columns like STN and U
df_KNMI = df_KNMI.drop(columns=['STN'])
# converting the wind and temperature columns
df_KNMI['   FF'] = df_KNMI['   FF'] / 10
df_KNMI['    T'] = df_KNMI['    T'] / 10
# --------------------------------------------------------
# Diurnal calculation
df_UHI = pd.read_csv('D:/project/run4/data/UHI_factors.csv')


def day_night(dates_KNMI, hour_KNMI):
    dateslist = [dt(year=dates_KNMI.year, month=4, day=1), dt(year=dates_KNMI.year, month=4, day=13),
                 dt(year=dates_KNMI.year, month=4, day=20), dt(year=dates_KNMI.year, month=5, day=20),
                 dt(year=dates_KNMI.year, month=5, day=26), dt(year=dates_KNMI.year, month=7, day=11),
                 dt(year=dates_KNMI.year, month=7, day=31), dt(year=dates_KNMI.year, month=8, day=22),
                 dt(year=dates_KNMI.year, month=8, day=31), dt(year=dates_KNMI.year, month=9, day=25),
                 dt(year=dates_KNMI.year, month=9, day=28), dt(year=dates_KNMI.year, month=9, day=30)]
    UHIlist = ['5/18', '5/19', '4/19', '4/20', '3/20', '4/20', '4/19', '5/19', '5/18', '5/17', '6/17']
    for i in range(len(dateslist) - 1):
        if dates_KNMI >= dateslist[i] and dates_KNMI < dateslist[i + 1]:
            diurnal = df_UHI[UHIlist[i]][hour_KNMI]
            sunrise, sunset = UHIlist[i].split('/')
            print(sunrise, sunset)
            if hour_KNMI >= int(sunrise) and hour_KNMI <= int(sunset):
                daynight = 'day'
            break
        else:
            daynight = 'night'
            diurnal = 1

    return daynight, diurnal


# addind the wind, WE and wind direction into pandas series through lists
daynightlist = []
diurnallist = []

for i in range(len(df_KNMI.index)):
    daynight, diurnal = day_night(df_KNMI['YYYYMMDD'].iloc[i], df_KNMI['HH'].iloc[i])
    daynightlist.append(daynight)
    diurnallist.append(diurnal)

df_KNMI['daynight'] = daynightlist
df_KNMI['diurnal'] = diurnallist


# --------------------------------------------------------

def min_max(df_KNMI, date_time):
    # date = date_time[0]

    list_temperature_inperiod = []
    list_wind_inperiod = []
    list_max_temp = []
    list_min_temp = []
    list_av_wind = []

    for j in range(0, len(df_KNMI.index), 24):
        date = date_time[j]
        print(f'date {date}')

        av_wind_cum = 0
        temperature_inperiod = []
        wind_inperiod = []
        for i in range(len(df_KNMI.index)):

            # Calculate period start
            period_start = dt(year=date.year, month=date.month, day=date.day, hour=9)

            # Calculate period end
            period_end = date + timedelta(days=1)
            period_end = period_end.replace(hour=8)

            if date_time[i] >= period_start and date_time[i] <= period_end:
                temperature_inperiod.append(df_KNMI['    T'].iloc[i])
                wind_inperiod.append(df_KNMI['   FF'].iloc[i])
                av_wind_cum += df_KNMI['   FF'].iloc[i]
                #   print(date, wind_inperiod)

        max_temp = np.max(np.array([temperature_inperiod]))
        min_temp = np.min(np.array([temperature_inperiod]))
        av_wind = av_wind_cum / len(wind_inperiod)

        list_max_temp.append(max_temp)
        list_min_temp.append(min_temp)
        list_av_wind.append(av_wind)
    list_temperature_inperiod.append(temperature_inperiod)
    list_wind_inperiod.append(wind_inperiod)
    # print('length', list_wind_inperiod)
    return list_max_temp, list_min_temp, list_av_wind


list_max_temp, list_min_temp, list_av_wind = min_max(df_KNMI, date_time)

for i, max_temp in enumerate(list_max_temp):
    # Filter timestamps for the current day
    mask = (df_KNMI['YYYYMMDD'].dt.date == df_KNMI.loc[i * 24, 'YYYYMMDD'].date())
    # Assign the daily maximum temperature to all hourly timestamps for the current day
    df_KNMI.loc[mask, 'Tmax'] = max_temp

for i, min_temp in enumerate(list_min_temp):
    # Filter timestamps for the current day
    mask = (df_KNMI['YYYYMMDD'].dt.date == df_KNMI.loc[i * 24, 'YYYYMMDD'].date())
    # Assign the daily maximum temperature to all hourly timestamps for the current day
    df_KNMI.loc[mask, 'Tmin'] = min_temp

for i, av_wind in enumerate(list_av_wind):
    # Filter timestamps for the current day
    mask = (df_KNMI['YYYYMMDD'].dt.date == df_KNMI.loc[i * 24, 'YYYYMMDD'].date())
    # Assign the daily maximum temperature to all hourly timestamps for the current day
    df_KNMI.loc[mask, 'FFavg'] = av_wind
# --------------------------------------------------------
# Writing the csv away
df_KNMI.to_csv(f'D:/Qd_results2.csv')
