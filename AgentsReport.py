# Created May 2022 by Carlos Alba 
#requires Python 3.10 (conda activate py310)
# Create a report of shift(s) for given agent(s) for a date

import datetime,time,sys
from collections import deque

# run example: python3 AgentsReport.py queue_log 28/04/2022 PJSIP/user


# sys.arg[1] queue_log type file formated as 1628742620|NONE|NONE|NONE|QUEUESTART|  where first field is timestamp in Unix Epoch
#typically queue_log under /var/log/asterisk
#as: 1651496662|1651496662.49874|queuename|PJSIP/agent1|ADDMEMBER|
# sys.arg[2] date in dd/mm/yyyy format
# sys.arg[3] sys.arg[4] sys.arg[n]...agents name , as PJSIP/user1 ...AIX2/user2 ...       

#helpers
def convertToEpoch(date):
    #date in dd/mm/yyyy format
    #return date array  [start,end] in epoch 
    d = date.split('/')
    #y,m,d,0,0 , y,m,d,23,59
    return [int(datetime.datetime(int(d[2]),int(d[1]),int(d[0]),0,0,0).strftime('%s')),int(datetime.datetime(int(d[2]),int(d[1]),int(d[0]),23,59,59).strftime('%s'))]

def convertFromEpoch(epoch):
    #formar epoch to dd/mm/yyyy
    return time.strftime('%d/%m/%Y %H:%M:%S', time.localtime(epoch))

#Class
class agentStack:
  def __init__(self, name):
    self.name = name#agent name
    self.stack = deque()#dict of {event,timestamp}

  def add(self,event,timestamp):
    #self.stack.append(event,timestamp)
    match (len(self.stack)):
        case 0:
            if event == "ADDMEMBER":
                self.stack.append({'event':event,'timestamp':timestamp})
            if event == "REMOVEMEMBER":
                print("Warn 41: REMOVEMEMBER event before ADDMEMBER")#Can not REMOVEMEMBER on Empty Stack
                pass
        case 1:
            if event == "ADDMEMBER":
                print("Warn 44: Previous ADDMEMBER event")
                pass
            if event == "REMOVEMEMBER":
                stackElement= self.stack.pop()
                #print(stackElement)
                match stackElement['event']:
                    case "ADDMEMBER":
                        t1= int(timestamp)
                        t2= int(stackElement["timestamp"])
                        t = (t1-t2)/60
                        txt = "Agent {agent} had a shift from {start} for: {mins:.2f} mins."
                        #txt = "Turno de {agent} {start} -> {end} , duracion: {mins:.2f} mins."
                        print(txt.format(agent=self.name,start=convertFromEpoch(t2),end=convertFromEpoch(t1),mins=t))
                    case "REMOVEMEMBER":
                        pass
                    case _:
                        pass
        case _:
            print("Oops!")

#FIle management
def createTmp(src,tmp,date):
    #create tmp file with just date records 
    f = open(src,"r")
    tmp = open(tmp,"w+")
    e = convertToEpoch(date)
    c = 0
    for line in f:        
        timestamp = int(line.split("|")[0])
        if (timestamp >= e[0] and e[1] >= timestamp  ):
            c += 1
            tmp.write(line)
    print("Total ",date," records: ",c)
    f.close()
    tmp.close()
    return

def calculateAgent(file,agent):
    # return agent time from file
    f= open(file,"r")

    agentStackDict = {}
    for i in range(3,len(sys.argv)):
        agentStackDict[sys.argv[i]] = agentStack(name=sys.argv[i])
        
    for line in f:
        splittedLine = line.split("|")
        timestamp = splittedLine[0]
        agentName = splittedLine[3]
        event = splittedLine[4]        
        if agentName in agentStackDict.keys() and event in ("ADDMEMBER","REMOVEMEMBER"):
            agentStackDict[agentName].add(event=event,timestamp=timestamp)
    f.close()

def main():
    createTmp(sys.argv[1],"tmp",sys.argv[2])
    calculateAgent("tmp",sys.argv[3])

if __name__ == '__main__':
    main()