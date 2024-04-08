import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import matplotlib.dates as mdates
import datetime as dt
import math

# BRON: KONINKLIJK NEDERLANDS METEOROLOGISCH INSTITUUT (KNMI)
# Opmerking: door stationsverplaatsingen en veranderingen in waarneemmethodieken zijn deze tijdreeksen van dagwaarden mogelijk inhomogeen! Dat betekent dat deze reeks van gemeten waarden niet geschikt is voor trendanalyse. Voor studies naar klimaatverandering verwijzen we naar de gehomogeniseerde reeks maandtemperaturen van De Bilt <http://www.knmi.nl/kennis-en-datacentrum/achtergrond/gehomogeniseerde-reeks-maandtemperaturen-de-bilt> of de Centraal Nederland Temperatuur <http://www.knmi.nl/kennis-en-datacentrum/achtergrond/centraal-nederland-temperatuur-cnt>.
#
#
# STN      LON(east)   LAT(north)     ALT(m)  NAME
# 356:         5.146       51.859       0.70  HERWIJNEN
#
# YYYYMMDD = Datum (YYYY=jaar MM=maand DD=dag);
# TG       = Etmaalgemiddelde temperatuur (in 0.1 graden Celsius);
# TN       = Minimum temperatuur (in 0.1 graden Celsius);
# TNH      = Uurvak waarin TN is gemeten;
# TX       = Maximum temperatuur (in 0.1 graden Celsius);
# TXH      = Uurvak waarin TX is gemeten;
# Q        = Globale straling (in J/cm2);
#
# STN,YYYYMMDD,   TG,   TN,  TNH,   TX,  TXH,    Q
#
#  356,20040401,  131,   36,    6,  197,   16, 1518
#  356,20040402,  118,   80,    6,  169,   13,  844

# BRON: KONINKLIJK NEDERLANDS METEOROLOGISCH INSTITUUT (KNMI)
# Opmerking: door stationsverplaatsingen en veranderingen in waarneemmethodieken zijn deze tijdreeksen van uurwaarden mogelijk inhomogeen! Dat betekent dat deze reeks van gemeten waarden niet geschikt is voor trendanalyse. Voor studies naar klimaatverandering verwijzen we naar de gehomogeniseerde reeks maandtemperaturen van De Bilt <http://www.knmi.nl/klimatologie/onderzoeksgegevens/homogeen_260/index.html> of de Centraal Nederland Temperatuur <http://www.knmi.nl/klimatologie/onderzoeksgegevens/CNT/>.
#
#
# STN      LON(east)   LAT(north)     ALT(m)  NAME
# 356:         5.146       51.859       0.70  HERWIJNEN
#
# YYYYMMDD = datum (YYYY=jaar,MM=maand,DD=dag);
# HH       = tijd (HH=uur, UT.12 UT=13 MET, 14 MEZT. Uurvak 05 loopt van 04.00 UT tot 5.00 UT;
# DD       = Windrichting (in graden) gemiddeld over de laatste 10 minuten van het afgelopen uur (360=noord, 90=oost, 180=zuid, 270=west, 0=windstil 990=veranderlijk. Zie http://www.knmi.nl/kennis-en-datacentrum/achtergrond/klimatologische-brochures-en-boeken;
# FH       = Uurgemiddelde windsnelheid (in 0.1 m/s). Zie http://www.knmi.nl/kennis-en-datacentrum/achtergrond/klimatologische-brochures-en-boeken;
# FF       = Windsnelheid (in 0.1 m/s) gemiddeld over de laatste 10 minuten van het afgelopen uur;
# T        = Temperatuur (in 0.1 graden Celsius) op 1.50 m hoogte tijdens de waarneming;
# Q        = Globale straling (in J/cm2) per uurvak;
# U        = Relatieve vochtigheid (in procenten) op 1.50 m hoogte tijdens de waarneming;
#
# STN,YYYYMMDD,   HH,   DD,   FH,   FF,    T,    Q,    U
#
#  356,20040331,    1,   80,   50,   50,   58,    0,   78
#  356,20040331,    2,   90,   40,   30,   54,    0,   77

# Date	month	decade	hour	TT	FF	dd	Q	Qdif	sunalt	RH	diurn	UHImax
# 20150701	7	1	10	28	6	100	794.4444444	158.8888889	55.3	48	0.03	3.35
# 20150701	7	1	11	29.8	6	100	855.5555556	171.1111111	60.1	44	0.05	3.35
# 20150701	7	1	12	31.2	6	130	868.0555556	173.6111111	60.9	35	0.07	3.35
# 20150701	7	1	13	32.1	5	130	825	165	57.4	37	0.11	3.35
# 20150701	7	1	14	32.8	4	140	743.0555556	148.6111111	50.8	35	0.16	3.35
# 20150701	7	1	15	32.9	5	120	629.1666667	149.4126154	42.5	37	0.23	3.35
# 20150701	7	1	16	33	4	130	491.6666667	144.1847869	33.4	37	0.31	3.35




