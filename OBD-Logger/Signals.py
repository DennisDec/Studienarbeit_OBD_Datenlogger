from OBDSignal import OBDSignal
import numpy as np


__signals__ = [
    OBDSignal("SPEED"                   , "Car speed"                     , 1         , 1),
    OBDSignal("RPM"                     , "Revolutions per minute"        , 1         , 2),
    OBDSignal("ENGINE_LOAD"             , "Engine load"                   , 1         , 3),
    OBDSignal("MAF"                     , "Description"                   , 1         , 4),
    OBDSignal("AMBIANT_AIR_TEMP"        , "Description"                   , 1         , 5),
    OBDSignal("RELATIVE_ACCEL_POS"      , "Description"                   , 1         , 6),
    OBDSignal("COMMANDED_EQUIV_RATIO"   , "Description"                   , 1         , 7),
    OBDSignal("FUEL_LEVEL"              , "Description"                   , 1         , 8),
]


class Signals:
    def __init__(self):
        self.signals = __signals__

        for s in self.signals:
            if s is not None:
                self.__dict__[s.name] = s

    def __getitem__(self, key):
        """
            Signals can be accessed by different ways

            signals.RPM
            signals.["RPM"]
            signals.[1]
        """
        if isinstance(key, int):
            return self.signals[key]
        elif isinstance(key, str):
            return self.__dict__[key]

    def getSignalList(self):
        return self.signals



signals = Signals()


# # signals.getSignalList()
# for s in signals.getSignalList():
#     print(s)


# print([s.name for s in signals.getSignalList()])
# # print(signals["RPM"].sampleRate)


# data = {}

# data["RPM"] = [1,2,3,4,5,]

# data["Speed"] = [3,3,3,3,3,3,]

# print(data)

