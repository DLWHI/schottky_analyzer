import numpy as np
import pandas as pd
from numpy.lib.stride_tricks import sliding_window_view as swv

E_CHARGE = 1.60217663e-19
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

    def getDensity(self):
        return self.__dens_interp

    def getVoltageLn(self):
        if not hasattr(self, "__volt_log"):
            dV = np.diff(self.__volt)
            dlnJ = np.diff(np.log(self.__dens))
            self.__volt_log = dV/dlnJ
        return self.__volt_log

    def getResistance(self):
        if not hasattr(self, "__volt_log"):
            self.getVoltageLn()
        if not hasattr(self, "__resistance"):
            slope = np.diff(self.__volt_log)/np.diff(self.__dens_interp)
            self.__slope = np.average(np.extract(slope == slope, slope))
            self.__resistance = self.__slope/self.__area
        return self.__resistance

    def getIdeality(self):
        if not hasattr(self, "__volt_log"):
            self.getVoltageLn()
        if not hasattr(self, "__ideality"):
            dens, vlog = self.__remove_nans()
            fit = np.polyfit(dens, vlog, 1)
            print(fit)
            line = np.poly1d(fit)
            self.__ideality = line([1])[0]
        return self.__ideality
    
    def __remove_nans(self):
        length = len(self.__volt_log)
        dens = self.__dens_interp
        vlog = self.__volt_log
        nans = []
        for i in range(length):
            if (vlog[i] != vlog[i]):
                nans += [i]
        return np.delete(dens, nans), np.delete(vlog, nans)

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
