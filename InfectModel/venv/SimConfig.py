daycounter = 0
resultdataframe = []
cutoffday = 30
cutoffday2 = 80
NumberofAgents = 80000 # Number of Agents to be created
_overwhelmed = False
simulationDays = 200

measurementStart = 20
measurementCapacity =300
numberTestedSet = set()
minTestinterval = 3

measureResultsDataFrame = []
measureOverallResults = [0,0,0] #  positive, negative, positive percentage
measurementPipeline = []

#infectioner data for connection
FamilyConnections = 2
FamilyConnectionVariation = 2  # family connection can range inFamily Connection +- Variation
FamilyExposureTime = 16/24 #average hours per day exposure (think about the weekend!)

WorkplaceConnection = 8
WorkplaceConnectionVariation = 5
WorkplaceExposureTime = 5/24

ExternalConnnection = 5
ExternalConnectionVariation = 0
ExternalExposureTime = 0.25/24

WP_reductionrate_LD = 0.2
WP_reductionrate_postLD = 0.3

EX_reductionrate_LD = 0.005
EX_reductionrate_postLD = 0.1

overwhelm_percentage = 100

def getOverwhelmed():
     return _overwhelmed

def setOverwhelmed(perc):
    if perc < overwhelm_percentage:
        _overwhelmed = False
    else:
        _overwhelmed = True


def getWorkplaceExposureModificator():
    if daycounter <= cutoffday:
        return 1
    elif cutoffday < daycounter <= cutoffday2:
        return 0.05
    else:
        return 1

def ExternalExposureModificator():
    if daycounter <= cutoffday:
        return 1
    elif cutoffday < daycounter <= cutoffday2:
        return 0.1
    else:
        return 1


transmission_rate = 0.05

sick_transmssion_reduction = 0.1
hospitalized_transmission_reduction = 0.03
critical_transmission_reduction = 0.01


AgentHealthState = {0: "healthy",
                    1: "infected",
                    2: "infectious",
                    3: "sick",
                    4: "hospitalised",
                    5: "critical",
                    6: "deceased",
                    7: "recovered"}

IndexLookUP = {state:index for index,state in AgentHealthState.items()}




"""state change matrix of agents - only for state changes within the lifecycle of the desease, not contact - 
min day for possible state changes -1 indicates impossible state change"""
TransitionFromStateToStateDaysMin = [[-1, -1, -1, -1, -1, -1, -1, -1],
                                    [-1, -1, +2, -1, -1, -1, -1, -1],
                                    [-1, -1, -1, +2, -1, -1, -1, +10],
                                    [-1, -1, -1, -1, +5, +5, +5, +10],
                                    [-1, -1, -1, +4, -1, +2, +4, +8],
                                    [-1, -1, -1, -1, +2, -1, +4, +8],
                                    [-1, -1, -1, -1, -1, -1, -1, -1],
                                    [-1, -1, -1, -1, -1, -1, -1, -1],
                                    ]

TransitionFromStateToStateDaysMax = [[-1, -1, -1, -1, -1, -1, -1, -1],
                                    [-1, -1, +4, -1, -1, -1, -1, -1],
                                    [-1, -1, -1, +4, -1, -1, -1, +12],
                                    [-1, -1, -1, -1, +7, +7, +7, +8],
                                    [-1, -1, -1, +6, -1, +4, +6, +8],
                                    [-1, -1, -1, -1, +4, -1, +6, +8],
                                    [-1, -1, -1, -1, -1, -1, -1, -1],
                                    [-1, -1, -1, -1, -1, -1, -1, -1],
                                    ]

TransitionFromStateToStateProbality= [[0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 1, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0.6, 0, 0, 0, 0.5],
                                    [0, 0, 0, 0, 0.2, 0.01, 0.000001, 0.99],
                                    [0, 0, 0, 0.1, 0, 0.2, 0.000001, 0.95],
                                    [0, 0, 0, 0, 0.1, 0, 0.000003, 0.9],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    ]

OWTransitionFromStateToStateProbality= [[0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 1, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0.6, 0, 0, 0, 0.5],
                                    [0, 0, 0, 0, 0.2, 0.02, 0.001, 0.9],
                                    [0, 0, 0, 0.05, 0, 0.25, 0.01, 0.85],
                                    [0, 0, 0, 0, 0.05, 0, 0.03, 0.8],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    [0, 0, 0, 0, 0, 0, 0, 0],
                                    ]