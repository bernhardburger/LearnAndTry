
import SimConfig as conf
import InfectionAgent as IA
import random
import sys
import math
import time
import matplotlib.pyplot as plt

numHealthy = 0
numInfected = 0
numInfectious = 0
numSick = 0
numHospitalized = 0
numCritical = 0
numDeceased = 0
numRecovered = 0


def createFamilyRelations (thisdaylist,allrelationslist):
    familystartindex = 0
    baseNumber = conf.FamilyConnections
    variation = conf.FamilyConnectionVariation
    while (familystartindex < len(thisdaylist)):
        numberofrelation = random.randint(baseNumber - variation, baseNumber + variation)

        if numberofrelation > (len(thisdaylist)-familystartindex):
            numberofrelation = len(thisdaylist)-familystartindex
        familyMemberIndex = familystartindex # where does the family start
        relationtobuild = numberofrelation
        while (relationtobuild > 1):
            for k in range(relationtobuild - 1):
                nr1 = IA.Relation(thisdaylist[familyMemberIndex].AgentID,
                            thisdaylist[familyMemberIndex + k + 1].AgentID,
                            conf.FamilyExposureTime, 'F')
                nr2 = IA.Relation(thisdaylist[familyMemberIndex+k+1].AgentID,
                                  thisdaylist[familyMemberIndex].AgentID,
                                  conf.FamilyExposureTime, 'F')
                thisdaylist[familyMemberIndex].relations.append(nr1)
                thisdaylist[familyMemberIndex + k +1].relations.append(nr2)
                allrelationslist.append(nr1)
                allrelationslist.append(nr2)


            relationtobuild -= 1
            familyMemberIndex +=1
        familystartindex = familystartindex + numberofrelation # new offset
    return thisdaylist, allrelationslist

def createWorkRelations(thisdaylist, allrelationslist):
    agentIterator = iter(thisdaylist)
    baseNumber = conf.WorkplaceConnection
    variation = conf.WorkplaceConnectionVariation
    while True:
        try:
            agent = next(agentIterator)
            numberofrelation = random.randint(baseNumber - variation,baseNumber + variation)
            fromAgentID = agent.AgentID
            for i in range(numberofrelation):
                targetID = random.randint(0, conf.NumberofAgents-1)
                if targetID == fromAgentID:
                    targetID = random.randint(0, conf.NumberofAgents)
                nr1 = IA.Relation(thisdaylist[fromAgentID].AgentID,
                                  thisdaylist[targetID].AgentID,
                                  conf.WorkplaceExposureTime, 'W')
                nr2 = IA.Relation(thisdaylist[targetID].AgentID,
                                  thisdaylist[fromAgentID].AgentID,
                                  conf.WorkplaceExposureTime, 'W')
                thisdaylist[fromAgentID].relations.append(nr1)
                thisdaylist[targetID].relations.append(nr2)
                allrelationslist.append(nr1)
                allrelationslist.append(nr2)

        except StopIteration:
            break
        except IndexError as err:
            print (err.args)
            Raise




def createExternalRelations(thisdaylist, allrelationslist):
    agentIterator = iter(thisdaylist)
    baseNumber = conf.ExternalConnnection
    variation = conf.ExternalConnectionVariation
    while True:
        try:
            agent = next(agentIterator)
            numberofrelation = random.randint(baseNumber - variation, baseNumber + variation)
            fromAgentID = agent.AgentID
            for i in range(numberofrelation):
                targetID = random.randint(0, conf.NumberofAgents - 1)
                if targetID == fromAgentID:
                    targetID = random.randint(0, conf.NumberofAgents)
                nr1 = IA.Relation(thisdaylist[fromAgentID].AgentID,
                                  thisdaylist[targetID].AgentID,
                                  conf.ExternalExposureTime, 'E')
                nr2 = IA.Relation(thisdaylist[targetID].AgentID,
                                  thisdaylist[fromAgentID].AgentID,
                                  conf.ExternalExposureTime, 'E')
                thisdaylist[fromAgentID].relations.append(nr1)
                thisdaylist[targetID].relations.append(nr2)
                allrelationslist.append(nr1)
                allrelationslist.append(nr2)

        except StopIteration:
            break
        except IndexError as err:
            print(err.args)
            Raise




