# -*- coding: utf-8 -*-

import os
import calculate_time
import json
import time

from math import *


logfile = open('log.drift.gps','w')

class Point:
    lat = 0;
    lon = 0;
    time = None;
    def __init__(self,la,lo,ctime):
        self.lat = la;
        self.lon = lo;
        self.time = ctime



def distance(lat1,lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)
    """
    # 将十进制度数转化为弧度
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine公式
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371 # 地球平均半径，单位为公里
    print str(c * r * 1000)+" km";
    return c * r * 1000


# input Lat_A 纬度A
# input Lng_A 经度A
# input Lat_B 纬度B
# input Lng_B 经度B
# output distance 距离(km)
def calcDistance(Lat_A, Lng_A, Lat_B, Lng_B):
    try:
        ra = 6378.140  # 赤道半径 (km)
        rb = 6356.755  # 极半径 (km)
        flatten = (ra - rb) / ra  # 地球扁率
        # print Lat_A,Lng_A,Lat_B,Lng_B
        rad_lat_A = radians(Lat_A)
        rad_lng_A = radians(Lng_A)
        rad_lat_B = radians(Lat_B)
        rad_lng_B = radians(Lng_B)
        pA = atan(rb / ra * tan(rad_lat_A))
        pB = atan(rb / ra * tan(rad_lat_B))
        xx = acos(sin(pA) * sin(pB) + cos(pA) * cos(pB) * cos(rad_lng_A - rad_lng_B))
        c1 = (sin(xx) - xx) * (sin(pA) + sin(pB)) ** 2 / cos(xx / 2) ** 2
        c2 = (sin(xx) + xx) * (sin(pA) - sin(pB)) ** 2 / sin(xx / 2) ** 2
        dr = flatten / 8 * (c1 - c2)
        distance = ra * (xx + dr)
        return distance
    except:
        logfile.write('zero '+str(Lat_A)+" "+str(Lng_A)+","+str(Lat_B)+str(Lng_B))
        return 0


def stringtoHour(str = ''):
    #将其转换为时间数组
    timeArray = time.strptime(str, "%Y-%m-%d %H:%M:%S")
    #转换为时间戳:
    timeStamp = int(time.mktime(timeArray))
    return  timeStamp/60.0/60.0


def printPoint(pointlist=[]):
    for i in pointlist:
        logfile.write("["+str(i.lat)+","+str(i.lon)+","+str(i.time)+","+"]\n")



#返回正确point对应的list
def checkdriftpoint(pointlist = []):

    printPoint(pointlist)

    marklist=[]
    returnlist = []
    for i in range(len(pointlist)):
        marklist.append(0)

    for i in range(len(pointlist)):
        logfile.write("F i="+str(i)+"\n")
        for j in range(i+1,len(pointlist)):
            # logfile.write(pointlist[i].time+' == '+pointlist[j].time+"\n")
            caltime = stringtoHour(pointlist[i].time)-stringtoHour(pointlist[j].time)
            caltime = fabs(caltime)
            if calculateDriftGps(pointlist[i].lat,pointlist[i].lon,pointlist[j].lat,pointlist[j].lon,caltime):
                logfile.write("i="+str(i)+" j="+str(j)+"\n")
                marklist[i]+=1
                marklist[j]+=1

    marklistresult = sorted(marklist)

    logfile.write(str(marklist))
    driftnum = marklistresult[len(marklistresult)-1]
    if driftnum == 0:
        driftnum = 11

    for i  in range(len(marklist)):
        if marklist[i] != driftnum:
            returnlist.append(i)
    logfile.write("-----"+str(returnlist)+"\n\n")
    return returnlist


# 计算飘逸点
def calculateDriftGps(lat_old,lon_old,lat,lon,caltime):
    if caltime == 0:
        return False
    if calcDistance(lat_old,lon_old,lat,lon)/caltime >= 300:
        return True
    return False


#处理11个点，写入返回的正常的点。
def handleReadBuffer(buffer,ofile):
    pointlist = []
    for line in buffer:
        s = json.loads(line)
        lon =  s['longitude_amap']
        lat =  s['latitude_amap']
        ctime = s['calculateDate']
        pointlist.append(Point(lat,lon,ctime))

    numlist = checkdriftpoint(pointlist)

    for i in numlist:
        #print 'f '+str(i)+ ' len(buffer)='+str(len(buffer))
        ofile.write(buffer[i]);
        # ofile.write('\n');
        #
        # positionDate = s['positionDate']
        # receiveDate  = s['receiveDate']
        # calculate_date = calculate_gps(receiveDate_old,positionDate_old,receiveDate,positionDate)
        # if calculate_date == '0000-00-00 00:00:00':
        #     continue
        #
        # receiveDate_old = receiveDate;
        # positionDate_old = positionDate;
        #
        # s['calculateDate'] = calculate_date;
        # content = json.dumps(s,ensure_ascii=False);
        # #print content
        # ofile.write(content.encode('utf-8'));
        # ofile.write('\n');


#读取文件内容处理，
def readFile(filepathname=''):
    ifile = open(filepathname,'r')
    receiveDate_old = ''
    positionDate_old = ''
    ofile = open(filepathname+'.gps','w')

    readBuffer = []
    for line in ifile:
        s = json.loads(line)
        ctime = s['calculateDate']
        if calculate_time.excludeDate(ctime):
            continue;
        if len(readBuffer) == 11:
            handleReadBuffer(readBuffer,ofile)
            readBuffer = []

        readBuffer.append(line)

    if len(readBuffer)!=0:
        #再执行一次
        handleReadBuffer(readBuffer,ofile)
        readBuffer=[]

    ofile.close();




def check_calculate_time(filepathname=''):
    ifile = open(filepathname,'r')
    calculateDate_old = '2016-01-01 00:00:00'
    line_old = ''
    ofile = open('check_calculate_time.log','a')
    ofile.write(filepathname.encode('utf-8')+"\n")
    i = 0;
    for line in ifile:
        i+=1

        s = json.loads(line)
        calculateDate = s['calculateDate']
        receiveDate = s['receiveDate']
        positionDate = s['positionDate']
        if calculate_time.excludeDate(calculateDate) or calculate_time.excludeDate(receiveDate) or calculate_time.excludeDate(positionDate):
            continue

        if i == 1:
            calculateDate_old = calculateDate
            line_old = line
            continue

        if stringtoHour(calculateDate)-stringtoHour(calculateDate_old) >=12:
            ofile.write(line_old);
            ofile.write(line+"\n");

        line_old = line
        calculateDate_old = calculateDate;

    ofile.close();


def check_gps_gprs(filepathname=''):
    ifile = open(filepathname,'r')
    calculateDate_old = '2016-01-01 00:00:00'
    receiveDate_old = ''
    positionDate_old = ''
    deviceNo_old = ''
    line_old = ''

    ofile = open('check_gps_gprs.log','a')
    #ofile.write(filepathname.encode('utf-8')+"\n")
    i = 0;
    gprslosecount = 0
    gpslosecount = 0
    for line in ifile:
        i+=1

        s = json.loads(line)
        calculateDate = s['calculateDate']
        receiveDate = s['receiveDate']
        positionDate = s['positionDate']
        deviceNo_old = s['deviceNo']
        if calculate_time.excludeDate(calculateDate) or calculate_time.excludeDate(receiveDate) or calculate_time.excludeDate(positionDate):
            continue

        if i == 1:
            calculateDate_old = calculateDate
            receiveDate_old = s['receiveDate']
            positionDate_old = s['positionDate']
            line_old = line
            continue

        if stringtoHour(receiveDate)-stringtoHour(receiveDate_old) >=24:
            gprslosecount+=1
        if stringtoHour(positionDate)-stringtoHour(positionDate_old) >=24:
            gpslosecount+=1


        line_old = line
        calculateDate_old = calculateDate;
        receiveDate_old = receiveDate;
        positionDate_old = positionDate
    print filepathname.split(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/')[1].split(u'_20160420000000-20160726000000.txt.amap.sort.calculate_time')[0]
    carnum = filepathname.split(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/')[1].split(u'_20160420000000-20160726000000.txt.amap.sort.calculate_time')[0]
    print carnum.encode('utf-8')+" GPRS lose bigger 24 hours " +str(gprslosecount)+"---"+"GPS lose bigger than 24 hours "+str(gpslosecount)
#    ofile.write(carnum.encode('utf-8')+" GPRS lose bigger 24 hours " +str(gprslosecount)+"---"+"GPS lose bigger than 24 hours "+str(gpslosecount) + "\n\n")
    ofile.write(carnum.encode('utf-8')+","+str(deviceNo_old)+"," +str(gprslosecount)+","+str(gpslosecount) + "\n")

    ofile.close();

# #读取文件内容处理，
# def check_gps_gprs_distance(filepathname=''):
#     ifile = open(filepathname,'r')
#     calculateDate_old = '2016-01-01 00:00:00'
#     receiveDate_old = ''
#     positionDate_old = ''
#     deviceNo_old = ''
#
#     line_old = ''
#
#     ofile = open('check_gps_gprs.log','a')
#     #ofile.write(filepathname.encode('utf-8')+"\n")
#     i = 0;
#     gprslosecount = 0
#     gpslosecount = 0
#     deviceNo=''
#     for line in ifile:
#         i+=1
#         print line
#         s = json.loads(line)
#         calculateDate = s['calculateDate']
#         receiveDate = s['receiveDate']
#         positionDate = s['positionDate']
#         deviceNo = s['deviceNo']
#         print s
#         if calculate_time.excludeDate(calculateDate) or calculate_time.excludeDate(receiveDate) or calculate_time.excludeDate(positionDate):
#             continue
#
#         if i == 1:
#             calculateDate_old = calculateDate
#             receiveDate_old = s['receiveDate']
#             positionDate_old = s['positionDate']
#             deviceNo_old = s['deviceNo']
#             line_old = line
#             continue
#
#         if stringtoHour(receiveDate)-stringtoHour(receiveDate_old) >=24:
#             gprslosecount+=1
#         if stringtoHour(positionDate)-stringtoHour(positionDate_old) >=24:
#             gpslosecount+=1
#
#
#         line_old = line
#         calculateDate_old = calculateDate;
#         receiveDate_old = receiveDate;
#         positionDate_old = positionDate
#         deviceNo_old = deviceNo;
#     print filepathname.split(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/')[1].split(u'_20160420000000-20160726000000.txt.amap.sort.calculate_time')[0]
#     carnum = filepathname.split(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/')[1].split(u'_20160420000000-20160726000000.txt.amap.sort.calculate_time')[0]
#     print carnum.encode('utf-8')+" GPRS lose bigger 24 hours " +str(gprslosecount)+"---"+"GPS lose bigger than 24 hours "+str(gpslosecount)
# #    ofile.write(carnum.encode('utf-8')+" GPRS lose bigger 24 hours " +str(gprslosecount)+"---"+"GPS lose bigger than 24 hours "+str(gpslosecount) + "\n\n")
#     ofile.write(carnum.encode('utf-8')+","+str(deviceNo)+"," +str(gprslosecount)+","+str(gpslosecount) + "\n")
#
#     ofile.close();







def readFileList():
    l = calculate_time.GetFileList('../data/金融车辆最新截至数据2016-07-26/2016-07-26',[],['.amap.sort.calculate_time'],['gps','.rar'])

    #l = [u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/苏A1CY82_20160420000000-20160726000000.txt.amap.sort.calculate_time']
    for e in l:
        print e
        #readFile(e);
        #check_calculate_time(e)
        check_gps_gprs(e)


#仅仅统计24小时没有上报的GPS和GPRS记录
if __name__ == '__main__':
    # ofile = open('check_calculate_time.log','w')
    # ofile.close()
    # pass
    ofile = open('check_gps_gprs.log','w')
    ofile.write('\xEF\xBB\xBF');

    ofile.write("车牌号,deviceNo,GPRS丢失大于24小时次数,GPS丢失大于24小时次数\n")
    ofile.close()
    readFileList()
    # caltime = stringtoHour('2016-07-11 16:44:49')-stringtoHour('2016-07-11 16:46:48')
    # caltime = fabs(caltime)
    # print caltime
    # print calculateDriftGps(32.2342260178,118.772936386,32.0647340271,118.634438707,caltime)
    # # print distance(30.6357442057,104.080202019,30.634359278,104.077468276)
    # # print calcDistance(30.6357442057,104.080202019,30.634359278,104.077468276)
    # print calcDistance(32.2342260178,118.772936386,32.0647340271,118.634438707)/caltime
    # # print calculate_time.excludeDate('2016-04-08 14:27:39')
