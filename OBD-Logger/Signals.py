from OBDSignal import OBDSignal
import numpy as np


__signals__ = [
  #           SignalName                  description               isOBDSignal  sampleRate      Index
    OBDSignal("Time"                    , "Date and Time"                ,False     , 1         , 0),
    OBDSignal("SPEED"                   , "Car speed"                    ,True      , 1         , 1),
    OBDSignal("RPM"                     , "Revolutions per minute"       ,True      , 1         , 2),
    OBDSignal("ENGINE_LOAD"             , "Engine load"                  ,True      , 1         , 3),
    OBDSignal("MAF"                     , "Description"                  ,True      , 1         , 4),
    OBDSignal("AMBIANT_AIR_TEMP"        , "Description"                  ,True      , 1         , 5),
    OBDSignal("RELATIVE_ACCEL_POS"      , "Description"                  ,True      , 1         , 6),
    OBDSignal("COMMANDED_EQUIV_RATIO"   , "Description"                  ,True      , 1         , 7),
    OBDSignal("FUEL_LEVEL"              , "Description"                  ,True      , 2         , 8),
    OBDSignal("GPS_Long"                , "Longitude"                    ,False      , 2         , 8),
    OBDSignal("GPS_Lat"                 , "Latitude"                     ,False      , 2         , 8),
    OBDSignal("GPS_Alt"                 , "Altitude"                     ,False      , 2         , 8),
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
        return [x for x in self.signals if x.isOBDSignal == True]

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