def CreateBaseLists (size):
    thisdaylist = []
    for i in range (size):
        newagent = IA.Agent(i)
        thisdaylist.append(newagent)
    return thisdaylist


def seed(numberInfected,thisdaylist):
    for i in range (numberInfected):
        index = random.randint(0, conf.NumberofAgents-1)
        thisdaylist[index].newState = conf.AgentHealthState[1]

def simulateDay(agentlist, relationlist):
    conf.daycounter+=1 #hässliche Zirkuläre Abh
    relation = iter(relationlist)
    #infection
    while True:
        try:
           # random.seed(time.time() * 1000000)
            rel = next(relation)
            statefrom = agentlist[rel.fromID].healthState
            stateto = agentlist[rel.toID].healthState

            if statefrom not in ('healthy', 'deceased', "recovered" ) and stateto in ('healthy') :
                if statefrom in ('infectious'):
                    probality = rel.exposureTime * conf.transmission_rate * conf.getWorkplaceExposureModificator()
                elif statefrom in ('sick'):
                    probality = rel.exposureTime * conf.transmission_rate * conf.sick_transmssion_reduction* conf.getWorkplaceExposureModificator()
                elif statefrom in ('hostpitalized'):
                    probality = rel.exposureTime * conf.transmission_rate * conf.hospitalized_transmission_reduction* conf.getWorkplaceExposureModificator()
                elif statefrom in ('critical'):
                    probality = rel.exposureTime * conf.transmission_rate * conf.critical_transmission_reduction* conf.getWorkplaceExposureModificator()
                else:
                    probality = rel.exposureTime * conf.transmission_rate* conf.getWorkplaceExposureModificator()
                if random.random() < probality:
                    agentlist[rel.toID].newState = conf.AgentHealthState[1]
                    agentlist[rel.toID].lastChange = -1
        except StopIteration:
            break

    #StateChanges
    agentIter = iter(agentlist)
    while True:
     #   random.seed(time.time() * 1000000)
        try:
            agent = next(agentIter)
            statefrom = agent.healthState
            changeTime = agent.lastStateChange
            mintimevector = conf.TransitionFromStateToStateDaysMin[conf.IndexLookUP [statefrom]]
            maxtimevector = conf.TransitionFromStateToStateDaysMax[conf.IndexLookUP [statefrom]]
            if conf.getOverwhelmed() == True:
                changevector = conf.TransitionFromStateToStateProbality[conf.IndexLookUP[statefrom]]
            else:
                changevector = conf.OWTransitionFromStateToStateProbality[conf.IndexLookUP [statefrom]]
            changeProb= random.random()
            toStateIndex = calculateToStateIndex(changeProb, changevector)
            if toStateIndex == -1:
               pass
               """ agent.newState = agent.healthState"""
            elif agent.lastStateChange > mintimevector[toStateIndex]:
                agent.newState = conf.AgentHealthState[toStateIndex]
                agent.lastStateChange = -1
            else:
                pass
                """agent.newState = agent.healthState"""
        except StopIteration:
            break
    # update States
    for agent in agentlist:
        agent.healthState = agent.newState
        #register for measurement
        daydiff = conf.daycounter - agent.testDay
        if (conf.daycounter > conf.measurementStart):
            if agent.healthState in ('sick', 'hospitalized', 'critical') and agent.registeredForTesting == False \
                     and daydiff > conf.minTestinterval:
                conf.measurementPipeline.append(agent)
                agent.registeredForTesting = True
                agentrelation = iter(agent.relations)
                cnt=0
                while True:
                    try:
                        rel= next(agentrelation)
                        if rel.relationType in ('F','W'):
                            if agentlist[rel.toID].registeredForTesting == False and \
                                    agentlist[rel.toID].testResult == False and\
                                    (conf.daycounter - agentlist[rel.toID].testDay) > conf.minTestinterval:
                                conf.measurementPipeline.append(agentlist[rel.toID])
                                cnt += 1
                                agentlist[rel.toID].registeredForTesting = True

                    except StopIteration:
                        break
        agent.lastStateChange += 1
    # simulate measurements
    if (conf.daycounter > conf.measurementStart):
        positiveCount = 0

        pipelineLength = len(conf.measurementPipeline)
        #print(pipelineLength)
        if pipelineLength <= conf.measurementCapacity:
            measurecount = pipelineLength
        else:
            measurecount = conf.measurementCapacity
        for i in range(measurecount):
            agent = conf.measurementPipeline.pop()
            conf.numberTestedSet.add(agent.AgentID)
            agent.testDay = conf.daycounter
            if agent.healthState not in ('healthy', "recovered"):
                agent.testResult = True
                positiveCount +=1
            else:
                agent.testResult = False

        #print(measurecount,positiveCount)



    return agentlist, relationlist

