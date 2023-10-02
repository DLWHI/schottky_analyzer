import numpy as np
import pandas as pd


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

    def getDensity(self):
        return self.__dens

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
            slope = np.diff(self.__volt_log)/np.diff(self.__dens[:-1].copy())
            self.__slope = np.average(np.extract(slope == slope, slope))
            self.__resistance = self.__slope/self.__area
        return self.__resistance

    def getIdeality(self):
        if not hasattr(self, "__volt_log"):
            self.getVoltageLn()
        if not hasattr(self, "__ideality"):
            print(self.__dens)
            print(self.__volt_log)
            fit = np.polyfit(self.__dens[:-1].copy(), self.__volt_log, 1)
            line = np.poly1d(fit)
            self.__ideality = line([1])
        return self.__ideality

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
