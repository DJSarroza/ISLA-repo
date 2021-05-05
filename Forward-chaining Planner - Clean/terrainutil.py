import sys
import copy
import networkx as nx
import datetime
import matplotlib.pyplot as plt
import utility as util
import ast

from networkx import Graph, DiGraph


class TerrainNode:
    'Terrain graph node'
    
    def __init__(self):
        #self.actors = []
        #self.action = None
        #self.partial_state = None
        #self.layer = 0
        self.label = None

def readFromFile(path:str, mode="predicate-str"):

    # Modes:
    #   predicate-str   (adjacent loc_from loc_to)
    #   predicate-list  ["adjacent", loc_from:str, loc_to:str]
    
    #nx.read_edgelist(path)
    
    output_list = []
    input_file = open(path,'r')
    
    for input_line in input_file:
        
        # 1. Comment processing
        
        # 2. Valid input line processing
        split_input_line = input_line.strip().split('|')
        # split_input_line[0] From 
        # split_input_line[1] To
        # split_input_line[2] Weight?
        #print(split_input_line)
        if len(split_input_line) == 2:
            if mode == "predicate-str":
                output_list.append("(adjacent "+split_input_line[0]+" "+split_input_line[1]+")")
            elif mode == "predicate-list":
                temp_list = []
                temp_list.append(ast.literal_eval(split_input_line[0]))
                temp_list.append(ast.literal_eval(split_input_line[1]))
                
                output_list.append(temp_list)
        else:
            pass
            #raise Exception("Invalid terrain file: " + path)

    return output_list