def count_and_print_stats(thisdaylist,day):

    stats = [0 for _ in range (len(conf.AgentHealthState))]
    measure = [conf.daycounter,0,0,0,0,0,0] #day, pos. test, neg test, all test, pos percentage all test, ppl tested, percentage ppl
    if day == 0:
        pass
    for agent in thisdaylist:
        index = conf.IndexLookUP[agent.healthState]
        stats[index] +=1



    percentvector = [conf.daycounter]+list(map(percentage, stats))
    conf.setOverwhelmed(percentvector[6])
    conf.resultdataframe.append(percentvector)
    for agent in thisdaylist:
        if agent.testDay > 0:
            if agent.testResult == True:
                measure[1] +=1
            else:
                measure[2] +=1
    measure[3] += (measure[1]+measure[2])
    if measure[3] > 0:
        measure[4] = measure[1]/measure[3]*100
    else:
        measure[4] = 0
    measure[5] = len(conf.numberTestedSet)
    if measure[5] > 0:
        measure[6] = measure[1]/measure[5]*100
    else:
        measure[6] = 0
    conf.measureResultsDataFrame.append(measure)
    print(stats,percentvector,measure)


def percentage(x):
    return x/conf.NumberofAgents*100

def getcolumn(aList, columnindex):
    column =[]
    for i in range(len(aList)):
        column.append(aList[i][columnindex])
    return column

def calculateToStateIndex(changeProb, changevector):
    lowlimit = 1  # shit magic number
    toState = -1
    for i in range(len(changevector)):
        if changeProb < changevector[i] and changevector[i] <= lowlimit:
            lowlimit = changevector[i]
            toState = i
    return toState

def print_header():
    print("Number of Agents"+ str(conf.NumberofAgents))
    print("Number of Iterations" + str(conf.simulationDays))
    print("Family Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.FamilyConnections),
                                                                        str(conf.FamilyConnectionVariation),
                                                                        str(conf.FamilyExposureTime)))

    print("Work Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.WorkplaceConnection),
                                                                        str(conf.WorkplaceConnectionVariation),
                                                                        str(conf.WorkplaceExposureTime)))
    print("Ext Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.ExternalConnnection),
                                                                      str(conf.ExternalConnectionVariation),
                                                                      str(conf.ExternalExposureTime)))
    print("Infection/Transmission Factor {}".format(str(conf.transmission_rate)))

