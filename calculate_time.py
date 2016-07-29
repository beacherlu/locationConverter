# -*- coding: utf-8 -*-
import json
import requests
import math
import json
import os




#时间融合
#
#如果两个时间都正常，连续上传，则以positionDate为calculateDate
#如果positionDate时间不变，receiveDate连续变化，则以receiveDate为calculateDate
# 如果positionDate连续变化，receiveDate不变，则以positionDate为calculateDate
#如果positionDate时间不变，receiveDate不变，记录信息报错。


logfile = open('logs','w')


#4月20号的点直接抛弃
def excludeDate(date=''):
    if cmp(date, '2016-04-20 00:00:00')<0 or cmp(date, '2026-04-20 00:00:00')>0:
        logfile.write("date = "+date+ ' excludeDate True')
        return True
    else:
        #print date+' excludeDate False'
        return False


def calculate_time(receiveDate_old,positionDate_old,receiveDate,positionDate):
    if excludeDate(receiveDate_old) or excludeDate(positionDate_old) or excludeDate(receiveDate) or excludeDate(positionDate):
        # print '---',receiveDate_old,receiveDate,positionDate_old,positionDate
        logfile.write('error 5\n')
        return '0000-00-00 00:00:00'
    if positionDate != positionDate_old  and receiveDate != receiveDate_old:
        logfile.write('situation 1 \n')
        return positionDate
    elif positionDate == positionDate_old and receiveDate != receiveDate_old:
        logfile.write('situation 2\n')
        return receiveDate
    elif positionDate != positionDate_old and receiveDate == receiveDate_old:
        logfile.write('situation 3\n')
        return positionDate
    elif positionDate == positionDate_old and receiveDate == receiveDate_old:
        logfile.write('error 4\n')
        return '0000-00-00 00:00:00'


def sortFileContent():
    l = GetFileList('../data/金融车辆最新截至数据2016-07-26/2016-07-26',[],['.amap'],[])
    for i in l:
        print 'sort ' + i;
        contentlist = []
        ifile = open(i,'r')
        for line in ifile:
            s = json.loads(line)
            positionDate = s['positionDate']
            receiveDate  = s['receiveDate']
            contentlist.append(str(positionDate)+str(receiveDate)+'value'+line)
        ifile.close()
        contentlist = sorted(contentlist)

        ofile=open(i+".sort",'w')

        for i in contentlist:
            ofile.write(i.split('value')[1])
        ofile.close()


#读取文件内容处理，并且加入新的字段。
def readFile(filepathname=''):
    ifile = open(filepathname,'r')
    receiveDate_old = '123'
    positionDate_old = '456'
    ofile = open(filepathname+'.calculate_time','w')

    linenum = 0;

    for line in ifile:

        linenum+=1;
        if linenum == 1:
            s = json.loads(line)
            positionDate_old = s['positionDate']
            receiveDate_old  = s['receiveDate']
            continue

        s = json.loads(line)

        lon =  s['longitude_amap']
        lat = s['latitude_amap']
        positionDate = s['positionDate']
        receiveDate  = s['receiveDate']

        calculate_date = calculate_time(receiveDate_old,positionDate_old,receiveDate,positionDate)

        receiveDate_old = receiveDate;
        positionDate_old = positionDate;

        if calculate_date == '0000-00-00 00:00:00':
            continue

        s['calculateDate'] = calculate_date;
        content = json.dumps(s,ensure_ascii=False);
        #print content
        ofile.write(content.encode('utf-8'));
        ofile.write('\n');
    ofile.close();


#待完成。。
def GetFileList(dir,fileList,includefilename,excludefilename):
    l = os.listdir(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26')
    for e in l:
        #print e.encode('utf-8')
        flag = True
        for j in excludefilename:
            if e.find(j) != -1:
                flag = False
                break
        if not flag:
            continue

        for i in includefilename:
            if e.find(i) != -1:
                fileList.append(dir.decode('utf-8')+"/"+e)
                break
        #fileList.append(dir.decode('utf-8')+"/"+e);
    return fileList


# def GetFileList(dir, fileList):
#
#     l = os.listdir(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26')
#     for e in l:
#         #print e.encode('utf-8')
#         if e.find('amap') == -1:
#             continue;
#         if e.find('time') != -1:
#             continue;
#         if e.find('.sort') != -1:
#             fileList.append(dir.decode('utf-8')+"/"+e);
#             continue;
#
#
#     return fileList


#只保留原始数据，删除中间数据。待完成
def initFile():
    pass


def readFileList():
    l = GetFileList('../data/金融车辆最新截至数据2016-07-26/2016-07-26',[],['.amap.sort'],['rar','time'])
    for e in l:
        print e
        readFile(e);


if __name__ == '__main__':
    #sortFileContent()
    #readFile(u'../data/金融车辆最新截至数据2016-07-26/2016-07-26/川A0PV09_20160420000000-20160726000000.txt')
    readFileList();
    #print excludeDate('2016-07-07 11:57:14 ')