#==============================================================================
class knmi:
   
    def __init__(self, xmin, xmax):
        
        self.xmin = xmin
        self.xmax = xmax
        
        self.dataframeH = pd.DataFrame() # input  if !day fileH.csv -> fileH_sample.csv
        self.downscaleH = pd.DataFrame() # output if !day -> fileH_down.csv
        self.upscaleH = pd.DataFrame()   # output if !day -> fileH_up.csv
       
    def __repr__(self):
        return f'{self.dim}'

# read ========================================================================
    def read(self, fname):

        period = self.xmax - self.xmin
        tottime = (period.total_seconds()/3600/24)        
        
        filename = fname + '.csv'
        mydateparser = lambda x: pd.datetime.strptime(x, '%Y%m%d')
        self.dataframeH = pd.read_csv(filename, parse_dates = ['YYYYMMDD'], 
                                      date_parser=mydateparser,skipinitialspace=True, index_col=0)

        lijst = []
        kijst = []
        for index, row in self.dataframeH.iterrows():
            index = row['YYYYMMDD'] + dt.timedelta(row['H']/24)   
            time = index - self.xmin
            lijst.append(index) 
            kijst.append(time.total_seconds()/3600/24)

        # hour: SQ, RH, FH, TT, Q, U
        self.dataframeH['dtime'] = lijst
        self.dataframeH['time'] = kijst
        self.dataframeH = self.dataframeH.loc[(self.dataframeH['time'] > -0.001) & (self.dataframeH['time'] < tottime+0.001)] 
        self.dataframeH.index = self.dataframeH['dtime']
        self.dataframeH = self.dataframeH.drop(columns='dtime')
        self.dataframeH = self.dataframeH.drop(columns='YYYYMMDD')
        self.dataframeH = self.dataframeH.dropna(axis=1,how='all')
        self.dataframeH.interpolate(method='linear',axis=1,inplace=True)
        self.dataframeH.rename(columns={'T': 'TT'}, inplace=True)
        #self.dataframeH['SQ'].values[self.dataframeH['SQ'].values < 0.0] = 0.0
        self.dataframeH['RH'].values[self.dataframeH['RH'].values < 0.0] = 0.0
        #self.dataframeH.FH *= 0.1 # m/s
        self.dataframeH.FF *= 0.1  # m/s
        self.dataframeH.TT *= 0.1 # C

        #self.dataframeH.SQ *= 0.1 / 3600 # h/s
        self.dataframeH.Q  *= 1e4 / 3600 # W/m2
        self.dataframeH.RH *= 0.1 / 3600 / 1000 # m/s 
        self.dataframeH.U  *= 1.0 # %
        #self.dataframeH = self.dataframeH.drop(columns={'SQ','H'})
        
        self.dataframeH = self.dataframeH.copy()
        self.dataframeH = self.dataframeH.resample('1h').mean()
        self.dataframeH.interpolate(inplace=True)

        self.dataframeH.UHI = self.dataframeH.TT * self.dataframeH.TT ##  aanvullen


        #print(self.dataframeH)
           
 
# stat ========================================================================
    def stat(self, fname):
        
        filename = fname + '_stat.csv'          
        with open(filename,'w') as f:
            #f.write(f'FH (m/s)  {self.dataframeH.FH.min():10.2f} {self.dataframeH.FH.mean():10.2f} {self.dataframeH.FH.max():10.2f}\n')
            f.write(f'FF (m/s)  {self.dataframeH.FF.min():10.2f} {self.dataframeH.FF.mean():10.2f} {self.dataframeH.FF.max():10.2f}\n')
            f.write(f'TT (C)    {self.dataframeH.TT.min():10.2f} {self.dataframeH.TT.mean():10.2f} {self.dataframeH.TT.max():10.2f}\n')
            f.write(f'Q  (W/m2) {self.dataframeH.Q.min():10.2f} {self.dataframeH.Q.mean():10.2f} {self.dataframeH.Q.max():10.2f}\n')
            f.write(f'RH (m/s)  {(self.dataframeH.RH.min()*8.64e7):10.2f} {(self.dataframeH.RH.mean()*8.64e7):10.2f} {(self.dataframeH.RH.max()*8.64e7):10.2f}\n')
            f.write(f'U  (%)    {self.dataframeH.U.min():10.2f} {self.dataframeH.U.mean():10.2f} {self.dataframeH.U.max():10.2f}\n')