def print_results():
    print("Number of Agents"+ str(conf.NumberofAgents))
    print("Number of Iterations" + str(conf.simulationDays))
    print("Family Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.FamilyConnections),
                                                                        str(conf.FamilyConnectionVariation),
                                                                        str(conf.FamilyExposureTime)))

    print("Work Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.WorkplaceConnection),
                                                                        str(conf.WorkplaceConnectionVariation),
                                                                        str(conf.WorkplaceExposureTime)))
    print("Ext Connections/Variations/Exposuere: {}  {}  {}".format(str(conf.ExternalConnnection),
                                                                      str(conf.ExternalConnectionVariation),
                                                                      str(conf.ExternalExposureTime)))
    print("Infection/Transmission Factor {}".format(str(conf.transmission_rate)))
    print('Lockdown Start/End: {} / {}'.format(str(conf.cutoffday),str(conf.cutoffday2)))

    print('Lockdown')


def plot():
    x = getcolumn(conf.resultdataframe,0)
    y1 = getcolumn(conf.resultdataframe,1)
    y2 = getcolumn(conf.resultdataframe, 2)
    y3 = getcolumn(conf.resultdataframe, 3)
    y4 = getcolumn(conf.resultdataframe, 4)
    y5 = getcolumn(conf.resultdataframe, 5)
    y6 = getcolumn(conf.resultdataframe, 6)
    y7 = getcolumn(conf.resultdataframe, 7)
    y8 = getcolumn(conf.resultdataframe, 8)
    lbl =['infected','infectious','sick','hospitalized','critical','deceased','recovered']
    fig, ax = plt.subplots()
    ax.stackplot(x,y2,y3,y4,y5,y6,y7,y8, labels=lbl)
    ax.legend(loc='upper left')
    plt.show()
    fig2, ax2 = plt.subplots()
    x = getcolumn(conf.measureResultsDataFrame,0)
    y1 = getcolumn(conf.measureResultsDataFrame,3)
    y2 = getcolumn(conf.measureResultsDataFrame,1)
    y3 = getcolumn(conf.measureResultsDataFrame, 4)
    lbl2 =['#Tests', '#positive Tests']
    lbl3 = ['positive Percentage']
    ax2.plot(x,y1,y2)
    ax3 = ax2.twinx()
    ax3.plot(x,y3,'g')
    plt.show()

def intermediateplot(thisdaylist):
    axislength = math.ceil(math.sqrt(conf.NumberofAgents))
    xa =[]
    ya =[]
    color =[]
    for x in range(axislength):
        for y in range (axislength):
            if (x*axislength+y) >= conf.NumberofAgents:
                break
            xa.append(x)
            ya.append(y)
            if thisdaylist[(x*axislength+y)].healthState == 'healthy':
                col = 'w'
            elif thisdaylist[(x*axislength+y)].healthState == 'deceased':
                col = 'k'
            elif thisdaylist[(x*axislength+y)].healthState == 'recovered':
                col = 'g'
            elif thisdaylist[(x*axislength+y)].healthState == 'infected':
                col = 'b'
            elif thisdaylist[(x*axislength+y)].healthState == 'infectous':
                col = 'c'
            elif thisdaylist[(x * axislength + y)].healthState == 'sick':
                col = 'm'
            elif thisdaylist[(x * axislength + y)].healthState == 'hospitalized':
                col = 'r'
            else:
                col = 'purple'
            color.append(col)
    fig2, ax2 = plt.subplots()
    plt.scatter(xa,ya,c=color)
    plt.show()

def main():
    global numHealthy
    numHealthy = conf.NumberofAgents
    thisdaylist = CreateBaseLists(conf.NumberofAgents)
    allRelationList =[]
    print_header()
    createFamilyRelations(thisdaylist, allRelationList)
    print(len(allRelationList))
    createWorkRelations(thisdaylist,allRelationList)
    print(len(allRelationList))
    createExternalRelations(thisdaylist, allRelationList)
    print(len(allRelationList))
    seed(1, thisdaylist)

    for i in range(conf.simulationDays):
        thisdaylist,allRelationList = simulateDay(thisdaylist,allRelationList)
        # print out
        random.seed(time.time()*1000000)
        count_and_print_stats(thisdaylist,i)
       # if (conf.daycounter%50 == 0):
       #     intermediateplot(thisdaylist)
    plot()
    print_results()

if __name__ == "__main__":
    main()