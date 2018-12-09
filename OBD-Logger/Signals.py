from OBDSignal import OBDSignal
import numpy as np

__signals__ = [
  #           SignalName                  db-name                       isOBDSignal  sampleRate     Index
    OBDSignal("TIME"                    , "time"                            ,False      , 1         , 0),

    #OBD SIGNALS:
    OBDSignal("SPEED"                   , "speed"                           ,True       , 1         , 1),
    OBDSignal("RPM"                     , "rpm"                             ,True       , 1         , 2),
    OBDSignal("ENGINE_LOAD"             , "engine_load"                     ,True       , 1         , 3),
    OBDSignal("MAF"                     , "maf"                             ,True       , 1         , 4),
    OBDSignal("AMBIANT_AIR_TEMP"        , "temperature"                     ,True       , 1         , 5),
    OBDSignal("RELATIVE_ACCEL_POS"      , "pedal"                           ,True       , 1         , 6),
    OBDSignal("COMMANDED_EQUIV_RATIO"   , "afr"                             ,True       , 1         , 7),
    OBDSignal("FUEL_LEVEL"              , "fuel_level"                      ,True       , 2         , 8),

    #Other SIGNALS:
    OBDSignal("GPS_Long"               , "Longitude"                       ,False      , 2         , 8),
    OBDSignal("GPS_Lat"                , "Latitude"                        ,False      , 2         , 8),
    #OBDSignal("GPS_Alt"                , "Altitude"                        ,False      , 2         , 8),
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
    
    def getTimeSignal(self):
        return [x for x in self.signals if x.name == "TIME"][0]

    def getOBDSignalList(self):
        return [x for x in self.signals if x.isOBDSignal == True]


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



