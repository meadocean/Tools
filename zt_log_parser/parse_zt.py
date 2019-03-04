#Parse Log file
import string
import re
import sys

SIDE_COMP_SMD_TH = 200
SIDE_COMP_TOP2_TH = 47
SIDE_COMP_MAX_TH = 10
FLAT_COMP_SMD_TH = 193
FLAT_COMP_TOP2_TH = 54
FLAT_COMP_MAX_TH = 11
SIDE_ABS_SMD_TH = 320
SIDE_ABS_TOP2_TH = 57
SIDE_ABS_MAX_TH = 16
FLAT_ABS_SMD_TH = 120
FLAT_ABS_TOP2_TH = 39
FLAT_ABS_MAX_TH = 7

FLAT_POS = 1
SIDE_POS = 2
MID_POS = 3

lineData=[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

def parse_raw_line(line, data):
    date=re.findall(r'\d+',line)
    values = line.split(',')
    values[0] = values[0][-2:]
    #print m
    cnt = 0
    for i in range(7):
        data[i]=int(date[i])
        cnt += 1
    for val in values:
        data[cnt] = int(val, 16)
        cnt += 1
    return cnt

def parse_analyze_data_line(line, data):
    date=re.findall(r'\d+',line)
    values = line.split(',')
    if values[0][-2] == ':':
        values[0] = values[0][-1]
    else:
        values[0] = values[0][-2:-1]
    #print date
    cnt = 0
    for i in range(6):
        data[i]=int(date[i])
        cnt += 1
    i = 0
    for val in values:
        if i < 3:
            data[cnt] = int(val, 16)
        else:
            data[cnt] = int(val, 10)
        i += 1
        cnt += 1
    return cnt

def parse_similarity_line(line, data):
    m=re.findall(r'\d+',line)
    #print m
    i=0
    for val in m:
        data[i]=int(val,10)
        i=i+1
    return i

def parse_rt_state_line(line, data):
    m=re.findall(r'\d+',line)
    #print m
    i=0
    for val in m:
        data[i]=int(val,10)
        i=i+1
    return i

def is_raw_data_line(line):
    return re.findall(r'RX: R\d+', line)

def is_analyzing_data_line(line):
    return re.findall(r'RX: @:', line)

def is_rt_state_line(line):
    return re.findall(r'RX: \$P:', line)

def is_similarity_data_line(line):
    return re.findall(r'RX: & ', line)

def is_same_raw_packet(r1,r2,r3,anaData,similarity,rtState):
    if len(r1) == 0 or len(r2) == 0 or len(r3) == 0 or len(anaData) == 0 or len(similarity) == 0 or len(rtState) == 0:
        return False
    delta = 0
    for i in range(0,5,1):
        delta += (r1[i]-r2[i])+(r1[i]-r3[i]+(r1[i]-anaData[i])+(r1[i]-similarity[i])+(r1[i]-rtState[i]))
    if delta == 0:
        return True
    return False

def print_raw_line(raw, channels, data, date, time, anaData, similarityData, rtState):
    temp = []
    temp += "%s/%s/%s\t%s:%s:%s\t"%(date[0],date[1],date[2],time[0],time[1],time[2])
    for i in range(channels):
        temp += "%s\t"%(data[i])
    raw += temp
    #print("Date:%s,%s"%(date,time))
    #print(anaData)
    #print(similarityData)
    #print(rtState)
    anaStr = "%s\t%s\t%s\t%s\t%s\t"%(anaData[6],anaData[7],anaData[8],anaData[9],anaData[10])
    raw += anaStr
    rtStateStr = "%s\t%s\t%s\t%s\t"%(rtState[7],rtState[8],rtState[9],rtState[6])
    raw += rtStateStr
    similartyStr = "%s\t%s\t%s\t%s"%(similarityData[6],similarityData[7],similarityData[9],similarityData[10])
    raw += similartyStr
    raw += "\n"
    return

def write_output(name, data):
    fp = open(name,'w+')
    fp.write("Date\tTime\tCh0\tCh1\tCh2\tCh3\tCh4\tCh5\tCh6\tCh7\tCh8\tCh9\tCh10\tCh11\tCh12\tCh13\tCh14\tCh15\tMin\tMean\tMax\tTop2\tSME\tHeight\tVoltage\tCharging\tPos\tRT Pos\tNew Pos\tSimilarity\tSimilarity Count\n")
    for line in data:
        fp.write(line)
        #print(str(data[i]))
    fp.close()
    return

rawData = []
rawOutput = []
analysisOut = []
R1 = []
R2 = []
R3 = []
Date = []
Time = []
anaData = []
rtState = []
similarityData = []

inputFile = open(sys.argv[1],'r')
lineCount = 0
for lines in inputFile.readlines():
    lineCount += 1
    #print("Line: %d"%lineCount)
    if is_raw_data_line(lines):
        parse_raw_line(lines,lineData)
        if lineData[6] == 1:
            R1 = lineData[:]
            #print(R1)
        elif lineData[6] == 2:
            R2 = lineData[:]
            #print(R2)
        elif lineData[6] == 3:
            R3 = lineData[:]
            #print(R3)
    if is_analyzing_data_line(lines):
        parse_analyze_data_line(lines,lineData)
        anaData = lineData[:]
        #print anaData
    if is_rt_state_line(lines):
        parse_rt_state_line(lines,lineData)
        rtState = lineData[:]
        #print rtState
    if is_similarity_data_line(lines):
        parse_similarity_line(lines,lineData)
        similarityData = lineData[:]
        #print similarityData

    if is_same_raw_packet(R1,R2,R3,anaData,similarityData,rtState):
        rawData = R1[7:13]
        rawData += R2[7:13]
        rawData += R3[7:11]
        Date = R1[0:3]
        Time = R1[3:6]
        print_raw_line(rawOutput, 16, rawData, Date, Time, anaData, similarityData, rtState)
        rawData = []
        Date = []
        Time = []
        anaData = []
        similarityData = []
        srtState = []
        R1 = []
        R2 = []
        R3 = []

#print rawData
#print rawOutput
write_output("test_out.txt", rawOutput)
