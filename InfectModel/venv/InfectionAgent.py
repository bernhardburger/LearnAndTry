import SimConfig as conf

class Relation:


    def __init__(self, fromID, toID, exposureTime, relationType):
        self.fromID = fromID
        self.toID = toID
        self.exposureTime = exposureTime
        self.relationType = relationType



    def __repr__(self):
        return f"Relastion: from {self.fromID} to {self.toID} of type {self.relationType} with {self.exposureTime} exposure time "


class Agent:


    def __init__(self, ID):
        self.AgentID = ID
        self.relations = []
        self.healthState = conf.AgentHealthState[0]
        self.lastStateChange = 0
        self.newState = conf.AgentHealthState[0]
        self.registeredForTesting = False
        self.testDay = 0
        self.testResult = False


    def __repr__(self):
        return  "Agent ID: {} \nAgent State: {}\n Relations: {}\n Tested positive: {}".format(str (self.AgentID),
                                                                                              self.healthState,
                                                                                              str(self.relations),
                                                                                              str (self.testedPositive))


