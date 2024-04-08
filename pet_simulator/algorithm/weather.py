# Importing packages
from datetime import datetime as dt
import pvlib
import pandas as pd
import numpy as np
import os
import math as mt
import csv

# ----------------------------------------------------------



def writeknmicsv(basedirectory, subdirectory, filename, filenametmintmax):

    # Loading in total knmi file
    df_tot = pd.read_csv(f'{basedirectory}\\{subdirectory}\\{filename}', parse_dates=['YYYYMMDD'])
    print(df_tot)

    # substracting the last line
    df_KNMI = df_tot[df_tot.H < 24]

    print(df_KNMI)
    df_KNMI.loc[:,'FF'] = df_KNMI.loc[:,'FF'] * 0.1
    df_KNMI.loc[:, 'T'] = df_KNMI.loc[:, 'T'] * 0.1
    # ----------------------------------------------------------

    # Setting date with hour values
    date_time = []

    for i in range(len(df_KNMI.index)):
        date_time.append(
            dt(df_KNMI['YYYYMMDD'].iloc[i].year, df_KNMI['YYYYMMDD'].iloc[i].month, df_KNMI['YYYYMMDD'].iloc[i].day,
               df_KNMI['H'].iloc[i], 0, 0))

    df_tmintmax = pd.read_csv(f'{basedirectory}\\{subdirectory}\\{filenametmintmax}', parse_dates=['YYYYMMDD'])

    Tmin = df_tmintmax.loc[:, 'T'].min()
    df_KNMI.loc[:, 'Tmin'] = np.ones(len(df_KNMI.index)) * Tmin * 0.1

    Tmax = df_tmintmax.loc[:, 'T'].max()
    df_KNMI.loc[:, 'Tmax'] = np.ones(len(df_KNMI.index)) * Tmax * 0.1

    # ----------------------------------------------------------
    # calculating the solar altitude and the diffuse irradiation
    # Location coordinates for Amsterdam (latitude, longitude)
    latitude = 52.3667
    longitude = 4.8945

    solar_position = pvlib.solarposition.get_solarposition(date_time, latitude, longitude)

    # Extract solar elevation angle
    solar_elevation = solar_position['elevation'].values

    df_KNMI.loc[:, 'Qnew'] = df_KNMI.loc[:, 'Q'] / 3600 * 10000

    # Calculating atmospheric transmissivity (tau_a)
    print(df_KNMI.columns)
    tau_a = df_KNMI.Qnew.values / (1367.0 * np.sin(solar_elevation))

    # Calculating the diffuse irradiation
    Qd = np.zeros(len(df_KNMI.index))

    for i in range(len(df_KNMI.index)):
        if tau_a[i] < 0.3:
            Qd[i] = df_KNMI['Qnew'].iloc[i]
        elif tau_a[i] > 0.7:
            Qd[i] = 0.2 * df_KNMI['Qnew'].iloc[i]
        else:
            Qd[i] = df_KNMI['Qnew'].iloc[i] * (1.6 - 2 * tau_a[i])


    df_KNMI.loc[:, 'Qdif'] = Qd
    df_KNMI.loc[:, 'sunalt'] = solar_elevation


    # --------------------------------------------------------
    # calulating the wind, WE and wind direction
    def wind_direction(dd, FF):
        if FF >= 1.5:
            wind = True
        else:
            wind = False
        # wind = FF >= 1.5
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
        wind, WE, winddir = wind_direction(df_KNMI['DD'].iloc[i], df_KNMI['FF'].iloc[i])
        windlist.append(wind)
        WElist.append(WE)
        windirlist.append(winddir)

    df_KNMI.loc[:, 'wind'] = windlist
    df_KNMI.loc[:, 'WE'] = WElist
    df_KNMI.loc[:, 'winddir'] = windirlist

    # --------------------------------------------------------

    # Diurnal calculation
    df_UHI = pd.read_csv(f'{basedirectory}\\{subdirectory}\\UHI_factors.csv')
    # check the period

    #date = df_KNMI.loc[0,'YYYYMMDD']

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

    for i in range(len(windlist)):
        daynight, diurnal = day_night(df_KNMI.loc[i, 'YYYYMMDD'], df_KNMI.loc[i, 'H'])
        daynightlist.append(daynight)
        diurnallist.append(diurnal)

    df_KNMI['daynight'] = daynightlist
    df_KNMI['diurnal'] = diurnallist

    df_KNMI.loc[:, 'ymax'] = np.ones(len(df_KNMI.index)) * 437988
    df_KNMI.loc[:,'xmax'] =np.ones(len(df_KNMI.index)) * 91061
    df_KNMI.loc[:,'ymin'] = np.ones(len(df_KNMI.index)) * 435988
    df_KNMI.loc[:,'xmin'] = np.ones(len(df_KNMI.index)) * 89061

    # Adding the station names
    df_KNMI.loc[:, 'station'] = ['Rotterdam'] * len(df_KNMI.index)

    df_KNMI.loc[:, 'directory_in'] = [f'{basedirectory}\\{subdirectory}'] * len(df_KNMI.index)
    stringlist = []
    for i, h in enumerate(df_KNMI.loc[:, 'H']):
        stringlist.append('sim100-' + str(h))
        df_KNMI.loc[i, 'directory_out'] = [f'{basedirectory}\\{stringlist[i]}\\']
        df_KNMI.loc[i, 'directory_label'] = f'{stringlist[i]}'

    print(stringlist)
    # df_KNMI.loc[:, 'directory_out'] = [f'{basedirectory}\\{stringlist}\\']
    #df_KNMI.loc[:, 'directory_label'] = f'{stringlist}'

    # drop unnecessary columns like STN and U
    df_KNMI = df_KNMI.drop(columns=['STN'])
    # Writing the csv away
    df_KNMI.to_csv(f'{basedirectory}\\{subdirectory}\\knmi_results.csv')




