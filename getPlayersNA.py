#/bin/python3
from threading import Thread
import asyncio, aiohttp, json

import time, datetime, queue
import numpy as np
import sortedcontainers

import pymysql

from RateLimiter import RateLimiterManager


timeBegin = time.mktime(datetime.datetime.utcnow().timetuple())

listMatchId = sortedcontainers.SortedSet()
listAccountId = sortedcontainers.SortedSet()
listAccountId.add(208543788)


rl = RateLimiterManager()

rl.updateApplicationLimit(10,3000)
rl.updateApplicationLimit(600,180000)

rl.displayMethodsLimit()

def callLogger(id,queueLogCalls):
    connection = pymysql.connect(host='localhost',
                                 user='user',
                                 password='pass',
                                 db='db',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection.cursor() as cursor:
        i = 0
        while True:
            i += 1
            request = queueLogCalls.get(True)
            
            if request is None:
                queueLogCalls.put(None)
                connection.commit()
                print("end call logger")
                break

            sql = "INSERT IGNORE INTO `requests_na` (`url`,`code`,`timestamp_sent`,`timestamp`,`X-App-Rate-Limit`,`X-App-Rate-Limit-Count`,`X-Method-Rate-Limit`,`X-Method-Rate-Limit-Count`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql,(request['url'],request['status'],request['time_sent'],request['time'],request['AppLimit'],request['AppCount'],request['MethodLimit'],request['MethodCount']))
            
            if i == 1000:
                i = 0
                connection.commit()
            
            
def saveAccounts(id,queueAccountSave):
    connection = pymysql.connect(host='localhost',
                                 user='user',
                                 password='pass',
                                 db='db',
                                 cursorclass=pymysql.cursors.DictCursor)
    
    with connection.cursor() as cursor:
        i = 0
        while True:
            i += 1
            
            request = queueAccountSave.get()
            
            if request is None:
                queueAccountSave.put(None)
                connection.commit()
                print("end account saver")
                break

            sql = "INSERT IGNORE INTO `accountId_na` VALUES (%s, %s, %s)"
            cursor.execute(sql,(request['accountId'],request['summonerId'],request['platformId']))
            if i == 1000:
                i = 0
                connection.commit()


async def fetch(session, url, queueLogCalls):
    callTime = int(time.mktime(datetime.datetime.utcnow().timetuple()))
    try:
        response = await session.request('GET', url)
    except Exception as e:
        queueLogCalls.put_nowait({"url":url,"status":408,"time":callTime,"AppLimit":None,"AppCount":None,"MethodLimit":None,"MethodCount":None})
        print(e)
        return None
    try:
        if not "Date" in response.headers:
            print("No date")
            print(response)
            return None
        callReceived = int(time.mktime(datetime.datetime.strptime(response.headers['Date'], '%a, %d %b %Y %H:%M:%S GMT').timetuple()))
        queueLogCalls.put_nowait({"url":url,"status":response.status,"time_sent":callTime,"time":callReceived,"AppLimit":response.headers['X-App-Rate-Limit'],"AppCount":response.headers['X-App-Rate-Limit-Count'],"MethodLimit":response.headers['X-Method-Rate-Limit'],"MethodCount":response.headers['X-Method-Rate-Limit-Count']})
        return response
    except:
        queueLogCalls.put_nowait({"url":url,"status":response.status,"time_sent":callTime,"time":callReceived,"AppLimit":None,"AppCount":None,"MethodLimit":None,"MethodCount":None})
        return response



async def matchlistCaller(queueLogCalls, queueAccountId, queueMatchId, lockMatchlist, lockPause):
    global listMatchId
    async with aiohttp.ClientSession() as session:
        while True:
            
            #Get accountId from queue
            accountId = await queueAccountId.get()
            #print("accountId : " + str(queueAccountId.qsize()))
            #Leave if no accountId left
            if accountId is None:
                await queueAccountId.put(None)
                break
            
            #Get a token for matchlist from rate limiter
            token = await rl.getToken("matchlist")
            
            #Call matchlist with accountId
            url = "https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/"+str(accountId)+"?&queue=420&beginTime=1520431270000&api_key=RGAPI-0000"
            data = await fetch(session, url, queueLogCalls)
            
            limits = getLimits(data.headers)
            await rl.getBack("matchlist", token, int(time.mktime(datetime.datetime.strptime(data.headers['Date'], '%a, %d %b %Y %H:%M:%S GMT').timetuple())), limits)
            
            if data == None:
                await queueAccountId.put(accountId)
            
            
            #If server error or rate limit, wait and put the accountId in the queue again
            elif data.status in [500,502,503,504]:
                await asyncio.sleep(1)
                await queueAccountId.put(accountId)
            elif data.status == 429:
                print(data.headers)
                await asyncio.sleep(1)
                await queueAccountId.put(accountId)
            #If 403, quit
            elif data.status == 403:
                "Critical 403 error detected"
                break
            elif data.status == 200:
                    
                response = json.loads(await data.text())
                
                #If at least one match in the list
                if response['totalGames'] > 0:
                    #Get all the matchIds of the list
                    matchIds = []
                    for match in response['matches']:
                        if match['platformId']=="NA1":
                            matchIds.append(match['gameId'])
                        
                    #Lock the global matchlist, find the new matchIds and add them to the global list
                    with await lockMatchlist:
                        matchlist = [x for x in matchIds if x not in listMatchId]
                        for m in matchlist:
                            listMatchId.add(m)
                    
                    #Put the new matchIds in the queue
                    for i in matchlist:
                        await queueMatchId.put(i)
                    #print("end put")
                    
                    
async def matchCaller(queueLogCalls, queueAccountId, queueMatchId, queueAccountSave, lockAccountlist, lockPause):
    global listAccountId
    async with aiohttp.ClientSession() as session:
        while True:
            
            #Get accountId from queue
            matchId = await queueMatchId.get()
            #print("matchId : " + str(queueMatchId.qsize()))
            
            #Leave if no accountId left
            if matchId is None:
                await queueMatchId.put(None)
                break
            
            #Get a token for matchlist from rate limiter
            token = await rl.getToken("match")
            
            #Call matchlist with accountId
            url = "https://na1.api.riotgames.com/lol/match/v3/matches/"+str(matchId)+"?api_key=RGAPI-0000"
            data = await fetch(session, url, queueLogCalls)
            
            limits = getLimits(data.headers)
            await rl.getBack("match", token, int(time.mktime(datetime.datetime.strptime(data.headers['Date'], '%a, %d %b %Y %H:%M:%S GMT').timetuple())), limits)
            
            if data == None:
                await queueMatchId.put(matchId)
            
            #If server error or rate limit, wait and put the accountId in the queue again
            elif data.status in [500,502,503,504]:
                await asyncio.sleep(1)
                await queueMatchId.put(matchId)
            #print headers for 429
            elif data.status == 429:
                print(data.headers)
                await asyncio.sleep(1)
                await queueMatchId.put(matchId)
            #If 403, quit
            elif data.status == 403:
                "Critical 403 error detected"
                break
            elif data.status == 200:
                    
                response = json.loads(await data.text())
                
                participants = []
                
                for p in (response['participantIdentities']):
                    if p['player']['currentPlatformId'] == "NA1":
                        if 'summonerId' in p['player']:
                            participants.append({"accountId":p['player']['currentAccountId'],"summonerId":p['player']['summonerId'],"platformId":p['player']['currentPlatformId']})
                        else:
                            print("No summonerId")
                            print(matchId)
                            print(p['player'])
                            participants.append({"accountId":p['player']['currentAccountId'],"summonerId":0,"platformId":p['player']['currentPlatformId']})
                
                with await lockAccountlist:
                    participantslist = [x for x in participants if x['accountId'] not in listAccountId]
                    for p in participantslist:
                        listAccountId.add(p['accountId'])
                    
                #Put the new accountIds in the queue
                for i in participantslist:
                    await queueAccountId.put(i['accountId'])
                    queueAccountSave.put(i)
                    
                '''try:
                    mongoTable.insert_one(response);
                except pymongo.errors.DuplicateKeyError:
                    pass'''
                        
                
                
    
#Master checking if there is still requests or all have been crawled and tells to stop
async def master(queueLogCalls, queueAccountId, queueMatchId, lockPause):
    global listMatchId
    global listAccountId
    
    while True:
        await asyncio.sleep(10)
        print("Matchs : " + str(len(listMatchId)) + " / Accounts : " + str(len(listAccountId)))
        print("Matchs queue : " + str(len(queueMatchId._queue)) + " / Account queue : " + str(len(queueAccountId._queue))+ " / Logs queue : " + str(queueLogCalls.qsize()))
        
        
        if len(queueMatchId._queue) == 0 and len(queueAccountId._queue) == 0:
            await asyncio.sleep(30)
            if len(queueMatchId._queue) == 0 and len(queueAccountId._queue) == 0:
                print("end master")
                await queueAccountId.put(None)
                await queueMatchId.put(None)
                queueLogCalls.put(None, True)
                queueAccountSave.put(None, True)
                return
        

def start_loop(loop, tasks):

    loop.run_until_complete(asyncio.gather(*tasks))
    loop.run_until_complete(asyncio.sleep(0))
    
    
def getLimits(headers):
    if 'X-Method-Rate-Limit' in headers and 'X-App-Rate-Limit' in headers:
        appLimits = {}
        for appLimit in headers['X-App-Rate-Limit'].split(","):
            appLimits[int(appLimit.split(":")[1])] = int(appLimit.split(":")[0])
            
        methodLimits = {}
        for methodLimit in headers['X-Method-Rate-Limit'].split(","):
            methodLimits[int(methodLimit.split(":")[1])] = int(methodLimit.split(":")[0])
        
        return (appLimits,methodLimits)
    return None
            
        
    
#Init loop
loop = asyncio.get_event_loop()
asyncio.set_event_loop(loop)

#Init queues
queueAccountId = asyncio.Queue(loop=loop, maxsize=0)
queueMatchId = asyncio.Queue(loop=loop, maxsize=0)


queueLogCalls = queue.Queue()
queueAccountSave = queue.Queue()

#Init locks
lockMatchlist = asyncio.Lock()
lockAccountlist = asyncio.Lock()
lockPause = asyncio.Lock()

queueAccountId.put_nowait(47863586)




tasks = [asyncio.ensure_future(master(queueLogCalls, queueAccountId, queueMatchId, lockPause))] 
tasks += [asyncio.ensure_future(matchlistCaller(queueLogCalls, queueAccountId, queueMatchId, lockMatchlist, lockPause)) for x in range(0,150)]
tasks += [asyncio.ensure_future(matchCaller(queueLogCalls, queueAccountId, queueMatchId, queueAccountSave, lockAccountlist, lockPause)) for x in range(0,100)]


t = Thread(target=start_loop, args=(loop,tasks))
t.start()

t1 = Thread(target=callLogger, args=(1,queueLogCalls))
t1.start()

t2 = Thread(target=saveAccounts, args=(1,queueAccountSave))
t2.start()

t1.join()
t2.join()


loop.call_soon_threadsafe(loop.stop)
t.join()
loop.stop()

print("end")
print(timeBegin)
print(time.mktime(datetime.datetime.utcnow().timetuple()) )
print(timeBegin - time.mktime(datetime.datetime.utcnow().timetuple()) )
