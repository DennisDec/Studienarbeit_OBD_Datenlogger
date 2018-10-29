

class OBDSignal:

    def __init__(self, name, description, sampleRate, columnInFile):
        self.name = name
        self.description = description
        self.sampleRate = sampleRate
        self.columnInFile = columnInFile

    def __str__(self):
        return "%s" % (self.name)    


