def writesetup(basedirectory, subdirectory, filename):

    df_KNMI = pd.read_csv(f'{basedirectory}\\{subdirectory}\\{filename}')
    print(df_KNMI)
    df_setup = pd.DataFrame(data=df_KNMI.loc[:, 'directory_in'])

    df_setup.loc[:, 'directory_out'] = df_KNMI.loc[:, 'directory_out']

    df_setup.loc[:, 'label'] = df_KNMI.loc[:, 'directory_label']

    df_setup.loc[:, 'station'] = df_KNMI.loc[:, 'station']

    df_setup.loc[:, 'ymax'] = df_KNMI.loc[:, 'ymax']
    df_setup.loc[:, 'xmax'] = df_KNMI.loc[:, 'xmax']
    df_setup.loc[:, 'ymin'] = df_KNMI.loc[:, 'ymin']
    df_setup.loc[:, 'xmin'] = df_KNMI.loc[:, 'xmin']
    df_setup.loc[:, 'TT'] = df_KNMI.loc[:, 'T']
    df_setup.loc[:, 'FF'] = df_KNMI.loc[:, 'FF']
    df_setup.loc[:, 'dd'] = df_KNMI.loc[:, 'DD']
    df_setup.loc[:, 'Q'] = df_KNMI.loc[:, 'Qnew']
    df_setup.loc[:, 'Qdif'] = df_KNMI.loc[:, 'Qdif']
    df_setup.loc[:, 'sunalt'] = df_KNMI.loc[:, 'sunalt']
    df_setup.loc[:, 'RH'] = df_KNMI.loc[:, 'U']
    df_setup.loc[:, 'wind'] = df_KNMI.loc[:, 'wind']
    df_setup.loc[:, 'WE'] = df_KNMI.loc[:, 'WE']
    df_setup.loc[:, 'winddir'] = df_KNMI.loc[:, 'winddir']
    df_setup.loc[:, 'daynight'] = df_KNMI.loc[:, 'daynight']
    df_setup.loc[:, 'diurnal'] = df_KNMI.loc[:, 'diurnal']
    df_setup.loc[:, 'Tmin'] = df_KNMI.loc[:, 'Tmin']
    df_setup.loc[:, 'Tmax'] = df_KNMI.loc[:, 'Tmax']
    df_setup.loc[:, 'U'] = df_KNMI.loc[:, 'FH']

    df_setupt = df_setup.T

    print(df_setup)
    print(df_setupt)

    for i in range(len(df_setupt.index)):
        df_setupt.loc[:, i].to_csv(f'{basedirectory}\\{subdirectory}\\set{str(i)}.csv')


def popfirstrow(basedirectory, subdirectory, input_file, output_file):
    with open(f'{basedirectory}\\{subdirectory}\\{input_file}', 'r', newline='') as csvfile_in, open(f'{basedirectory}\\{subdirectory}\\{output_file}', 'w', newline='') as csvfile_out:
        # Create a CSV reader and writer
        csv_reader = csv.reader(csvfile_in)
        csv_writer = csv.writer(csvfile_out)

        # Skip the first row (header) using next()
        next(csv_reader)

        # Write the remaining rows to the output CSV file
        for row in csv_reader:
            csv_writer.writerow(row)


writeknmicsv('D:\\project\\run3', 'input', 'knmi_results_wind.csv', 'knmi_result_tmintmax.csv')

writesetup('D:\\project\\run3', 'input', 'knmi_results.csv')

popfirstrow('D:\\project\\run3', 'input', f'set{0}.csv', f'set0100.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{1}.csv', f'set0200.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{2}.csv', f'set0300.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{3}.csv', f'set0400.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{4}.csv', f'set0500.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{5}.csv', f'set0600.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{6}.csv', f'set0700.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{7}.csv', f'set0800.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{8}.csv', f'set0900.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{9}.csv', f'set1000.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{10}.csv', f'set1100.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{11}.csv', f'set1200.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{12}.csv', f'set1300.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{13}.csv', f'set1400.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{14}.csv', f'set1500.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{15}.csv', f'set1600.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{16}.csv', f'set1700.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{17}.csv', f'set1800.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{18}.csv', f'set1900.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{19}.csv', f'set2000.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{20}.csv', f'set2100.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{21}.csv', f'set2200.csv')
popfirstrow('D:\\project\\run3', 'input', f'set{22}.csv', f'set2300.csv')


