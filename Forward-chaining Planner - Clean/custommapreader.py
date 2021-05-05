



class LocationMap:

    def __init__(self, datastructure, mode:str):
        
        self.grid = None
        
        if mode=="squaregrid":
            #load datastructure to self.grid
            pass
            
        #if mode=="hexagongrid":
        #if mode=="trianglegrid":
        
        else:
            raise Exception(" [!!!] ERROR: Unsupported mode: " + mode)
        
    def load(self, datastructure):
        #load datastructure to self.grid
        pass
    
class CustomMapReader:

    def __init__(self):
        