# sample ======================================================================
    def rescale(self, upscale, downscale): 
    
        self.downscaleH = self.dataframeH.copy()
        self.downscaleH = self.downscaleH.resample('30min').mean()
        self.downscaleH.interpolate(inplace=True)
        self.upscaleH = self.dataframeH.copy()
        self.upscaleH = self.upscaleH.resample('1d').mean()
        self.upscaleH.interpolate(inplace=True)
            
            
# sample ======================================================================
    def write(self, fname, upscale, downscale): 
        
        filename = fname + 'H_sample.csv'
        self.dataframeH.rename(columns={'TT':'temperature','Q':'radiation','U':'humidity','RH':'precipitation','FF':'windspeed'}, inplace=True)
        self.dataframeH.to_csv(filename)   
        if downscale:
            filename = fname + 'H_downscale.csv'
            self.downscaleH.rename(columns={'TT':'temperature','Q':'radiation','U':'humidity','RH':'precipitation','FF':'windspeed'}, inplace=True)
            self.downscaleH.to_csv(filename)
        if upscale:
            filename = fname + 'H_upscale.csv'
            self.upscaleH.rename(columns={'TT':'temperature','Q':'radiation','U':'humidity','RH':'precipitation','FF':'windspeed'}, inplace=True)
            self.upscaleH.to_csv(filename)
                            
