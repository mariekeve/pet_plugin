import numpy as np
#-------------------------------------------------------------------------------------------------------------
#directory_main = 'c:/Users/marie/Documents/thesisprep/weekprogressies/literatuur/0-1678305133663/scripts reference flowchart/scripts reference flowchart/wageningen/'
directory_main = 'c:/project/wageningen/'
directory_main = 'd:/project/run5/'
#-------------------------------------------------------------------------------------------------------------
# petparameters
# purpose: initialise and read dynamic parameters and static parameters
# input: set.csv
# output: set.csv

def writer(filename, header, arr):
    with open(filename, 'at') as f:
        f.write(f'\n{header}\n\n')
        if len(arr.shape) == 2:
            for i in range(arr.shape[0]):
                for j in range(arr.shape[1]):
                    f.write(f'{arr[i, j]:6.1f}')
                f.write('\n')
            f.write('\n')
        if len(arr.shape) == 3:
            for k in range(arr.shape[2]):
                for i in range(arr.shape[0]):
                    for j in range(arr.shape[1]):
                        f.write(f'{arr[i, j, k]:6.1f}')
                    f.write('\n')
                f.write('\n')

def wind_direction(dd,FF):

    wind = FF >= 1.5
    if wind:
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
        WE = False
    return wind, WE, winddir


def day_night(month, day, hour):

    daynight = 'night'
    diurnal = 1
    if day > 0 and day < 13 and month == 4:
        if hour > 5 and hour < 18:
            daynight = 'day'
            diurnal = data['5/18', hour]

    return daynight, diurnal

def window_footprint(winddir, upwind, sidewind, downwind, nowind, cellsize):

    #upwind = 2   #1000 210
    #sidewind = 0 #250  70
    #downwind = 0 #100  70
    #nowind = 0   #350  88

    if winddir == 'S':
        xleft = sidewind
        xright = sidewind
        ydown = upwind
        yup = downwind
    elif winddir == 'N':
        xleft = sidewind
        xright = sidewind
        ydown = downwind
        yup = upwind
    elif winddir == 'E':
        xleft = downwind
        xright = upwind
        yup = sidewind
        ydown = sidewind
    elif winddir == 'W':
        xleft = upwind
        xright = downwind
        yup = sidewind
        ydown = sidewind
    elif winddir=='C':
        xleft = nowind
        xright = nowind
        yup = nowind
        ydown = nowind

    return int(xleft/cellsize), int(xright/cellsize), int(yup/cellsize), int(ydown/cellsize)

class StatParameters():

    def __init__(self, xmin, xmax, ymin, ymax, cellsize=1, blocksize=2, station='herwijnen', station_lat=51.859,
                 station_lon=5.146):

        self.ymin = ymin
        self.ymax = ymax
        self.xmin = xmin
        self.xmax = xmax
        self.nrow = 0
        self.ncol = 0
        self.cellsize = cellsize
        self.blocksize = blocksize
        self.station = station
        self.station_lat = station_lat
        self.station_lon = station_lon
        self.directory_in = 'd:/project/run0/data/'
        self.directory_out = 'd:/project/run0/sim1/'
        self.label = 'run0sim1'
        self.Resize()

    def Resize(self):

        self.nrow = int((self.ymax - self.ymin) / self.blocksize)
        self.ncol = int((self.xmax - self.xmin) / self.blocksize)
        self.xmax = self.xmin + self.ncol * self.blocksize
        self.ymax = self.ymin + self.nrow * self.blocksize
        self.nrow = int((self.ymax - self.ymin) / self.cellsize)
        self.ncol = int((self.xmax - self.xmin) / self.cellsize)

    def Reader(self, filename):

        with open(filename, 'r') as fp:
            lines = fp.readlines()
            lines = [line.strip() for line in lines]
            lines = [line.split(', ') for line in lines]
            self.ymin = lines[0][1]
            self.ymax = lines[1][1]
            self.xmin = lines[2][1]
            self.xmax = lines[3][1]
            self.cellsize = lines[4][1]
            self.blocksize = lines[5][1]

    def Writer(self, filename):

        with open(filename, 'w') as fp:
            fp.write(f'ymin,{self.ymin}\n')
            fp.write(f'ymax,{self.ymax}\n')
            fp.write(f'xmin,{self.xmin}\n')
            fp.write(f'xmax,{self.xmax}\n')
            fp.write(f'cellsize,{self.cellsize}\n')
            fp.write(f'blocksize,{self.blocksize}\n')

