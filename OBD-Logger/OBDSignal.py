

class OBDSignal:

    def __init__(self, name, db_name, isOBDSignal, sampleRate, roundDigit):
        self.name = name
        self.db_name = db_name
        self.isOBDSignal = isOBDSignal
        self.sampleRate = sampleRate
        self.roundDigit = roundDigit

    def __str__(self):
        return "%s" % (self.name)

    def __eq__(self, other):
        if isinstance(other, OBDSignal):
            return self.name == other.name and self.sampleRate == other.sampleRate




















