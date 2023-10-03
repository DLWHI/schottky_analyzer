import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv

E_CHARGE = -1.60217663e-19
C_BOLTZMANN = 1.380649e-23
ROOM_TEMP = 293
A = 112e-4

class Analyzer:
    def __init__(self, voltage, current, area) -> None:
        self.__area = area
        self.__volt = voltage
        self.__current = current
        self.__dens = current/area
        self.__dens_interp = swv(self.__dens, 2).mean(axis=1)
        self.__volt_log = None
        self.__resistance = None
        self.__ideality = None
        self.__h = None
        self.__barrier = None

    def getDensity(self):
        return self.__dens_interp

    def getVoltageLn(self):
        if self.__volt_log is None:
            dV = np.diff(self.__volt)
            dlnJ = np.diff(np.log(self.__dens))
            self.__volt_log = dV/dlnJ
        return self.__volt_log

    def getResistance(self):
        if self.__volt_log is None:
            self.getVoltageLn()
        if self.__h is None:
            self.getH()
        if self.__resistance is None:
            slope = np.diff(self.__volt_log)/np.diff(self.__dens_interp)
            self.__slope = np.average(np.extract(slope == slope, slope))
            self.__resistance = self.__slope/self.__area
            slope = np.diff(self.__h)/np.diff(self.__dens)
            slope = np.average(np.extract(slope == slope, slope))
            self.__resistance += slope/self.__area
            self.__resistance /= 2
        return self.__resistance

    def getIdeality(self):
        if self.__volt_log is None:
            self.getVoltageLn()
        if self.__ideality is None:
            dens, vlog = self.__remove_nans(self.__dens_interp, self.__volt_log)
            fit = np.polyfit(dens, vlog, 1)
            line = np.poly1d(fit)
            self.__intersect = line(0)
            self.__ideality = self.__intersect*E_CHARGE/(C_BOLTZMANN*ROOM_TEMP)
        return self.__ideality
    
    def getH(self):
        if self.__ideality is None:
            self.getIdeality()
        if self.__h is None:
            lg = np.log(self.__dens/(A*ROOM_TEMP*ROOM_TEMP))
            self.__h = self.__volt - self.__intersect*lg
        return self.__h
    
    def getBarrier(self):
        if self.__h is None:
            self.getH()
        if self.__barrier is None:
            dens, h = self.__remove_nans(self.__dens, self.__h)
            fit = np.polyfit(dens, h, 1)
            line = np.poly1d(fit)
            self.__barrier = line(0)/self.__ideality
        return self.__barrier

    def __remove_nans(self, x, y):
        length = len(y)
        nans = []
        for i in range(length):
            if (y[i] != y[i]):
                nans += [i]
        return np.delete(x, nans), np.delete(y, nans)

# n = y[-1] - slope*np.log(J[-1])

# H = V - (n*k*t/q)*np.log(J/(A*t*t))

# phib = (H[-1] - slope*J[-1])/n

# print("R =", R)
# print("n =",  n)
# print("фb = ", phib*6.242e+18)

# measures["dV/d(lnJ)"] = pd.Series(y)
# measures["H(J)"] = pd.Series(H)
# fig = px.scatter(
#         measures,
#         x="Density (A/m^2)",
#         y="H(J)",
#         color="Light",
#         symbol="Light"
#     )
# fig.show()
