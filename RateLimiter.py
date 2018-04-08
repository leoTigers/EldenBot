import asyncio, time, datetime


class RateLimiter:
    
    def __init__(self, limits : (int,int) = (10,10), name: str =""):
        
        #Init Async lock for the limiter
        self.lock = asyncio.Lock()
        self.backLock = asyncio.Lock()
        
        #Limits params
        self.limit = limits[0]
        self.duration = limits[1]
        
        #Count and begin of the time window
        self.count = 0
        self.time = 0
        
        #Name of the limiter (for debug prupose)
        self.name = name
        
        # "ID" of the time window
        self.num = 0
        
        #Init outgoing requests counters
        self.currentlyPending = 0
        self.previouslyPending = 0
        
        #Synchronicity state with server time window
        self.synced = False
        
        
    #Allows to update the limit number of requests
    def updateLimit(self,limit: int):
        self.limit = limit
        
    #Return the set duration of the time window
    def getDuration(self):
        return self.duration
    
    #Return the set limit number of requests
    def getLimit(self):
        return self.limit
    
    async def _reset(self):
        
        #Be sure to be out of the time window
        while self.time + self.duration >= int(time.mktime(datetime.datetime.utcnow().timetuple())):
            await asyncio.sleep(1)
        
        #Reseting count and time
        self.time = int(time.mktime(datetime.datetime.utcnow().timetuple()))
        self.count = 0
        
        #Manage the count of pending requests
        self.previouslyPending += self.currentlyPending
        self.currentlyPending = 0
        
        #Incr the num for the new time window
        self.num += 1
        #The window is not synch with server yet
        self.synced = False
    
    #Fired when a request is back
    async def getBack(self, num:int, timestamp:int, limit=None):
        with await self.backLock:
            
            #If the current time window is up to date
            if self.time + self.duration > timestamp:
                
                #Decrease the pending counter depending on the time window the request was counted
                if self.num == num:
                    self.currentlyPending -= 1
                else:
                    self.previouslyPending -= 1
                    self.count += 1
                
                #Sync the beginning of time window with server and update the limit
                if not self.synced:
                    if not limit == None:
                        self.updateLimit(limit)
                    self.synced = True
                    self.time = timestamp
                    
            #If the time window is out of date
            else:
                await self._reset()
                if not limit == None:
                    self.updateLimit(limit)
                self.previouslyPending -= 1
                self.count += 1
                self.synced = True
                self.time = timestamp
                

    async def getToken(self):

        with await self.lock:
                #Check if outside time window, reset count
                if self.time + self.duration < time.mktime(datetime.datetime.utcnow().timetuple()):

                    #Wait until it's safe to request and open a new time window
                    while self.previouslyPending >= self.limit:
                        await asyncio.sleep(0.5)
                        
                #If in time window, check count
                elif self.count < self.limit:

                    #Wait until it's safe to request or time window is passed
                    while (self.previouslyPending + self.count) >= self.limit and self.time + self.duration > time.mktime(datetime.datetime.utcnow().timetuple()):
                        await asyncio.sleep(0.5)
                    
                #If count limit reached, await for the end of time window
                else:
                    
                    #Await for the next time window
                    await asyncio.sleep( int((self.time + self.duration) - time.mktime(datetime.datetime.utcnow().timetuple())) + 1)

                    
                with await self.backLock:
                    #Double check if a reset has not occured in the mean time
                    timestamp = time.mktime(datetime.datetime.utcnow().timetuple())
                    if self.time + self.duration < timestamp:
                        await self._reset()
                        
                    #Incr count
                    self.count +=1
                    self.currentlyPending += 1
                    
                    return self.num

class RateLimiterManager:
    
    #Default application rate limit
    defaultApplicationLimits = [(500,10),(30000,600)]
    
    defaultMethodsLimits = {
        "match":[(500,10)],
        "timeline":[(500,10)],
        "matchlist":[(1000,10)],
        "leagueBySummoner":[(300,60)],
        "leagueById":[(500,10)],
    }
    
    def __init__(self):
        
        self.application = []
        for appLimit in self.defaultApplicationLimits:
            self.application.append(RateLimiter(appLimit, "app"))
            
        self.methods = {}
        
        for method in self.defaultMethodsLimits:
            self.methods[method] = []
            for methodLimit in self.defaultMethodsLimits[method]:
                self.methods[method].append(RateLimiter(methodLimit, method))
        
    
    def updateApplicationLimit(self, duration:int, limit:int):
        for appLimit in self.application:
            if duration == appLimit.getDuration():
                appLimit.updateLimit(limit)
                return
        self.application.append(RateLimiter((limit,duration)))
        
    def deleteApplicationLimit(self, duration:int):
        for appLimit in self.application:
            if duration == appLimit.getDuration():
                self.application.remove(appLimit)
                return
    
    def displayApplicationLimit(self):
        for appLimit in self.application:
            print(str(appLimit.getLimit())+" : "+str(appLimit.getDuration()))
            
    
    def displayApplicationLimiters(self):
        for appLimit in self.application:
            appLimit.displayLimiter()
    
    
    def updateMethodsLimit(self, method:str, duration:int, limit:int):
        for methodLimit in self.methods[method]:
            if duration == methodLimit.getDuration():
                methodLimit.updateLimit(limit)
                return
        self.methods[method].append(RateLimiter((limit,duration),method))
        
    def deleteMethodsLimit(self, method:str, duration:int):
        for methodLimit in self.methods[method]:
            if duration == methodLimit.getDuration():
                self.methods[method].remove(methodLimit)
                return
            
    async def getBack(self, method:str, token, timestamp:int, limits):
        if limits == None:
            for i,appLimit in enumerate(self.application):
                await appLimit.getBack(token[0][i], timestamp)
            for i,methodLimit in enumerate(self.methods[method]):
                await methodLimit.getBack(token[1][i], timestamp)
        else:
            for i,appLimit in enumerate(self.application):
                await appLimit.getBack(token[0][i], timestamp, limits[0][appLimit.getDuration()])
            for i,methodLimit in enumerate(self.methods[method]):
                await methodLimit.getBack(token[1][i], timestamp, limits[1][methodLimit.getDuration()])
    
    def displayMethodsLimit(self):
        for method in self.methods:
            print(method)
            for methodLimit in self.methods[method]:
                print(str(methodLimit.getLimit())+" : "+str(methodLimit.getDuration()))
        print()
    
    def displayMethodLimiters(self, method:str):
        for methodLimit in self.methods[method]:
            methodLimit.displayLimiter()
    
    
        
    async def getToken(self, method:str):
        appToken=[]
        methodToken=[]
        for appLimit in self.application:
            appToken.append(await appLimit.getToken())
            
        try:
            for methodLimit in self.methods[method]:
                methodToken.append(await methodLimit.getToken())
                
            return (appToken,methodToken)
        except Exception as e:
            print("Method not found : " + method)
            
        