# sample ======================================================================
    def plot(self, fname, upscale, downscale): 
        
        ext = 'png'
        symbol = 'H'

        period = self.xmax - self.xmin
        tottime = (period.total_seconds()/3600/24)

        if tottime > 367:
            locator = mdates.YearLocator()  
            formatter = mdates.DateFormatter('%Y')
            xlabel='year'
            mark = 'None'
            line = '-'
        elif tottime > 32:
            locator = mdates.MonthLocator()  
            formatter = mdates.DateFormatter('%m')
            xlabel=f'month {self.xmin.year:04d}'
            mark = 'None'
            line = '-'
        else:
            locator = mdates.DayLocator()  
            formatter = mdates.DateFormatter('%d') #'%Y-%m-%d')
            xlabel= f'day {self.xmin.year:04d}-{self.xmin.month:02d}'
            mark = '.'
            line = '-'
        
        size = 16
        width = 12 
        height = 6
        fontP = FontProperties()
        fontP.set_size(12)

        #---------------------------------------------------------------------------------------------------------------
        # temperature figure

        plt.figure(linewidth = 2, figsize = (width,height))
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        if downscale:
            plt.plot(self.downscaleH.TT, label='30 min',marker=mark, linestyle=line)
        elif  upscale:
            plt.plot(self.upscaleH.TT, label='12 hour',marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.TT, label='1 hour', color= '#93b2dd', marker=mark, linestyle=line)

        plt.axhline(y=20, color='#f8bc77', linestyle='--', label='20 degrees - summer day')
        plt.axhline(y=25, color='#f15d4a', linestyle='--', label='25 degrees - heatwave day')

        # indices_above_25 = np.where(np.array(self.upscaleH.TT) >= 25)[0]
        #
        # # Plot dots where the temperature plot intersects the axis line of 25 degrees or higher
        # plt.scatter(indices_above_25, self.upscaleH.TT[indices_above_25], color='red',
        #             label='Intersection (25 degrees or higher)', marker='o')
        #
        # for index in indices_above_25:
        #     plt.axvline(x=index, color='blue', linestyle=':', label='Exceeds 25 degrees')

        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weather station'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.ylabel('TT atmospheric temperature (C)', fontsize=size)
        plt.xlim(self.xmin,self.xmax)
        plt.ylim(0,40)
        plt.legend(loc = 'upper right', fontsize=0.7*size)
        filename = fname + symbol + '_temp.'+ext
        plt.tight_layout()
        plt.savefig(filename, format = ext)
        plt.show()
        plt.close()

        # ---------------------------------------------------------------------------------------------------------------
        # shortwave radiation figure


        plt.figure(linewidth = 2, figsize = (width,height)) 
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        if downscale:
            plt.plot(self.downscaleH.Q, label='30 min', color='#f8bc77', marker=mark, linestyle=line)
        elif upscale:
            plt.plot(self.upscaleH.Q, label='12 hour', color='#f8bc77', marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.Q, label='1 hour', color='#f8bc77', marker=mark, linestyle=line)
                
        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weather station'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.ylabel('Q short wave radiation (W/m2)', fontsize=size)
        plt.xlim(self.xmin,self.xmax)
        #plt.ylim(0,1000)
        plt.legend(loc = 'upper right', prop=fontP)
        filename = fname + symbol + '_rad.'+ext
        plt.tight_layout()
        plt.savefig(filename, format = ext)
        plt.show()
        plt.close()

        """
        # ---------------------------------------------------------------------------------------------------------------
        # windspeed figure FH

        plt.figure(linewidth = 2, figsize = (width,height)) 
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        plt.tight_layout()
        
        if downscale:
            plt.plot(self.downscaleH.FH, label='30 min',marker=mark, linestyle=line)  
        elif upscale:
            plt.plot(self.upscaleH.FH, label='12 hour',marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.FH, label='1 hour',marker=mark, linestyle=line)
             
        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weerstation'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.ylabel('FH wind speed (m/s)', fontsize=size)
        plt.xlim(self.xmin,self.xmax)
        #plt.ylim(0,15)
        plt.legend(loc = 'upper right', fontsize=0.7*size) 
        filename = fname + symbol +'_wind.'+ext
        plt.tight_layout()
        plt.savefig(filename, format = ext)
        plt.show()
        plt.close()
        """

        # ---------------------------------------------------------------------------------------------------------------

        # windspeed figure FF

        plt.figure(linewidth=2, figsize=(width, height))
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        plt.tight_layout()

        if downscale:
            plt.plot(self.downscaleH.FF, label='30 min', color='#93b2dd', marker=mark, linestyle=line)
        elif upscale:
            plt.plot(self.upscaleH.FF, label='12 hour', color='#93b2dd', marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.FF, label='1 hour', color='#93b2dd', marker=mark, linestyle=line)

        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weather station'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.ylabel('wind speed (m/s)', fontsize=size)
        plt.xlim(self.xmin, self.xmax)
        # plt.ylim(0,15)
        plt.legend(loc='upper right', fontsize=0.7 * size)
        filename = fname + symbol + '_wind.' + ext
        plt.tight_layout()
        plt.savefig(filename, format=ext)
        plt.show()
        plt.close()


        # ---------------------------------------------------------------------------------------------------------------
        # humidity figure

        plt.figure(linewidth = 2, figsize = (width,height))
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        if downscale:
            plt.plot(self.downscaleH.U, label='30 min',color='#93b2dd', marker=mark, linestyle=line)
        elif upscale:
            plt.plot(self.upscaleH.U, label='12 hour', color='#93b2dd', marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.U, label='1 hour', color='#93b2dd', marker=mark, linestyle=line)
        
        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weather station'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.legend(loc = 'upper right', prop=fontP)
        plt.ylabel('U relative humidity (%)', fontsize=size)
        plt.xlim(self.xmin,self.xmax)
        #plt.ylim(20,100)
        filename = fname + symbol + '_hum.'+ext
        #plt.tight_layout()
        plt.savefig(filename, format = ext)
        plt.show()
        plt.close()

        # ---------------------------------------------------------------------------------------------------------------
        # rainfall figure

        plt.figure(linewidth = 2, figsize = (width,height)) 
        ax = plt.subplot(1, 1, 1)
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)
        
        if downscale:
            plt.plot(self.downscaleH.RH*1800*1000, label='30 min', color='#93b2dd', marker=mark, linestyle=line)
        elif upscale:
            plt.plot(self.upscaleH.RH*12*3600*1000, label='12 hour', color='#93b2dd', marker=mark, linestyle=line)
        else:
            plt.plot(self.dataframeH.RH*3600*1000, label='1 hour', color='#93b2dd', marker=mark, linestyle=line)
                
        plt.tick_params(axis='both', which='major', labelsize=size)
        plt.grid(which='major', color='k', linestyle='-', linewidth=0.5)
        title = f'{namecity} weather station'
        plt.title(title, fontsize=size)
        plt.xlabel(f'time ({xlabel})', fontsize=size)
        plt.legend(loc = 'upper right', prop=fontP)
        plt.ylabel('RH precipitation (mm)', fontsize=size)
        plt.xlim(self.xmin,self.xmax)
        #plt.ylim(0,25)
        filename = fname + symbol + '_rain.'+ext
        plt.tight_layout()
        plt.savefig(filename, format = ext)
        plt.show()
        plt.close()

#==============================================================================

upscale = False
downscale = False

directory = 'D:/project/'

#name = 'Marknesse'
#name = 'Wilhelminadorp'
#name = 'NieuwBeerta'
#name = 'DeBilt'
##name = 'Herwijnen'
#name = 'Volkel'
#name = 'Eelde'
#name = 'deBilt'
namecity = 'rotterdam'
#name = 'Voorschoten'
name = '/rotterdam_knmi_2015'

xmin = dt.datetime(2015,6,1)
xmax = dt.datetime(2015,9,30)

# xmin = dt.datetime(2013,7,1)
# xmax = dt.datetime(2013,8,1)

#xmin = dt.datetime(2013,5,1)
#xmax = dt.datetime(2013,9,30)

fname = directory + namecity + name
knmi = knmi(xmin, xmax)
knmi.read(fname)
knmi.rescale(upscale, downscale)
knmi.plot(fname, upscale, downscale)
knmi.write(fname, upscale, downscale)


