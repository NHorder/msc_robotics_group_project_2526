

class Action():

    def __init__(self,name:str,wall:str):
        self.name = name
        self.wall = wall
        self.loc = -1
    
    def SetListLoc(self,loc):
        self.loc = loc
    
    def GetLoc(self):
        return self.loc

    def GetData(self):
        return [self.name,self.wall,self.loc]