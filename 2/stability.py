
class binaryStabilityChecker:
    
    def __init__(self, signalInput, threshold=30, deltaTime=10):
        self.signalInput = signalInput
        self.threshold = threshold
        self.deltaTime = deltaTime

    def getStableState(self):
        