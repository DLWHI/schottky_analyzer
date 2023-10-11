import numpy as np
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
        self.__volt_log = None
        self.__resistance = None
        self.__ideality = None
        self.__h = None
        self.__barrier = None
        self.__fit_vln = None
        self.__fit_h = None

    def getDensity(self):
        return self.__dens

    def getVoltageLn(self):
        if self.__volt_log is None:
            dV = np.diff(self.__volt)
            dlnJ = np.diff(np.log(self.__dens))
            self.__volt_log = dV/dlnJ
            dens = swv(self.__dens, 2).mean(axis=1)
            self.__fit_vln = self.__fit(dens, self.__volt_log)
        return self.__volt_log

    def getH(self):
        if self.__fit_vln is None:
            getVoltageLn()
        if self.__h is None:
            lg = np.log(self.__dens/(A*ROOM_TEMP*ROOM_TEMP))
            self.__h = self.__volt - self.__fit_vln[1]*lg
            dens = swv(self.__dens, 2).mean(axis=1)
            # self.__fit(dens, self.__h)
        return self.__h

    def getParameters(self):
        if self.__volt_log is None or self.__fit is None:
            self.getVoltageLn()
        if self.__h is None:
            self.getH()
        return self.__fit_vln[0]/self.__area, self.__fit_vln[1]*E_CHARGE/(ROOM_TEMP*C_BOLTZMANN)
        

        
    def __fit(self, x, y):
        x, y = self.__remove_nans(x, y)
        print(x)
        print(y)
        fit = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=None)[0]
        return fit
        

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
