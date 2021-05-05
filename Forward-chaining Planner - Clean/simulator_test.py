import sys
import copy
import networkx as nx
import random

import matplotlib.pyplot as plt

from networkx.drawing.nx_agraph import write_dot, graphviz_layout
from networkx import Graph, DiGraph
from action import Action
from pddlparser import DomainProblem
from pddlparser import DomainProblemParser
from personality import Personality
from coreplanner import BasicFCPlanner 
from coreplanner import PlanNode
from coreplanner import GoalNode 

#------------------------------------------------
#    GLOBAL DECLARATIONS 

_INPUT_DIR = "problemdomain/"


#------------------------------------------------
#    FUNCTION DECLARATIONS 

def zeroStringPad(input_str:str, new_length:int):
    output_str = copy.copy(input_str)
    while len(output_str) < new_length:
        output_str = "0" + output_str
    return output_str
    
#------------------------------------------------
#    CLASS DECLARATIONS 

class Actor:
    ''
    def __init(self, someID, sometype, goals):
        self.id = someID
        self.type = sometype
        self.goals = goals

class WorldSimulator:
    'World simulator class'
    
    def __init__(self, domprob:DomainProblem):
    
        #self.someshit = somevalue
        self.all_actors = dict()
        self.domainproblem = domprob
        pass
            
    #---->>>>   
    def createNewActor(self, parameters:dict):
        personality     = parameters['personality']
        goals           = parameters['goals']
        identity        = parameters['identity']
        status          = parameters['status']
        domprob         = parameters['domprob']     # << this is what the actor KNOWS (not necessarily accurate)
        
        
        plan_engine = BasicFCPlanner(identity, domprob, personality)
        
        #actor_planner_01 = BasicFCPlanner(identity, domprob, personality_01)
        
        new_actor = Actor(identity, status, goals)
        self.all_actors[identity] = new_actor
    
    #---->>>>   Plans for one chapter, then store possible solutions 
    #           in a chapter_solutions list
    def runChapter(self, parameters:dict):

        # 1. assign initial state
        # 2. assign chapter goals
        # 3. assign participating actors (get from pool of ALL actors)
            # assign active actors (will perform actions)
            # assign passive actors (will be affected by active actors)
    
        initial_state           = parameters['initial_state']
        chapter_goals           = parameters['chapter_goals']
        participating_actors    = parameters['participating_actors'] 
        # >>>>
        #   participating_actors:list
        #   [identity,status,???]
        
        # 4. execute planning loop recursively (__worldPlannerRoutine)
        #   - current state
        #   - current_node     
        #   - found_goal_node_list
        #   - current_layer   
        #   - max_depth         
        #   - dp_parser           
        #   - plan_root_node      
        #   - achieved_goals      
        #   - nextstepsize        
        #   - nextsteprange       
        #   - mode      
        search_space = DiGraph()
        plan_root_node_label = str(hash(frozenset(initial_state)))
        plan_root_node_address = str(zeroStringPad("0",_ZEROPADDINGLENGTH))
        plan_root_node = PlanNode(plan_root_node_label, plan_root_node_address, [],initial_state, None, current_goals, 0)
        
        nextstepsize = 4
        nextsteprange = 2
        
        worldplannerparameters['current_node']         = plan_root_node
        worldplannerparameters['found_goal_node_list'] = found_goal_node_list 
        worldplannerparameters['current_layer']        = current_layer        
        worldplannerparameters['max_depth']            = max_depth            
        worldplannerparameters['dp_parser']            = dp_parser            
        worldplannerparameters['plan_root_node']       = plan_root_node       
        worldplannerparameters['achieved_goals']       = achieved_goals       
        worldplannerparameters['nextstepsize']         = nextstepsize         
        worldplannerparameters['nextsteprange']        = nextsteprange        
        
        worldplannerparameters['participating_actors'] = participating_actors        
        
        worldplannerparameters['mode']                 = mode                 
        
        
        
    def __worldPlannerRoutine(self, search_space:DiGraph, parameters:dict):
    
        # 1. for each participating actor, define action queue
        # 2. Using some heuristic, apply actions in different order cobinations (guide: nextstepsize)
        # 3. All other steps, aside from "step explanation" are based on FCP
        # ?. call __worldPlannerRoutine recursively
        
        #   Approach 1:
        #   - each character generates one plan search_space per chapter
        #   - each world plan step just revisits same search_space
        #       >
        
        #   parameters:
        #       current_node        :PlanNode
        #       unexplained_steps   :list
        #       found_goal_node_list:list
        #       current_layer       :int
        #       max_depth           :int
        #       dp_parser           :DomainProblemParser
        #       plan_root_node      :PlanNode
        
        current_node          = parameters['current_node']        
        found_goal_node_list  = parameters['found_goal_node_list']
        current_layer         = parameters['current_layer']
        max_depth             = parameters['max_depth']     
        dp_parser             = parameters['dp_parser']         
        plan_root_node        = parameters['plan_root_node']
        achieved_goals        = parameters['achieved_goals']
        nextstepsize          = parameters['nextstepsize']
        nextsteprange         = parameters['nextsteprange']
        participating_actors  = parameters['participating_actors']
        mode                  = parameters['mode']
        
        action_queue_dict = dict() #dictionary of lists
        # >>>>
        
        
        # >>>>
        for someactor in participating_actors:
            action_list = []
            #generate action_list for someactor
            action_queue_dict[someactor.id] = action_list
        
        

    def execute(self):
        print(" [...] Start")
        # ---------------------
        # 1. Create all actors
        actorparameters = dict()
        # >>>> Talia
        personality = Personality()
        personality.setAlignmentValues(70,70)
        
        actorparameters['identity']     = 'talia'
        actorparameters['personality']  = personality
        actorparameters['goals']        = None                               # <-- this should be regenerated every chapter
        actorparameters['status']       = 'ACTIVE'
        actorparameters['domprob']      = copy.copy(self.domainproblem)      # <-- for now, all actors have the same knowledgebase
        
        self.createNewActor(actorparameters)

        # >>>> Vince
        personality = Personality()
        personality.setAlignmentValues(70,-45)
        
        actorparameters['identity']     = 'vince'
        actorparameters['personality']  = personality
        actorparameters['goals']        = None                               # <-- this should be regenerated every chapter
        actorparameters['status']       = 'ACTIVE'
        actorparameters['domprob']      = copy.copy(self.domainproblem)      # <-- for now, all actors have the same knowledgebase
        
        self.createNewActor(actorparameters)
        
        # >>>> Rory
        personality = Personality()
        personality.setAlignmentValues(0,45)
        
        actorparameters['identity']     = 'rory'
        actorparameters['personality']  = personality
        actorparameters['goals']        = None                               # <-- this should be regenerated every chapter
        actorparameters['status']       = 'ACTIVE'
        actorparameters['domprob']      = copy.copy(self.domainproblem)      # <-- for now, all actors have the same knowledgebase
        
        self.createNewActor(actorparameters)
        
        # >>>> Gargax
        personality = Personality()
        personality.setAlignmentValues(-99,-99)
        
        actorparameters['identity']     = 'gargax'
        actorparameters['personality']  = personality
        actorparameters['goals']        = None                               # <-- this should be regenerated every chapter
        actorparameters['status']       = 'ACTIVE'
        actorparameters['domprob']      = copy.copy(self.domainproblem)      # <-- for now, all actors have the same knowledgebase
        
        self.createNewActor(actorparameters)
        
        # ---------------------
        # 2. Define chapters 
        #   2.1 Chapter goals
        #   2.2 Chapter actors
            # active actors (will perform actions)
            # passive actors (will be affected by active actors)
            
        # ---------------------
        # 3. Loop runChapter, chaining them together
        #   result_state -> new_initial_state
            
        print(" [...] End")

    
def main(argv):


    _INPUT_CATEGORY = "fantasy"
    _INPUT_SERIES = "02"
    
    inp_domain = _INPUT_DIR + _INPUT_CATEGORY + "-domain-" + str(_INPUT_SERIES) + ".pddl"
    inp_problem = _INPUT_DIR + _INPUT_CATEGORY + "-problem-" + str(_INPUT_SERIES) + ".pddl"
    
    print(" [...] inp_domain : " + inp_domain)
    print(" [...] inp_problem : " + inp_problem)
    
    domprob = DomainProblem()
    domprob.parseDomain(inp_domain)
    domprob.parseProblem(inp_problem)
    
    sim1 = WorldSimulator(domprob)
    sim1.execute()
    
    
    
if __name__ == '__main__':
    main(sys.argv)