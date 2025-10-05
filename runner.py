import numpy as np
from numpy.polynomial import Polynomial

SMOOTHSTEPS = [
    Polynomial([0, 1]),
    Polynomial([0, 0, 3, -2]),
    Polynomial([0, 0, 0, 10, -15, 6]),
    Polynomial([0, 0, 0, 0, 35, -84, 70, -20]),
    Polynomial([0, 0, 0, 0, 0, 126, -420, 540, -315, 70]),
    Polynomial([0, 0, 0, 0, 0, 0, 462, -1980, 3465, -3080, 1386, -252]),
    Polynomial([0, 0, 0, 0, 0, 0, 0, 1716, -9009, 20020, -24024, 16380, -6006, 924]),
]

class Runner:
    def __init__(self, climb, descent, min_climb, min_descent, max_start, max_stop):
        """
            :climb:       The smoothstep function used for the climbing phase.
            :descent:     The smoothstep function used for the descent phase.
            :max_start:   At which point in the range of (0, 1) the function stops climbing (reaches its maximum value of 1); clamped between 0 and 1.
            :max_stop:    At which point in the range of (0, 1) does the function start descending; clamped between max_start and 1.
            :min_climb:   The start value of the function.
            :min_descent: The end value of the function.
        """

        self.climb       = np.clip(int(climb), 0, len(SMOOTHSTEPS))
        self.descent     = np.clip(int(descent), 0, len(SMOOTHSTEPS))
        self.min_climb   = np.clip(min_climb, 0, 1)
        self.min_descent = np.clip(min_descent, 0, 1)
        self.max_start   = np.clip(max_start, 0, 1)
        self.max_stop    = np.clip(max_stop, self.max_start, 1)

    def __call__(self, value):
        if value <= 0: return self.min_climb;
        if value >= 1: return self.min_descent;
        if self.max_start <= value and value <= self.max_stop: return 1;
        if value < self.max_start:
            return self.min_climb + (1 - self.min_climb) * SMOOTHSTEPS[self.climb](value / self.max_start)
        return self.min_descent + (1 - self.min_descent) * SMOOTHSTEPS[self.descent]((1 - value) / (1 - self.max_stop))

class ScaledRunner(Runner):
    def __init__(self, max_bpm, duration, climb, descent, min_climb, min_descent, max_start, max_stop):
        """
            :max:      The maximum SPH.
            :duration: The duration of the running session.
        """
        super().__init__(climb, descent, min_climb, min_descent, max_start, max_stop);
        self.max_bpm = max_bpm
        self.duration = duration

    def __call__(self, value):
        value = np.clip(value, 0, self.duration)
        return self.max_bpm * super().__call__(value / self.duration)