class DynParameters():

    #def __init__(self, Date=20150701, decade=1, hour=10, min = 0, TT=28, FF=6, dd=100, Q=794.4444444, Qdif=158.8888889,
    #             sunalt=55.3, RH=48, diurn=0.03):

    def __init__(self, Date=20150701, decade=1, hour=10, min=0, TT=28, FF=6, dd=100, Q=794.444, Qdif=158.88,
                 sunalt=55.3, RH=48, diurnal=0.03, Tmin= 24, Tmax = 34, U = 6):

        self.Date = Date
        self.decade = decade

        self.year = int(self.Date / 10000)
        self.month = int((Date - self.year * 10000) / 100)
        self.day = int(Date - self.year * 10000 - self.month * 100)
        self.hour = int(hour)
        self.min = int(min)

        self.TT = TT            #TT:    Temperatuur (in 0.1 graden Celsius) op 1.50 m hoogte tijdens de waarneming
        self.FF = FF            #FF:    Windsnelheid (in 0.1 m/s) gemiddeld over de laatste 10 minuten van het afgelopen uur
        self.dd = dd            #DD:    Winddirection (in graden) gemiddeld over de laatste 10 minuten van het afgelopen uur (360=noord, 90=oost, 180=zuid, 270=west, 0=windstil 990=veranderlijk.
        self.Q = Q              #Q:     Global solar irradiationGlobale straling (in J/cm2) per uurvak
        self.Qdif = Qdif        #Qdif:  Difuse irradiation calculated from Q
        self.sunalt = sunalt
        self.RH = RH            #RH: relative humidity
        self.daynight, self.diurnal = day_night(self.month, self.day, self.hour)

        self.diurnal = diurnal
        self.S = 1.11           # mean solar radiation 1361 W/m2 = 1.11 Km/s S = 1.11 / 1361 / 3600 Q (J/m2)

        self.Tmin = Tmin        #18 #18    24
        self.Tmax = Tmax        #22 # 22   34
        self.U = U              #6 # m/s
        #self.diurnalcycle = 0.07

        self.wind, self.WE, self.winddir = wind_direction(self.dd, self.FF)
        '''
        self.upwind = 4
        self.sidewind = 2
        self.downwind = 2
        self.nowind = 2
        self.upveg = 4
        self.sideveg = 2
        self.downveg = 2
        self.noveg = 2
        '''

        self.upwind = 200
        self.sidewind = 75
        self.downwind = 75
        self.nowind = 175
        self.upveg = 1000
        self.sideveg = 250
        self.downveg = 100
        self.noveg = 350

    def Reader(self, filename):

        with open(filename, 'r') as fp:
            lines = fp.readlines()
            lines = [line.strip() for line in lines]
            lines = [line.split(', ') for line in lines]
            self.Date = lines[0][1]
            self.month = lines[1][1]
            self.decade = lines[2][1]
            self.hour = lines[3][1]
            self.TT = lines[4][1]
            self.FF = lines[5][1]
            self.dd = lines[6][1]
            self.Q = lines[7][1]
            self.Qdif = lines[8][1]
            self.sunalt = lines[9][1]
            self.RH = lines[10][1]
            self.diurnal = lines[19][1]
            #self.UHImax = lines[12][1]
            self.Tmin = lines[20][1]
            self.Tmax = lines[21][1]
            self.U = lines[22][1]
            self.wind, self.WE, self.winddir = wind_direction(self.dd, self.FF)

    def Writer(self, filename):

        with open(filename, 'w') as fp:
            fp.write(f'Date,{self.Date}\n')
            fp.write(f'month,{self.month}\n')
            fp.write(f'decade,{self.decade}\n')
            fp.write(f'hour,{self.hour}\n')
            fp.write(f'TT,{self.TT}\n')
            fp.write(f'FF,{self.FF}\n')
            fp.write(f'dd,{self.dd}\n')
            fp.write(f'Q,{self.Q}\n')
            fp.write(f'Qdif,{self.Qdif}\n')
            fp.write(f'sunalt,{self.sunalt}\n')
            fp.write(f'RH,{self.RH}\n')
            fp.write(f'wind,{self.wind}\n')
            fp.write(f'WE,{self.WE}\n')
            fp.write(f'winddir,{self.winddir}\n')
            fp.write(f'diurnal,{self.diurnal}\n')
            #fp.write(f'UHImax,{self.UHImax}\n')
            fp.write(f'Tmin,{self.Tmax}\n')
            fp.write(f'Tmax,{self.Tmin}\n')
            fp.write(f'U,{self.U}\n')
            fp.write(f'upwind,{self.upwind}\n')
            fp.write(f'sidewind,{self.sidewind}\n')
            fp.write(f'downwind,{self.downwind}\n')
            fp.write(f'nowind,{self.nowind}\n')
            fp.write(f'upveg,{self.upveg}\n')
            fp.write(f'sideveg,{self.sideveg}\n')
            fp.write(f'downwveg,{self.downveg}\n')
            fp.write(f'nowveg,{self.noveg}\n')