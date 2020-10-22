import time
import math

class Smoother:
    def __init__(self, decay_lambda=1000, translation_threshold=.03, rotation_threshold=6):
        self.decay_lambda = float(decay_lambda)
        self.last_update = 0
        self.values = [0.0,0.0,0.0,0.0,0.0,0.0]
        self.thresholds = (translation_threshold, translation_threshold, translation_threshold, rotation_threshold, rotation_threshold, rotation_threshold)

    def smooth(self, vector6):
        # make sure rotation scalars have not moved around the boundary
        for i in range(3,6):
            diff = vector6[i]-self.values[i]
            if diff > 90:
                self.values[i] += 360
            elif diff < -90:
                self.values[i] -= 360

        # If any movement exceeds the threshold, no smoothing
        for i in range(0, 6):
            if abs(vector6[i] - self.values[i]) > self.thresholds[i]:
                print("Threshold exceeds bounds, i=",i)
                #print(vector6)
                #print(self.values)
                self.last_update = 0
                break

        now = math.floor(time.time()*1000)
        value_weight = math.exp((self.last_update - now)/self.decay_lambda)
        self.last_update = now
        self.values = [(1-value_weight) * vector6[i] + (value_weight) * self.values[i] for i in range(6)]
        return self.values
