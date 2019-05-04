
from datetime import datetime, timedelta

class Util:
    """ This class contains different util methods """

    @staticmethod
    def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    @staticmethod
    def mean(value):
        """ calculate mean value of an array"""
        return (sum(value) / float(len(value)))

