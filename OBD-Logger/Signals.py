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
        #TODO: Sort by column in File
        return self.signals

    def containsSignalByString(self, str):
        for s in self.signals:
            if(s.name == str):
                return True
        return False

    def containsSignal(self, signal):
        if not isinstance(signal, OBDSignal):
            raise ValueError("Value has to be instance of OBDSignal")
        for s in self.signals:
            if(s == signal):
                return True
        return False



signals = Signals()



