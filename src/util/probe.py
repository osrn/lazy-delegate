from .log import logerr
import datetime

class Probe():
    """
    Probe class keeps track of a value, raising and clearing an alert status
    when the value is above or below a certain threshold.

    For the sake of simplicity the threshold (limit) acts as an upper bound when positive,
    and lower bound when negative, when the Probe value is set through the value setter.

    The class also allows for custom alarm logic when the Probe value is assigned through the setValue method.
    """
    def __init__(self, name, init=0, limit=None):
        now = datetime.datetime.now()
        self.name = name        # probe title - shows in discord
        self.th = limit         # the threshold above/or below which alarm raised
        self._now = init        # last value
        self._prev = init       # previous value
        self._lastalert = now   # last alert raise time
        self._lastcease = now   # last alert cease time
        self._alertcount = 0    # number of times value out of limits
        self.alertdesc = ''     # alert supplementary information
        self.notif = ''         # supplemantary notification message
        self.notifpending=False

    @property
    def isAlert(self):
        return False if (self._alertcount == 0) else True

    @property
    def lastAlertAt(self):
        return self._lastalert

    @property
    def lastCeaseAt(self):
        return self._lastcease

    @property
    def alertCount(self):
        return self._alertcount

    @property
    def value(self):
        return self._now

    @property
    def prevValue(self):
        return self._prev

    @value.setter
    def value(self, newvalue):
        """ Set the current value for the probe.
        If a limit were defined, compare the new value against the threshold and set alert status
        """
        self._prev = self._now
        self._now = newvalue
        
        if (self._now != self._prev):
            if (self._now == 'n/a'):
                self._alertcount += 1
                print('DEBUG: probe %s alarm raised ' % (self.name))
                self._lastalert = datetime.datetime.now()
            else:
                sign = 1 if self.th == 0 else self.th / abs(self.th)
                if ((self.th is not None) and (sign * self._now > self.th)):
                    self._alertcount += 1
                    if ((self._prev == 'n/a') or (sign * self._prev <= self.th)):
                        print('DEBUG: probe %s alarm raised ' % (self.name))
                        self._lastalert = datetime.datetime.now()
                else:
                    if (self._alertcount > 0):
                        print('DEBUG: probe %s alarm ceased ' % (self.name))
                        self._alertcount = 0
                        self._lastcease = datetime.datetime.now()


    def setValue(self, newvalue, alarmlogic, **kwargs):
        """ Set the current value for the probe.
        Compare the new value against the passed function to decide on alert status
        """
        self._prev = self._now
        self._now = newvalue

        if (self._now != self._prev):
            if (self._now == 'n/a'):
                self._alertcount += 1
                print('DEBUG: probe %s alarm raised ' % (self.name))
                self._lastalert = datetime.datetime.now()
            else:
                if (alarmlogic(self._now)):
                    self._alertcount += 1
                    if ((self._prev == 'n/a') or (not(alarmlogic(self._prev)))):
                        print('DEBUG: probe %s alarm raised ' % (self.name))
                        self._lastalert = datetime.datetime.now()
                        self.alertdesc = kwargs.get('err')

                else:
                    if (self._alertcount > 0):
                        print('DEBUG: probe %s alarm ceased ' % (self.name))
                        self._alertcount = 0
                        self._lastcease = datetime.datetime.now()

    def getFmtValue(self, fmtfunc):
        return fmtfunc(self._now)
