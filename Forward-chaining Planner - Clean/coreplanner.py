import sys
import copy
import networkx as nx
import random
import pickle
import datetime
import matplotlib.pyplot as plt
import utility as util
import ast
import pddlglobals
import hashlib
#import json
#import multiprocessing as mp

#from multiprocessing import Pool, Value

#from pathos.multiprocessing import ProcessingPool

from networkx.drawing.nx_agraph import write_dot, graphviz_layout
from networkx import Graph, DiGraph
from pddllib import Action, Predicate
from pddllib import DomainProblem
from pddllib import DomainProblemParser
from personality import Personality

from flask_sqlalchemy import SQLAlchemy                             
from flask_app.models import    PlanGraphNode as Model_PlanGraphNode
from flask_app.models import    PlanGraphEdge as Model_PlanGraphEdge

from sqlalchemy.orm   import  aliased
from sqlalchemy       import and_, or_, update, select 
#------------------------------------------------
#    GLOBAL DECLARATIONS 

_INPUT_DIR = "./domainproblem/"
#_INPUT_DIR = "/home/sarrozadj/ISLA_online/domainproblem/"

_LOG_DIR = "./logs/"
#_LOG_DIR = "/home/sarrozadj/ISLA_online/logs/"
_LOG_EXECUTION_LOGFILE = ["","","","","","",""]
_LOG_LAST_ENTRY_TIMESTAMP = [""]
_LOG_VARIABLES = [0,0,0,0,0]

_MAX_GOAL_GRAPH_LAYERS = 99

_MAX_PLAN_NODE_CHILDREN = 32
#_MAX_LOOP_TRIES = _MAX_PLAN_NODE_CHILDREN * 4
_MAX_LOOP_TRIES = 500
_MAX_LOOP_BACK = 100

_HARDLOOK_THRESHOLD = 0.5

_ZEROPADDINGLENGTH = 2
_DEBUG_GG_UNIQUE_ACTIONS = {}

_RAFFLE_LIST1 = []

_GOAL_GRAPH_NODE_PAIRS = {}

_GOAL_GRAPH_PATHS = {}

_GG_CONNECTION_RULE_ALLOWANCE = 1

_VALID_STATE_THROTTLE = 55
#_VALID_STATE_THROTTLE_FLAT = -1

#_RUNTIME_THRESHOLD_MINUTES = 6

#_RAFFLE_LIST1.append('random_travel')

#_DEBUG_GG_UNIQUE_ACTIONS = []

#_UNEXPLAINED_THRESHOLD = 0.40 * 100
#------------------------------------------------
#    FUNCTION DECLARATIONS 

def toFunctionString(name, parameters, debug=False):

    if debug:
        for something in parameters:
            print(something)
        print("____")
        
    function_string = ""
    function_string += name + "("
    
    comma_flag = False
    for parameter in parameters:
        if comma_flag:
            function_string += ", "
        else:
            comma_flag = True
        #if parameter[0][0] != "
        
        if parameter[1] == "predicate":
            raw_predicate = copy.deepcopy(parameter[0])
            
            raw_name = raw_predicate.pop(0)
            raw_parameters = raw_predicate
            #print(raw_name)
            #print(raw_parameters)
            #input()
            
            processed_predicate = toFunctionString(raw_name, raw_parameters, debug)
            function_string += processed_predicate
        else:
            function_string += str(parameter[0])
        
        
    function_string += ")"
        
    return function_string


    
#------------------------------------------------
#    CLASS DECLARATIONS 

class GoalGraphNode:
    'Goal graph node'
    
    def __init__(self):
        #self.actors = []
        self.action = None
        #self.partial_state = None
        self.partial_precon_state = None
        self.partial_effect_state = None
        self.layer = 0
        self.label = None
        
class PlanGraphNode:
    'Plan graph node'
    
    def __init__(self, label:str, address:str, plan:list, state:set, last_action:Action, goals:list, layer:int, goal_graph_soft_plan=None, soft_plan_source=None):
        self.label = label
        self.address = address
        self.plan = copy.deepcopy(plan)
        self.last_action = copy.deepcopy(last_action)
        self.state = copy.deepcopy(state)
        self.known_goals = copy.deepcopy(goals)
        self.layer = layer
        #self.action_cache = []
        self.intentions_achieved = []       # list of tuples:  (intention_actor, intention_predicate, not_flag)
        self.author_goal_score = -1
        self.achieved_author_goals = []
        self.goal_graph_soft_plan = goal_graph_soft_plan
        self.soft_plan_source = soft_plan_source
    def __str__(self):
        return  "PlanGraphNode:"                + "\n"      + \
                str(self.label)                 + "\n"      + \
                str(self.address)               + "\n"      + \
                str(self.plan)                  + "\n"      + \
                str(self.last_action)           + "\n"      + \
                str(sorted(self.state))         + "\n"      + \
                str(self.known_goals)           + "\n"      + \
                str(self.layer)                 + "\n"      + \
                str(self.goal_graph_soft_plan)  + "\n"      + \
                str(self.soft_plan_source)  + "\n"
               
class SolutionActionInstance:
    'Solution action instance; mirror of SolutionChapterInstanceAction DB model'
        
    def __init__(self, 
                    action_instance:Action, 
                    initial_state:set, 
                    final_state:set, 
                    initial_state_hrparagraph, 
                    negative_change_hrparagraph, 
                    positive_change_hrparagraph, 
                    final_state_hrparagraph_all,
                    final_state_hrparagraph_norm_only,
                    final_state_hrparagraph_adjacency_only,
                    final_state_hrparagraph_intentions_only,

                    final_state_hrparagraph_special1="",
                    final_state_hrparagraph_special2="",
                    final_state_hrparagraph_special3="",
                    final_state_hrparagraph_special4="",
                    
                    explained_by_list=None,
                    
                    plan_graph_node_label="",
                    plan_graph_node_parent="",
                    explanation_paths=None,
                    goal_graph_soft_plan=None,
                    soft_plan_source=None
                ):
        
        self.action_instance = action_instance
        
        self.initial_state = initial_state
        self.final_state = final_state
        
        self.initial_state_hrparagraph               = initial_state_hrparagraph  
        self.negative_change_hrparagraph             = negative_change_hrparagraph
        self.positive_change_hrparagraph             = positive_change_hrparagraph

        self.final_state_hrparagraph_all             = str(final_state_hrparagraph_all)                
        self.final_state_hrparagraph_norm_only       = str(final_state_hrparagraph_norm_only)          
        self.final_state_hrparagraph_adjacency_only  = str(final_state_hrparagraph_adjacency_only)     
        self.final_state_hrparagraph_intentions_only = str(final_state_hrparagraph_intentions_only)    
        
        self.final_state_hrparagraph_special1        = final_state_hrparagraph_special1               
        self.final_state_hrparagraph_special2        = final_state_hrparagraph_special2                   
        self.final_state_hrparagraph_special3        = final_state_hrparagraph_special3                   
        self.final_state_hrparagraph_special4        = final_state_hrparagraph_special4                   
        
        self.explained_by_list = copy.deepcopy(explained_by_list) #List of Actions
        self.explanation_paths = copy.deepcopy(explanation_paths)
        self.plan_graph_node_label = plan_graph_node_label
        self.plan_graph_node_parent = plan_graph_node_parent
        self.goal_graph_soft_plan = goal_graph_soft_plan
        self.soft_plan_source = soft_plan_source
#------------------------
#    Basic Forward-Chaining Plan Engine
class BasicFCPlanner:
    'Basic Forward-Chaining Plan Engine'
    # >> ATTRIBUTES
    #    domainproblem
    
    
    def __init__(self,identity:str, domprob:DomainProblem, personality:Personality, load_mode:str, parameters:dict, neutral_obj_count=0,run_id=None,db=None):
        
        # EXPERIMENTAL
        GLOBAL_current_graph = None
        
        # EXPERIMENTAL
        
        _INPUT_DOMAIN_FULL_LABEL = parameters['input_domain_full_label']
        #_INPUT_SERIES   = parameters['input_series']
        
        #inp_domain = _INPUT_DIR + _INPUT_DOMAIN_FULL_LABEL + "-domain-" + str(_INPUT_SERIES) + ".pddl"
        #inp_problem = _INPUT_DIR + _INPUT_DOMAIN_FULL_LABEL + "-problem-" + str(_INPUT_SERIES) + ".pddl"
        

        # Start logging
        now = datetime.datetime.now()
        now_str = now.strftime("%Y%m%d_%H%M%S")
        
        _PERSONALITY_SERIES = ""
        _PERSONALITY_SERIES += "GG" + util.zeroStringPad(str(personality.goal_graph_depth    ),2)
        _PERSONALITY_SERIES += "PG" + util.zeroStringPad(str(personality.plan_graph_depth    ),2)
        _PERSONALITY_SERIES += "NS" + util.zeroStringPad(str(personality.nextstepsize        ),2)
        _PERSONALITY_SERIES += "NSR"+ util.zeroStringPad(str(personality.nextsteprange       ),2)
        _PERSONALITY_SERIES += "SPG"+ util.zeroStringPad(str(personality.solutions_per_goal  ),2)
        
        
        _LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/LOG_coreplanner_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _PERSONALITY_SERIES + "-" + now_str + ".txt"
        _LOG_EXECUTION_LOGFILE[1] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_coreplanner_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _PERSONALITY_SERIES + ".csv"
        _LOG_EXECUTION_LOGFILE[3] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_coreplanner_sectiontiming_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _PERSONALITY_SERIES + ".csv"
        _LOG_EXECUTION_LOGFILE[4] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_coreplanner_special_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _PERSONALITY_SERIES + ".csv"
        _LOG_EXECUTION_LOGFILE[5] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_coreplanner_sectiontiming_getAllPaths_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _PERSONALITY_SERIES + ".csv"
        
        # 0. Goal definition and other initial tasks
        self.identity = identity
        self.identity_type = domprob._ADMIN_TYPE
        
        self.identity_predicate = [self.identity, self.identity_type]
        
        self.domainproblem = copy.deepcopy(domprob)
        self.personality = copy.deepcopy(personality)
        self.solutions = []
        self.prereq_action_cache = None
        
        
        #---->>>>
        # DEBUGGING variables
        self._GG_TOTAL_NODES = 0
        self._GG_ACTION_DENSITY_DICT = {}
        self._GG_ACTION_DENSITY_TOTAL = 0
        
        self._PG_ACTION_DENSITY_DICT = {}
        self._PG_ACTION_DENSITY_TOTAL = 0
        #---->>>>
        
        self.db = db
        
        
        goal_graph_depth = personality.goal_graph_depth
        dp_parser = DomainProblemParser(self.domainproblem)
        
        self.gg_goal_nodes_label_list = []
        self.gg_goal_nodes_label_list_others = []
        self.gg_goal_nodes_label_list_author = []
        self._CURRENT_LAYER_NODES = 0
        self.run_id = run_id
        
        
        logstr = "Generating Goal Graph -- MODE ["+load_mode+"]"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        
        print(str(datetime.datetime.now()) + ": Generating Goal Graph -- MODE ["+load_mode+"]")
        start_execution = datetime.datetime.now()
        if (load_mode == "SAVE"):
        
            print(str(datetime.datetime.now()) + ": >> Start goal graph generation...")
            self.generateRigidGoalGraph(goal_graph_depth)
            print(str(datetime.datetime.now()) + ": >> Done goal graph generation.")
            
            
            print(str(datetime.datetime.now()) + ": >> Start saving goal graph")
            goal_graph_file = open("picklejar/goal_graph.gpickle",'wb')
            nx.write_gpickle(self.goal_graph,goal_graph_file)
            
            with open('picklejar/gg_goal_nodes_label_list.pickle', 'wb') as handle:
                pickle.dump(self.gg_goal_nodes_label_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
            
            with open('picklejar/goal_graph_master_list.pickle', 'wb') as handle:
                pickle.dump(self.goal_graph_master_list, handle, protocol=pickle.HIGHEST_PROTOCOL)
                
            print(str(datetime.datetime.now()) + ": >> End saving goal graph")
            
        elif load_mode == "LOAD":
        
            print(str(datetime.datetime.now()) + ": >> Start loading goal graph")
            self.goal_graph = DiGraph()
            self.goal_graph_master_list = {}
            with open('picklejar/gg_goal_nodes_label_list.pickle', 'rb') as handle:
                self.gg_goal_nodes_label_list = pickle.load(handle)            
                
            with open('picklejar/goal_graph_master_list.pickle', 'rb') as handle:
                self.goal_graph_master_list = pickle.load(handle)            
                
            # TODO: Modify instantiation routine to cater to only a handful of actor variables
            #variable_dict ={}
            #variable_dict['']
            
            self.instantiateActions()
            self.instantiatePredicates()
            
            self.all_intentions = self.domainproblem.getAllIntentions()
        
            goal_graph_file = open("picklejar/goal_graph.gpickle",'rb')
            self.goal_graph = nx.read_gpickle(goal_graph_file)
            print(str(datetime.datetime.now()) + ": >> End loading goal graph")
        #elif load_mode == "TEST":
        #   
        
        elif load_mode == "":
            
            #print(str(datetime.datetime.now()) + ": >> Start goal graph generation... [NO SAVE]")
            #logstr = "Start goal graph generation... [NO SAVE]"
            #util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            #
            #self.generateRigidGoalGraph(goal_graph_depth)
            #
            #print(str(datetime.datetime.now()) + ": >> Done goal graph generation.")
            #logstr = "Done goal graph generation."
            #util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            pass
            
        else:
            logstr = " [!!!] Invalid load_mode: " + str(load_mode)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(" [!!!] Invalid load_mode: " + str(load_mode))
        
        end_execution = datetime.datetime.now()
        
        elapsed_time = end_execution - start_execution
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        #------------------------------------------------------------
        # 0. Initialize planner engine
        current_goals = []
        # TODO
        #if personality
        #   affects goal definitions
        for goal in self.domainproblem.positive_goals:
            current_goals.append([self.identity,goal])
        for goal in self.domainproblem.negative_goals:
            current_goals.append([self.identity,goal])
            
        # TODO
        #if personality (or intelligence)
        #   affect size of next step 
        nextstepsize = personality.nextstepsize
        nextsteprange = personality.nextsteprange
        
        
        # 1. Define search space graph
        self.search_space = DiGraph()
        
        # 2. Define root node
        
        #self.domainproblem.state = sorted(self.domainproblem.state)
        
        raw_state_str = str(frozenset(sorted(self.domainproblem.state)))
        plan_root_node_label = str(hash(raw_state_str)) + "_" \
                             + hashlib.blake2s(raw_state_str.encode('utf-8'),salt=run_id[0:8].encode('utf-8')).hexdigest()
                             
        plan_root_node_address = str(util.zeroStringPad("0",_ZEROPADDINGLENGTH))
        plan_root_node = PlanGraphNode(plan_root_node_label, plan_root_node_address, [],frozenset(sorted(self.domainproblem.state)), None, current_goals, 0)
        
        achieved_intentions = []
        
        self.search_space.add_node(plan_root_node_label, body=plan_root_node,layer=0)
        
        # 3. Define supporting data structures and parameters
        unexplained_steps = {}
        found_intention_node_list = []
        current_layer = 1
        
        plan_graph_depth = personality.plan_graph_depth
        
        #print("personality.plan_graph_depth")
        #print(personality.plan_graph_depth)
        #input()
        
        self.planner_parameters = dict()
        self.planner_parameters['current_node']         = plan_root_node
        self.planner_parameters['unexplained_steps']    = unexplained_steps
        self.planner_parameters['found_intention_node_list'] = found_intention_node_list
        self.planner_parameters['current_layer']        = current_layer
        self.planner_parameters['max_depth']            = plan_graph_depth
        self.planner_parameters['dp_parser']            = dp_parser
        self.planner_parameters['plan_root_node']       = plan_root_node        
        self.planner_parameters['achieved_intentions']  = achieved_intentions
        self.planner_parameters['nextstepsize']         = nextstepsize
        self.planner_parameters['nextsteprange']        = nextsteprange
        self.planner_parameters['mode']                 = "PERSONAL"                
        
        # 4. Create initial search space!
        #print(" [...] Root node: " + str(search_space.nodes[plan_root_node.label]))
        #print(" [...] Start now [Action list: "+str(len(self.goal_graph_master_list))+"]")
        
        #TODO - May be reactivated later (if needed)
        #return_flag = self.__glaiveRoutine(self.search_space, self.planner_parameters)
        
        # TODO
        #if return_flag
        
        pass
        
    #-----------------------
    
    #---->>>> [ PRIVATE METHODS ]
    
    def extractObjects(self, predicate, object_list_output):
        #print(stuff)
        #input()
        ctr = 0
        for term in predicate:
            if ctr > 0:
                object_list_output.append(copy.deepcopy(term))
            
            ctr+=1 
            
    def convertToStringSet(self, state_list):
        new_set = set()
        for something in state_list:
            #new_thing = "\"" + str(something) + "\""
            new_thing = str(something)
            new_set.add(new_thing)
        
        return new_set
    
    def saveNodeToDB(self, run_id, chapter_str, current_node):
        
        #node_body_serialized = pickle.dumps(current_node)
        
        node_label = run_id + "_" + chapter_str + "|" + current_node.label
        
        if current_node.last_action is not None:
            last_action = current_node.last_action.getFunctionString()
        else:
            last_action = "<None>"
        
        try:
            new_plan_graph_node = Model_PlanGraphNode(
                run_id                  = run_id                                       ,
                node_label              = node_label                                   ,
                layer                   = str(current_node.layer)                      ,
                last_action             = last_action                                  ,
                author_goal_score       = str(current_node.author_goal_score)          ,
                state                   = str(current_node.state)                      ,
                achieved_author_goals   = str(current_node.achieved_author_goals)
                #reserved_01             = 
                #reserved_02             = 
                #reserved_03             = 
                #reserved_04             = 
                #reserved_05             = 
            )
            
            
            self.db.session.add(new_plan_graph_node)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            pass
            
        pass
    
    def saveEdgeToDB(self, run_id, from_node_label, to_node_label):
        
        try:
            new_plan_graph_edge = Model_PlanGraphEdge(
                run_id                  = run_id            ,
                from_node_label         = from_node_label   ,
                to_node_label           = to_node_label
            )
            
            self.db.session.add(new_plan_graph_edge)
            self.db.session.commit()
        except Exception:
            self.db.session.rollback()
            pass
        pass
    
    def __populateWith(self, old_list:list, new_list:list, output_list):
        old_list_copy = copy.deepcopy(old_list)
        
        if len(old_list) == 0:
            for new_list_elem in new_list:
                temp_list = []
                temp_list.append(new_list_elem)
                output_list.append(temp_list)            
        else:
            for old_list_elem in old_list_copy:
                for new_list_elem in new_list:
                    temp_list = list(old_list_elem)
                    
                    temp_list.append(new_list_elem)
                    output_list.append(temp_list)
    
    def __containsPredicate(self, predicate_term, predicate_tree):
        found_flag = False
        
        for term in predicate_tree:
            #print(" [...>>>>>] Checking with : '"+str(term)+"'")
            if predicate_term == term:
                #print(" [...>>>>]" + str(predicate_term) + " ==  " + str(term))
                return True

            if type(term) is list:
                if term[0] == self.domainproblem._NOT_OPERATOR:
                    pass
                else:
                    found_flag = self.__containsPredicate(predicate_term, term)
            if found_flag == True:
                return True
            else:
                pass
                
        return found_flag
    
    def __getRandomNextSteps(self,size:int, mode:int, seed:int, steprange:int):
        
        #-------->>>>
        def __getRandomPath(gg, somegoal_node, length):
            
            length_ctr = 0
            path = []
            current_node = somegoal_node
            while length_ctr < length:
                successor_list = list(gg.successors(current_node))
                predecessor_list = list(gg.predecessors(current_node))
                if (len(predecessor_list) > 0) :
                    next_step = random.sample(list(predecessor_list),1).pop()
                    
                    #path.append(gg.nodes()[next_step]['body'].action)
                    path.append(gg.node[next_step]['body'].action)
                    
                    #print()
                    #input(" AAAAAAAAAHH: ")
                else:
                    
                    #print(current_node)
                    #print(" [>>!]" + str(successor_list) + ":" + str(len(successor_list)))
                    #print(" [>>!]" + str(predecessor_list) + ":" + str(len(predecessor_list)))
                    break
                length_ctr += 1
                current_node = next_step
            return path
        
         #-------->>>>
    
        next_step_list = []
        new_size = random.randint(size-steprange, size+steprange)
        
        size_ctr = 0
        try_ctr = 0
        found_flag = False
        
        #goal_nodes = self.goal_graph.nodes()
        chosen_goals = []
        
        while size_ctr < new_size:
            break_flag = False
            while not break_flag:
                somegoal_label = random.choice(self.gg_goal_nodes_label_list)
                if somegoal_label not in chosen_goals:
                    chosen_goals.append(somegoal_label)
                    break_flag = True
                
            next_step = somegoal_label
            new_path = copy.deepcopy(__getRandomPath(self.goal_graph, next_step,4))
            next_step_list.append(new_path)
            size_ctr += 1
            #print(" [>] new_path: " + str(new_path))
        
        #print(" [,,,] new_path")
        #print(" [>>] len(next_step_list) : " + str(len(next_step_list)))
        
        #for somecluster in next_step_list:
        #    print("[>>] Path:")
        #    for someaction in somecluster:
        #        print(" [>>>>>] " + someaction.getFunctionString())
        #input()
        return next_step_list
    
    def closestToState(self, gg_label_list:list, current_state:set, ctr_ceiling):
        
        #for something in predecessor_list:
        #    print(something)
        #print("---")
        
        for somepredicate in current_state:
            print(somepredicate)
        print("---")
        #input()
        #start_execution = datetime.datetime.now()
        
        highestscore = [None,-9999]
        gg = self.goal_graph
        
        rising_ctr = 0
        hard_ceiling = len(gg_label_list)
        for gg_label in gg_label_list:
            # 0. Ctr stuff
            rising_ctr +=0
            
            # 1. Get candidate information
            candidate_node = gg.node[gg_label]
            candidate_state = candidate_node['body'].partial_precon_state
            candidate_action = candidate_node['body'].action
            
            print(candidate_action.getFunctionString())
            
            # 2. Check candidate score
            candidate_score = 0
            candidate_score += len( util.listRemove(candidate_state,current_state)) * -1
            
            print(str(candidate_score) + "/" + str(len(candidate_state)))
            
            # 3. Update highestscore
            if candidate_score > highestscore[1]:
                highestscore[0] = candidate_node
                highestscore[1] = candidate_score
                
            if (rising_ctr / hard_ceiling) >= ctr_ceiling:
                print("hard stop??")
                print(rising_ctr)
                print(hard_ceiling)
                print(ctr_ceiling)
                break
        
        #print("candidate_node : " + str(candidate_node['body'].layer) + "-" + candidate_node['body'].action.getFunctionString() )
        #end_execution = datetime.datetime.now()
        #elapsed_time = end_execution - start_execution
        #elapsed_seconds = elapsed_time.total_seconds()
        #print(" [...?] __closestToState: " + str(elapsed_seconds))
        print(highestscore)
        return highestscore[0]
    
    def getValidStartStates(self, current_state:set):
        
        valid_start_state_labels = []
        gg = self.goal_graph
        
        node_count = 0
        
        #print("current_state")
        #for something in current_state:
        #    print(something)
        #print("===========")
        
        for gg_label in gg.nodes:
            
            #print(gg_label)
            
            node_count += 1
            # 1. Get candidate information
            candidate_node = gg.node[gg_label]

            
            candidate_action = candidate_node['body'].action
            
            candidate_state_pos = []
            util.listExtend(candidate_state_pos,candidate_action.positive_preconditions)
            candidate_state_pos = self.convertToStringSet(candidate_state_pos)
            
            candidate_state_neg = []
            util.listExtend(candidate_state_neg,candidate_action.negative_preconditions)
            
            
            # 2. Check candidate score
            candidate_score = 0
            
            # 2.1 Positive preconditions
            candidate_score += len( util.listRemove(candidate_state_pos,current_state)) * -1
            
            # 2.2 Negative preconditions

            for somenegpred in candidate_state_neg:
                #print(somenegpred[1])
                #input()
                if str(somenegpred[1]) in current_state:
                    candidate_score += -1
            
            
            
            # 3. Valid states have candidate_score == 0
            #print(str(candidate_score) + " : " + gg_label)
            
            if candidate_score == 0:
                valid_start_state_labels.append(gg_label)
                #print(candidate_action.getFunctionString())
                #print("--")
                

            #else:
                #print(str(candidate_score) + " : " + gg_label)
                #print("====")
                #input()
                #for something in candidate_state:
                #    print(something)
                
                
            #input()
                
        #print(node_count)
        #input()
        #return sorted(valid_start_state_labels)
        return valid_start_state_labels
    
    def getValidStartState(self, current_state:set, mode="first"):
        
        valid_start_state_labels = []
        gg = self.goal_graph
        
        node_count = 0
        
        #print("current_state")
        #for something in current_state:
        #    print(something)
        #print("===========")
        
        if mode == "random":
            gg_nodes = list(copy.deepcopy(gg.nodes))
            random.shuffle(gg_nodes)
        else:
            gg_nodes = gg.nodes
            
        for gg_label in gg_nodes:
            
            #print(gg_label)
            
            node_count += 1
            # 1. Get candidate information
            candidate_node = gg.node[gg_label]

            
            candidate_action = candidate_node['body'].action
            
            candidate_state_pos = []
            util.listExtend(candidate_state_pos,candidate_action.positive_preconditions)
            candidate_state_pos = self.convertToStringSet(candidate_state_pos)
            
            candidate_state_neg = []
            util.listExtend(candidate_state_neg,candidate_action.negative_preconditions)
            
            
            # 2. Check candidate score
            candidate_score = 0
            
            # 2.1 Positive preconditions
            candidate_score += len( util.listRemove(candidate_state_pos,current_state)) * -1
            
            # 2.2 Negative preconditions

            for somenegpred in candidate_state_neg:
                #print(somenegpred[1])
                #input()
                if str(somenegpred[1]) in current_state:
                    candidate_score += -1
            
            
            
            # 3. Valid states have candidate_score == 0
            #print(str(candidate_score) + " : " + gg_label)
            
            if candidate_score == 0:
                #valid_start_state_labels.append(gg_label)
                return gg_label
                #print(candidate_action.getFunctionString())
                #print("--")
                

            #else:
                #print(str(candidate_score) + " : " + gg_label)
                #print("====")
                #input()
                #for something in candidate_state:
                #    print(something)
                
                
            #input()
                
        #print(node_count)
        #input()
        #return sorted(valid_start_state_labels)
        #return valid_start_state_labels
        return None
    
    def getClosestValidStartState(self, current_state:set):
        gg = self.goal_graph
        
        closest_node_label = None
        closest_node_layer = None
        
        node_count = 0
        for gg_label in gg.nodes:
            node_count += 1
            # 1. Get candidate information
            candidate_node = gg.node[gg_label]

            
            candidate_action = candidate_node['body'].action
            
            candidate_state_pos = []
            util.listExtend(candidate_state_pos,candidate_action.positive_preconditions)
            candidate_state_pos = self.convertToStringSet(candidate_state_pos)
            
            candidate_state_neg = []
            util.listExtend(candidate_state_neg,candidate_action.negative_preconditions)
            
            
            # 2. Check candidate score
            candidate_score = 0
            
            # 2.1 Positive preconditions
            candidate_score += len( util.listRemove(candidate_state_pos,current_state)) * -1
            
            # 2.2 Negative preconditions

            for somenegpred in candidate_state_neg:
                #print(somenegpred[1])
                #input()
                if str(somenegpred[1]) in current_state:
                    candidate_score += -1
            
            
            
            # 3. Valid states have candidate_score == 0
            #print(str(candidate_score) + " : " + gg_label)
            
            if candidate_score == 0:
                
                # If layer is really close to target state, return immediately
                if candidate_node['body'].layer <= 1:
                    return gg_label
                else:
                    
                    if closest_node_layer is None:
                        closest_node_layer = candidate_node['body'].layer
                        closest_node_label = gg_label
                    elif candidate_node['body'].layer < closest_node_layer:
                        closest_node_layer = candidate_node['body'].layer
                        closest_node_label = gg_label
                    else:
                        pass
        
        
        return closest_node_label
    
    def getRigidNextSteps(self, current_state:set, size:int, mode:int, seed:int, steprange:int,dp_parser:DomainProblemParser):
        
        def __getRigidPath(somegoal_node_label, length, current_state, smart=True):
            length_ctr = 0
            path = []
            current_node_label = somegoal_node_label
            
            gg = self.goal_graph
            
            #print("\t Path:")
            while length_ctr < length:
            #while not(next_node is None):
            
                length_ctr += 1
                #predecessor_list = []
                #successor_list = list(gg.successors(current_node_label))
                predecessor_list = list(gg.predecessors(current_node_label))
                #path.append(gg.node[current_node_label]['body'].action)
                path.insert(0,gg.node[current_node_label]['body'].action)
                
                #print(" [...] Predecessors of " + current_node_label + ": " + str(len(predecessor_list)) + "/" + str(len(gg.nodes())))
                #input()
                
                if smart:
                    # [start][SMART] Pick step with highest heuristic score
                    if (length_ctr < length - 1):
                        ctr_ceiling = random.uniform(0.4, 0.8)
                    else:
                        ctr_ceiling = 1
                    
                    next_node = self.closestToState(predecessor_list, current_state, ctr_ceiling)
                    #input()
                    # [end][SMART]
                else:
                    # [start][DUMB] Pick random predecessor
                    #next_node = random.choice(predecessor_list)
                    try:
                        next_node = gg.nodes()[random.choice(predecessor_list)]
                    except IndexError:
                        next_node = None
                    # [end][DUMB]
                
                

                
                #next_node_label = str(next_node['body'].layer + 1) + "-" + next_node['body'].action.getFunctionString()
                if not(next_node is None):
                    #next_node_label = next_node['body'].label
                    current_node_label = next_node['body'].label
                else:
                    break
            
            return copy.copy(path)
        #-------->>>>
        
        #start_execution = datetime.datetime.now()
        next_step_list = []
        total_branching_size = random.randint(size-steprange, size+steprange)
        
        size_ctr = 0
        try_ctr = 0
        found_flag = False
        
        #goal_nodes = self.goal_graph.nodes()
        chosen_goals = []
        
        author_goal_branching_alloc = self.personality.author_goal_branching_alloc
        
        # Author goal branches
        author_goal_branching_alloc_size = (author_goal_branching_alloc/100) * total_branching_size
        
        
        
        # [NEW] OTHERS first
        #random.shuffle(self.gg_goal_nodes_label_list_others)
        #for somegoal_label in self.gg_goal_nodes_label_list_others:
        #    chosen_goals.append(somegoal_label)
        #    
        #    next_step_label = somegoal_label
        #    
        #    # Smart path
        #    new_path = copy.deepcopy(__getRigidPath(next_step_label, self.personality.goal_graph_depth, current_state, smart=True))
        #    next_step_list.append(new_path)
        #    
        #    #if len(new_path) > 1:
        #    #    for something in new_path:
        #    #        print("\t" + something.getFunctionString())
        #    #    print("=====")
        #    #    input()
        #    
        #    # Dumb path
        #    new_path = copy.deepcopy(__getRigidPath(next_step_label, self.personality.goal_graph_depth, current_state, smart=False))
        #    next_step_list.append(new_path)
        #    
        #    size_ctr += 1
        #    
        #    if size_ctr >= total_branching_size:
        #        break
        #        
        # [OLD] Author goals first
        if len(self.gg_goal_nodes_label_list_author) <= author_goal_branching_alloc_size:
            
            #start_execution = datetime.datetime.now()
            #print(" [,,,] [1]")
            for somegoal_label in self.gg_goal_nodes_label_list_author:
                #print(" [1][......] " + somegoal_label)
                if somegoal_label not in chosen_goals:
                    chosen_goals.append(somegoal_label)
                    #----
                    next_step_label = somegoal_label
                    new_path = __getRigidPath(next_step_label,self.personality.goal_graph_depth, current_state)
                    next_step_list.append(new_path)
                    size_ctr += 1
                    
                    #print(type(new_path))
                    #if len(new_path) > 1:
                    #    for something in new_path:
                    #        print("\t" + something.getFunctionString())
                    #    input()
            #end_execution = datetime.datetime.now()
            #elapsed_time = end_execution - start_execution
            #elapsed_seconds = elapsed_time.total_seconds()
            #print(" [...!] [Time check 0-2-1] : " + str(elapsed_seconds))
        else:
            
            #start_execution = datetime.datetime.now()
            #print(" [,,,] [2]")
            while size_ctr < author_goal_branching_alloc_size:
                break_flag = False
                
                random.shuffle(self.gg_goal_nodes_label_list_author)
                found_flag = False
                chosen_goal_label = None
                for somegoal_label in self.gg_goal_nodes_label_list_author:
                    #print(" [2][......] " + somegoal_label)
                    if somegoal_label not in chosen_goals:
                        chosen_goal_label = somegoal_label
                        chosen_goals.append(somegoal_label)
                        found_flag = True
                        break
                #----
                if found_flag:
                    next_step_label = chosen_goal_label
                    new_path = copy.deepcopy(__getRigidPath(next_step_label,self.personality.goal_graph_depth, current_state))
                    next_step_list.append(new_path)
                    size_ctr += 1
                    
                    #if len(new_path) > 1:
                    #    for something in new_path:
                    #        print("\t" + something.getFunctionString())
                    #    input()

                else:
                    break

            #end_execution = datetime.datetime.now()
            #elapsed_time = end_execution - start_execution
            #elapsed_seconds = elapsed_time.total_seconds()
            #print(" [...!] [Time check 0-2-2] : " + str(elapsed_seconds))
            
        # Other intention branches
        #start_execution = datetime.datetime.now()
        

        
        #input()

        #end_execution = datetime.datetime.now()
        #elapsed_time = end_execution - start_execution
        #elapsed_seconds = elapsed_time.total_seconds()
        #print(" [...!] [Time check 0-2-1] : " + str(elapsed_seconds))
        
        #logstr = "\t getRigidNextSteps: " + str(elapsed_seconds)+ " second/s"
        #print(logstr)
        #
        #logstr = "\t getRigidNextSteps: " + str(elapsed_minutes)+ " minutes/s"
        #print(logstr)
        
        return next_step_list
        
    def getAllPathsFromCurrentToGoal(self, valid_start_state_labels:list, current_goal_label:str, object_list:list, high_priority_goal_paths:list, low_priority_goal_paths:list, _TIMING_DEBUG2=None):
        
        #print("-----")
        #print(current_goal_label)
        #print(valid_start_state_label)
        #print("-----")
        #input()
        
        gg = self.goal_graph
        
        #print(gg.node[current_goal_label]['body'].action)
        #input()
        #print("[...] valid_start_state_labels: " + str(len(valid_start_state_labels)))
        
        
        valid_state_ctr = 0
        # Percent throttle?
        
        #_VALID_STATE_THROTTLE_PERCENT = len(valid_start_state_labels) * 0.5
        #
        #if _VALID_STATE_THROTTLE_PERCENT >= _VALID_STATE_THROTTLE_FLAT:
        #    _VALID_STATE_THROTTLE = _VALID_STATE_THROTTLE_PERCENT
        #else:
        #    _VALID_STATE_THROTTLE = _VALID_STATE_THROTTLE_FLAT
            
            
        for valid_start_state_label in valid_start_state_labels:
            #print(gg.node[valid_start_state_label]['body'].action)
            #input()
            
            valid_state_ctr += 1
            
            if (valid_state_ctr > _VALID_STATE_THROTTLE) and (_VALID_STATE_THROTTLE >= 0):
                break
            
            _gg_paths_label = valid_start_state_label + "->" + current_goal_label
            
            # [!] _GOAL_GRAPH_PATHS memoization
            
            if _gg_paths_label in _GOAL_GRAPH_PATHS:
            
                # [TIMING SECTION 01b_05 - START]
                _current_section01b_05_start = datetime.datetime.now()
                    
                #print("[...] Memoized path found:")
                #for something in _GOAL_GRAPH_PATHS[_gg_paths_label]:
                #    print(something)
                #print("===")
                goal_paths = _GOAL_GRAPH_PATHS[_gg_paths_label]
                
                for path in goal_paths:
                    _high_priority_flag = False
                    action_list = []
                    for someaction in path:
                        #action_list.append(gg.node[somelabel]['body'].action)
                        
                        if not _high_priority_flag:
                            for someobj in object_list:
                                if str(someobj) in str(someaction.parameters):
                                    _high_priority_flag = True
                    
                    if _high_priority_flag:
                        high_priority_goal_paths.append(copy.copy(path))
                    else:
                        low_priority_goal_paths.append(copy.copy(path))
            
                # [TIMING SECTION 01b_05 - END]
                #_current_section01b_05_start = datetime.datetime.now()
                _current_section01b_05_end = datetime.datetime.now()
                _current_section_elapsed = _current_section01b_05_end - _current_section01b_05_start
                _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                _TIMING_DEBUG2['section_01b_05'] += _current_section_elapsed_seconds

            
            else:
                goal_paths = []
                path_ctr = 0
                
                # [TIMING SECTION 01b_04a - START]
                _current_section01b_04a_start = datetime.datetime.now()

                _all_simple_paths = nx.all_simple_paths(gg,valid_start_state_label,current_goal_label)
                
                #_len_all_simple_paths = len(list(copy.copy(_all_simple_paths)))
                #if(_len_all_simple_paths > 0):
                #    print("[...] _all_simple_paths: " + str(_len_all_simple_paths))
                #    print(list(copy.copy(_all_simple_paths)))
                #    input()
                
                
                # [TIMING SECTION 01b_04a - END]
                #_current_section01b_04a_start = datetime.datetime.now()
                _current_section01b_04a_end = datetime.datetime.now()
                _current_section_elapsed = _current_section01b_04a_end - _current_section01b_04a_start
                _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                _TIMING_DEBUG2['section_01b_04a'] += _current_section_elapsed_seconds
                
                for path in _all_simple_paths:
                    path_ctr += 1
                    _high_priority_flag = False
                    #print("Path: " + str(path_ctr) + " = " + str(path))

                    # [TIMING SECTION 01b_04 - START]
                    _current_section01b_04b_start = datetime.datetime.now()
                    
                    action_list = []
                    for somelabel in path:
                        action_list.append(gg.node[somelabel]['body'].action)
                        
                        if not _high_priority_flag:
                            for someobj in object_list:
                                if str(someobj) in str(gg.node[somelabel]['body'].action.parameters):
                                    _high_priority_flag = True
                    
                    if _high_priority_flag:
                        high_priority_goal_paths.append(copy.deepcopy(action_list))
                    else:
                        low_priority_goal_paths.append(copy.deepcopy(action_list))
                    
                    
                    goal_paths.append(copy.deepcopy(action_list))
                    
                    # [TIMING SECTION 01b_04b - END]
                    #_current_section01b_04b_start = datetime.datetime.now()
                    _current_section01b_04b_end = datetime.datetime.now()
                    _current_section_elapsed = _current_section01b_04b_end - _current_section01b_04b_start
                    _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                    _TIMING_DEBUG2['section_01b_04b'] += _current_section_elapsed_seconds
                
                    #print("len(high_priority_goal_paths): " + str(len(high_priority_goal_paths)))
                    #print("len(low_priority_goal_paths): " + str(len(low_priority_goal_paths)))
                
                # [X] Disable memoization in favor of path prioritization
                _GOAL_GRAPH_PATHS[_gg_paths_label] = copy.deepcopy(goal_paths)
                    
                # [X] Get paths from the first valid state encountered
                if path_ctr > 0:
                    break
    
        
        #   get all paths to current_goal_label
        #   extend goal_paths
        
        #return copy.deepcopy(goal_paths)
    
    
    def getAllPaths(self, current_state:set, current_node=None, remaining_goals=[],max_runtime_mins=8):
        'Returns a list of Action objects'
        
        all_paths = []
        chosen_goals = []
        _force_break = False
        
        #print("current state: ")
        #print(current_state)
        #for something in current_state:
        #    print(something)
        #print("-----")
        #input()
        
        _TIMING_DEBUG2 = {}
        _TIMING_DEBUG2['section_01b_01'] = 0
        _TIMING_DEBUG2['section_01b_02'] = 0   
        _TIMING_DEBUG2['section_01b_03'] = 0   
        _TIMING_DEBUG2['section_01b_04a'] = 0   
        _TIMING_DEBUG2['section_01b_04b'] = 0   
        _TIMING_DEBUG2['section_01b_05'] = 0   
        
        # 0. Valid start states
        
        # [TIMING SECTION 01b_01 - START]
        _current_section01b_01_start = datetime.datetime.now()
        
        
        # 0.1a Multiple (sorted) valid states
        valid_start_state_labels = self.getValidStartStates(current_state)
        
        # 0.1b Multiple (randomized) valid states
        #random.shuffle(self.gg_goal_nodes_label_list)
        
        #_start = self.getValidStartState(current_state, mode="random")
        #if _start is not None:
        #    valid_start_state_labels = [_start]
        #else:
        #    valid_start_state_labels = []
        
        
        if len(valid_start_state_labels) == 0:
            print("[...!] No valid states in Goal Graph")
            return all_paths

        # [TIMING SECTION 01b_01 - END]
        #_current_section01b_01_start = datetime.datetime.now()
        _current_section01b_01_end = datetime.datetime.now()
        _current_section_elapsed = _current_section01b_01_end - _current_section01b_01_start
        _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
        _TIMING_DEBUG2['section_01b_01'] += _current_section_elapsed_seconds
            
        # 0.2 Closest valid state
        #valid_start_state_label = self.getClosestValidStartState(current_state)
        
        #if valid_start_state_label is None:
        #    print("[...!] No valid states in Goal Graph")
        #    return all_paths
        gg = self.goal_graph
        
        
        
        
        # 0. Unified Goals
        #random.shuffle(self.gg_goal_nodes_label_list)
        #print("gg_goal_nodes_label_list: " + str(len(self.gg_goal_nodes_label_list)))
        #for current_goal_label in self.gg_goal_nodes_label_list:

        # [TIMING SECTION 01b_02 - START]
        _current_section01b_02_start = datetime.datetime.now()
        
        apparently_valid_count = 0
        
        # 2. Author Goals only
        random.shuffle(self.gg_goal_nodes_label_list_author)
        for current_goal_label in self.gg_goal_nodes_label_list_author:
            #print("[...] " + str(current_goal_label))
            
            # Goal node action
            goal_node = gg.node[current_goal_label]['body']
            goal_action = goal_node.action
            
            if current_goal_label in valid_start_state_labels:
                apparently_valid_count += 1
                for some_author_goal in remaining_goals:
                    if some_author_goal in goal_node.partial_effect_state:
                        all_paths.append([goal_action])
                        break
                

            high_priority_goal_paths = []
            low_priority_goal_paths = []
            _testflag1 = False
            for some_author_goal in remaining_goals:
                #print("[...] some_author_goal" + str(some_author_goal))
                
                _add_path = False
                if some_author_goal in goal_node.partial_effect_state:
                    _add_path = True
                    
                    object_list = []
                    self.extractObjects(some_author_goal, object_list)
                    
                #if some_author_goal[0] == 'not':
                #    if some_author_goal[1] not in goal_node.partial_state:
                #        _add_path = True
                #else:
                #    if some_author_goal in goal_node.partial_state:
                #        _add_path = True
                        
                if _add_path:
                    #print("Adding path")
                    chosen_goals.append(current_goal_label)
                    # Paths
                    
                    
                    # [TIMING SECTION 01b_03 - START]
                    _current_section01b_03_start = datetime.datetime.now()
                    
                    self.getAllPathsFromCurrentToGoal(valid_start_state_labels,current_goal_label, object_list, high_priority_goal_paths, low_priority_goal_paths, _TIMING_DEBUG2=_TIMING_DEBUG2)
                    _testflag1 = True
                    # [TIMING SECTION 01b_03 - END]
                    #_current_section01b_03_start = datetime.datetime.now()
                    _current_section01b_03_end = datetime.datetime.now()
                    _current_section_elapsed = _current_section01b_03_end - _current_section01b_03_start
                    _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                    _TIMING_DEBUG2['section_01b_03'] += _current_section_elapsed_seconds
                    
                    if _TIMING_DEBUG2['section_01b_03'] >= max_runtime_mins * 60:
                        _force_break = True
                        break
                    
                    
                    #print("self.getAllPathsFromCurrentToGoal: " + str(len(goal_paths)))
                    #all_paths.extend(goal_paths)
            
            all_paths.extend(high_priority_goal_paths)
            all_paths.extend(low_priority_goal_paths)
            
            if _force_break:
                break
            #if(_testflag1):
            #    print("high_priority_goal_paths: " + str(len(high_priority_goal_paths)))
            #    print("low_priority_goal_paths: " + str(len(low_priority_goal_paths)))
            #    #input()
            #    _testflag1 = False
                
                    #print("goal_action: " + str(goal_action.getFunctionString()))
                #    print("NOT adding path")
                
        # [TIMING SECTION 01b_02 - END]
        #_current_section01b_02_start = datetime.datetime.now()
        _current_section01b_02_end = datetime.datetime.now()
        _current_section_elapsed = _current_section01b_02_end - _current_section01b_02_start
        _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
        _TIMING_DEBUG2['section_01b_02'] += _current_section_elapsed_seconds
        
        logstr = ""
        logstr += "," + str(_TIMING_DEBUG2['section_01b_01']) 
        logstr += "," + str(_TIMING_DEBUG2['section_01b_02']) 
        logstr += "," + str(_TIMING_DEBUG2['section_01b_03']) 
        logstr += "," + str(_TIMING_DEBUG2['section_01b_04a']) 
        logstr += "," + str(_TIMING_DEBUG2['section_01b_04b']) 
        logstr += "," + str(_TIMING_DEBUG2['section_01b_05']) 
        
        #print(logstr)
        util.log(_LOG_EXECUTION_LOGFILE[5], logstr, "line/txt", enabled=True)
        
        
        
        
        #input()
        
        #remaining_goals = current_node.achieved_author_goals
        
        # OLD APPROACH
        # 1. All other Goals
        #random.shuffle(self.gg_goal_nodes_label_list_others)
        #for current_goal_label in self.gg_goal_nodes_label_list_others:
        #    #print(current_goal_label)
        #    
        #    # Goal node action
        #    goal_node = gg.node[current_goal_label]['body']
        #    goal_action = goal_node.action
        #    
        #    for some_author_goal in remaining_goals:
        #        if some_author_goal in goal_node.partial_state:
        #            #print("Adding path")
        #            chosen_goals.append(current_goal_label)
        #            # Paths
        #            goal_paths = self.getAllPathsFromCurrentToGoal(valid_start_state_labels,current_goal_label,dp_parser)
        #            all_paths.extend(goal_paths)
        #
        #            all_paths.append([goal_action])
        #        #else:
        #        #    print("NOT adding path")
        #
        #
        #
        # 2. Author Goals
        #random.shuffle(self.gg_goal_nodes_label_list_author)
        #for current_goal_label in self.gg_goal_nodes_label_list_author:
        #    #print(current_goal_label)
        #    
        #    # Goal node action
        #    goal_node = gg.node[current_goal_label]['body']
        #    goal_action = goal_node.action
        #    
        #    for some_author_goal in remaining_goals:
        #        #print(str(type(some_author_goal)) + " : " + str(some_author_goal))
        #        #print(str(type(goal_node.partial_state)) + " : " + str(goal_node.partial_state))
        #        #input()
        #        if some_author_goal in goal_node.partial_state:
        #            #print("Adding path")
        #            chosen_goals.append(current_goal_label)
        #            # Paths
        #            goal_paths = self.getAllPathsFromCurrentToGoal(valid_start_state_labels,current_goal_label,dp_parser)
        #            all_paths.extend(goal_paths)
        #
        #            all_paths.append([goal_action])
        #        #else:
        #        #    print("NOT adding path")
                
    
        
        
        #print("..debug end")
        #input()
        
        #print("PATHS!")
        #for somepath in all_paths:
        #    print(somepath)
        #input()
        
        #print("getAllPaths: " + str(len(all_paths)))
        return all_paths
    
    def getNextSteps(self, current_state,action_pool, quantity=3, mode="random", dp_parser=None):
        
        qty_ctr = 0
        all_paths = []
        if mode == "random":
            
            for somenodelabel in action_pool:
                next_step = self.action_instance_dict[somenodelabel]
            
                if (dp_parser.preconditionSatisfied(next_step,current_state)):
                    
                    #print(type(next_step))
                    #input()
                    
                    all_paths.append([next_step])
                    qty_ctr += 1
                    
                    if qty_ctr == quantity:
                        break
            
        # Should return an Action objects
        # Returns a list of 1-length paths
        return all_paths
    
    #---->>>> [ PUBLIC METHODS ]
    
    #-------->>>> Goal Graph Methods
    
    def generateLoosePrerequisiteActions(self, predicate_list:list, pos_term=True, mode="positive_connection", debug=False):
        
        _debug_flag = False
        
        prerequisite_actions = []
        
        #if "marker" in str(predicate_list):
        #    _debug_flag = True
        #    
        #    print("predicate_list : " + str(predicate_list))
        #    print("[.>>---------]")
        
        for action_instance in self.action_instance_list:
            
            # [0] Populate ingore list if necessary
            ignore_list = []
            
            # [1] Retrieve aggregate effects
            aggregate_possible_positive_effects = self._ACTION_AGGREGATE_EFFECTS[action_instance.getFunctionString()][0]
            aggregate_possible_negative_effects = self._ACTION_AGGREGATE_EFFECTS[action_instance.getFunctionString()][1]
            
            # [2] Check if all predicates in predicate_list are present in aggregate_possible_positive_effects / aggregate_possible_negative_effects
            
            predicate_list_score = 0
            #print("--")
            
            if debug:
                if "travel" in action_instance.getFunctionString():
                    print("\t\n")
                    print("\tpredicate_list: " + str(predicate_list))
                    print("\t---")
                    print("\tAssessing score :: " + action_instance.getFunctionString())
                    print("\t" + str(aggregate_possible_positive_effects))
                    print("\t" + str(aggregate_possible_negative_effects))
                    print("\t=====")
            
            # [3a] Positive connection approach
            if mode == "positive_connection":
                for predicate_term_tuple in predicate_list:
                    #print(predicate_term_tuple)
                    
                    if predicate_term_tuple[0] == [self.domainproblem._TRUE]:
                        predicate_list_score += 1
                
                        if debug:
                            if "travel" in action_instance.getFunctionString():
                                print("\t[TRUE] found")
                        continue
                    elif predicate_term_tuple[0].lower() == self.domainproblem._NOT_OPERATOR:
                        pos_term = False
                        _predicate_term = predicate_term_tuple[1]
                    else:
                        pos_term = True
                        _predicate_term = predicate_term_tuple
                        
                    
                    _predicate_term_label = _predicate_term[0]                
                    # [2.0] Adjacency is assumed true
                    if _predicate_term_label == "adjacent":
                        predicate_list_score += 1
                    # [2.1] Handle equality
                    
                    elif _predicate_term_label.lower() == self.domainproblem._EQUAL_OPERATOR:
                        #print("=")
                        #print(_predicate_term)
                        #input()
                        if debug:
                            if "travel" in action_instance.getFunctionString():
                                print("\tAssessing equality...")
                        if pos_term:
                            if str(_predicate_term[1]) == str(_predicate_term[2]):
                                predicate_list_score += 1
                                
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tequals found: " + str(_predicate_term))
                                        
                            else:
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +0 : " + str(_predicate_term))
                
                        else:
                            if str(_predicate_term[1]) != str(_predicate_term[2]):
                                predicate_list_score += 1
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tnot equals found: " + str(_predicate_term))
                                        
                            else:
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +0 : " + str(_predicate_term))
                
                    # [2.X] Others        
                    else:
                        # _predicate_term --> from child node (or current node of the current layer
                        # aggregate_possible_positive_effects of possible new node
                        
                        if pos_term:
                            #if (str(_predicate_term) in aggregate_possible_positive_effects) or (str(_predicate_term) not in aggregate_possible_negative_effects):
                            #    predicate_list_score += 1
                            if str(_predicate_term) in aggregate_possible_positive_effects: 
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +1 : " + str(_predicate_term))
                                predicate_list_score += 1
                            else:
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +0 : " + str(_predicate_term))
                            #if str(_predicate_term) in aggregate_possible_negative_effects:
                            #    predicate_list_score -= 1
                
                        else:
                            #if (str(_predicate_term) in aggregate_possible_negative_effects) or (str(_predicate_term) not in aggregate_possible_positive_effects):
                            #    predicate_list_score += 1
                            if str(_predicate_term) in aggregate_possible_negative_effects:
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +1 : " + str(_predicate_term))
                
                                predicate_list_score += 1
                            else:
                                if debug:
                                    if "travel" in action_instance.getFunctionString():
                                        print("\tscore +0 : " + str(_predicate_term))
                
                            #if str(_predicate_term) in aggregate_possible_positive_effects:
                            #    predicate_list_score -= 1
            
            # [3b] No-negative connection approach
            elif mode == "negative_connection":
            
            # [3c]
            
                for predicate_term_tuple in predicate_list:
                    #print(predicate_term_tuple)
                    
                    # [2.1] Pre-processing
                    if predicate_term_tuple[0] == [self.domainproblem._TRUE]:
                        #predicate_list_score += 1
                        continue
                    elif predicate_term_tuple[0].lower() == self.domainproblem._NOT_OPERATOR:
                        pos_term = False
                        _predicate_term = predicate_term_tuple[1]
                    else:
                        pos_term = True
                        _predicate_term = predicate_term_tuple
                
                    # [2.2] Equality handling
                    _predicate_term_label = _predicate_term[0]                
                    if _predicate_term_label.lower() == self.domainproblem._EQUAL_OPERATOR:
                        #print("=")
                        #print(_predicate_term)
                        #input()
                        if pos_term:
                            if str(_predicate_term[1]) != str(_predicate_term[2]):
                                predicate_list_score -= 1
                                break
                
                        else:
                            if str(_predicate_term[1]) == str(_predicate_term[2]):
                                predicate_list_score -= 1
                                break
                    
                    # [2.X] Others        
                    else:
                        if pos_term:
                            if str(_predicate_term) in aggregate_possible_negative_effects: 
                                predicate_list_score -= 1
                                break
                
                        else:
                            if str(_predicate_term) in aggregate_possible_positive_effects:
                                predicate_list_score -= 1
                                break
            
            #=======
            
            _score = predicate_list_score / len(predicate_list)
            
            # [3.X] Strict scoring
            #if predicate_list_score > 0:
            #    _add_flag = True
            
            if debug:
                if "travel" in action_instance.getFunctionString():
                    print("\tScore: " + str(predicate_list_score) + "/" + str(len(predicate_list)))
            
            if mode == "positive_connection":
                _add_flag = False
                if predicate_list_score > len(predicate_list):
                    #print("[...] generateLoosePrerequisiteActions: Score overflow")
                    _add_flag = True
                elif predicate_list_score == len(predicate_list):
                    #if "travel" in action_instance.getFunctionString():
                    #    print("[...] generateLoosePrerequisiteActions: Score ok")
                    _add_flag = True
                #else:
                #    print("[...] generateLoosePrerequisiteActions: Score underflow")
                #    print(action_instance.getFunctionString() + ":" + str(predicate_list_score))
                #    
                #    for something in predicate_list:
                #        print("\t"+str(something))
                #    
                #    print("---")
                    
                # [3.X] Relaxed scoring (percentage)
                #elif _score >= 0.9:
                # [3.X] Relaxed scoring (flat rate)
                elif (predicate_list_score >= (len(predicate_list) - _GG_CONNECTION_RULE_ALLOWANCE)) and (predicate_list_score >= 0):

                    if ("rm_" in action_instance.getFunctionString()) and (_debug_flag):
                        print("[...] "+action_instance.getFunctionString()+" : " + str(predicate_list_score))
                    _add_flag = True
                    
                    
            elif mode == "negative_connection":
                _add_flag = True
                if predicate_list_score < 0:
                    _add_flag = False
                
            if ((not (action_instance.name in ignore_list)) and _add_flag):
                prerequisite_actions.append(action_instance)
            else:
                pass
                
                
            #if "friendly" in action_instance.name:
            #    print("NO-GO: " + action_instance.name)
            #    print("predicate_list_score:" + str(predicate_list_score))
            #    print(predicate_list)
            #    input()
            #else:
            #    print(action_instance.name)
                
                
        return copy.deepcopy(prerequisite_actions)
    
    def generateRigidGoalGraph(self, max_layers = _MAX_GOAL_GRAPH_LAYERS, update=False):
        
        
        #-------->> Internal functions
        
        #   Handles partial_state definition
        def addNewLayer(action_list:list, new_layer:list, current_graph:DiGraph, layer_number:int, child_node:GoalGraphNode = None, goal_flag = "others"):
            #if layer_number == 0:
                
            
            #print(" [...>>] Size action_list: " + str(len(action_list)))
            #for action in action_list:

            #args = []
            #for ctr in range(0,len(action_list)):
            #    args.append([new_layer, current_graph, layer_number, child_node, goal_flag])

            for action in action_list:
                
                raw_label = action.getFunctionString()
                layer_label = str(layer_number) + "-" + raw_label
                
                #------------------------
                # Heuristic that determines if an action 
                # can be included in the goal graph
                
                #passed_heuristic = True
                #pass_rate = 1.0
                #   48031 GG nodes
                #pass_rate = 0.5
                #pass_rate = 0.3
                #GG nodes
                #   45503
                #   45583
                #pass_rate = 0.2
                #pass_rate = 0.1
                #   38881
                #pass_rate = 0.01
                #   14123
                
                #pass_result = random.uniform(0, 1)
                #print(pass_result)
                #if pass_result <= pass_rate:
                #    passed_heuristic = True
                #else:
                #    passed_heuristic = False
                passed_heuristic = True
                #------------------------
                
                if passed_heuristic:
                    if raw_label not in self.goal_graph_master_list:
                        # TODO:
                        # Need to revisit master list functionality
                        #print(" [.....>>] raw_label : " + raw_label)
                        self.goal_graph_master_list[raw_label] = action
                        
                    else:
                        #print(" [...] Master list duplicate:" + raw_label)
                        
                        #continue
                        pass
                        
                    #print(" [...] New node")
                    #print("\t" + str(new_label) + "::" + str(layer_number))
                    new_node = GoalGraphNode()
                    new_node.action = action
                    new_node.partial_precon_state = []
                    new_node.partial_effect_state = []
                    new_node.label = layer_label
                        
                    if layer_label not in current_graph:
                        #print(" [.....>>] layer_label : " + layer_label)
                        
                        current_graph.add_node(layer_label,body=new_node,layer=layer_number)
                        self._GG_TOTAL_NODES += 1
                        self._CURRENT_LAYER_NODES += 1
                        
                        new_layer.append(new_node)
                        if new_node.action.name in self._GG_ACTION_DENSITY_DICT:
                            self._GG_ACTION_DENSITY_DICT[new_node.action.name] += 1
                        else:
                            self._GG_ACTION_DENSITY_DICT[new_node.action.name] = 1
                    else:
                        #print(" [...] Goal graph duplicate:" + raw_label)
                        pass
                        
                    
                    if not (child_node is None):
                        child_node_label = str(layer_number-1) + "-" + child_node.action.getFunctionString()
                        if (child_node_label in current_graph) and (layer_label in current_graph):
                            #print(" [...!!!] Add edge success")
                            current_graph.add_edge(layer_label, child_node_label)
                            
                            _gg_np_label = new_node.action.name + ">>" + child_node.action.name
                            if _gg_np_label not in _GOAL_GRAPH_NODE_PAIRS:
                                _GOAL_GRAPH_NODE_PAIRS[_gg_np_label] = 1
                            else:
                                _GOAL_GRAPH_NODE_PAIRS[_gg_np_label] += 1
                            
                                
                        else:
                            raise Exception(" [!!!] ERROR: Invalid child node: " + child_node_label)
                        
                        
                        
                        # [1] Partial Precon State
                        util.listExtend(new_node.partial_precon_state,new_node.action.positive_preconditions)
                        util.listExtend(new_node.partial_precon_state,new_node.action.negative_preconditions)
                        
                        # [2] Partial Effect State
                        util.listExtend(new_node.partial_effect_state,new_node.action.possible_positive_effects)
                        util.listExtend(new_node.partial_effect_state,new_node.action.possible_negative_effects)
                        
                        #temp_list = []
                        #util.listExtend(temp_list,child_node.partial_state)
                        #
                        # [1] Preconditions
                        #util.listExtend(temp_list,new_node.action.positive_preconditions)
                        #for some_neg_effect in new_node.action.negative_preconditions:
                        #    util.listRemove(temp_list,[some_neg_effect[1]])
                        #
                        # [2] Effects
                        #util.listExtend(temp_list,new_node.action.possible_positive_effects)
                        #for some_neg_effect in new_node.action.possible_negative_effects:
                        #    util.listRemove(temp_list,[some_neg_effect[1]])
                            
                            
                        #try:
                        #    #print(child_node.action.negative_preconditions)
                        #    #input()
                        #    util.listRemove(temp_list,child_node.action.negative_preconditions[1])
                        #except IndexError:
                        #    pass

                        #util.listExtend(temp_list,new_node.action.positive_effects)
                        #try:
                        #    util.listRemove(temp_list,child_node.action.negative_preconditions[1])
                        #except IndexError:
                        #    pass
                        
                        #if len(new_node.action.negative_effects > 0):
                        #try:
                        #    util.listRemove(temp_list,new_node.action.negative_effects[1])
                        #except IndexError:
                        #    pass
                            
                        
                        #new_node.partial_state = temp_list
                    else:
                        #new_node.partial_state.extend(new_node.action.positive_preconditions)
                        # [1] Partial Precon State
                        util.listExtend(new_node.partial_precon_state,new_node.action.positive_preconditions)
                        util.listExtend(new_node.partial_precon_state,new_node.action.negative_preconditions)
                        
                        # [2] Partial Effect State
                        util.listExtend(new_node.partial_effect_state,new_node.action.possible_positive_effects)
                        util.listExtend(new_node.partial_effect_state,new_node.action.possible_negative_effects)
                        
                        _gg_np_label = new_node.action.name + ">>ROOT_LAYER"
                        if _gg_np_label not in _GOAL_GRAPH_NODE_PAIRS:
                            _GOAL_GRAPH_NODE_PAIRS[_gg_np_label] = 1
                        else:
                            _GOAL_GRAPH_NODE_PAIRS[_gg_np_label] += 1
                        
                        
                    if layer_number == 0:
                        if not (layer_label in self.gg_goal_nodes_label_list):
                            self.gg_goal_nodes_label_list.append(layer_label)
                            
                        if goal_flag == "author":
                            if not (layer_label in self.gg_goal_nodes_label_list_author):
                                self.gg_goal_nodes_label_list_author.append(layer_label)
                        
                        if goal_flag == "others":
                            if not (layer_label in self.gg_goal_nodes_label_list_others):
                                self.gg_goal_nodes_label_list_others.append(layer_label)
                            
                            
                else:
                    # Failed heuristic
                    #print("[...] Failed Heuristic")
                    pass
                        
                pass
            
        #   Still uses generateLoosePrerequisiteActions(PREDICATE_STRING: str)
        def buildGoalGraph(current_graph:DiGraph, current_layer:list, layer):
            
            #build current layer
            if layer >= max_layers:
                #print("max gg layer")
                #input()
                return
            elif layer == 0:
                # Root layer found, populate with intentions

                
                # TRY APPROACH: make goal graph from ALL possible intentions
                #for intention in self.all_possible_intentions:
                
                # OLD APPROACH: only make goal graph out of EXISTING intentions
                # >>>> All character goals
                #print("////===self.all_intentions")
                #for intention in self.all_intentions:
                #    #print(" [...>] character intention: " + str(intention))
                #    #print(" [...>] character intention result: " + str(intention[1]))
                #    
                #    if("[['not'" in str(intention[1])):
                #        pos_term=False
                #    else:
                #        pos_term=True
                    
                    #pre_actions = self.generateLoosePrerequisiteActions(intention[1],pos_term=pos_term)
                    #addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="author")
                
                # Debugging
                #print("////===self.domainproblem.positive_goals")
                #for somegoal in self.domainproblem.positive_goals:
                #    #print(" [...>] [+] author goal: " + str([self.identity_predicate,somegoal]))
                #    intention = [self.identity_predicate,somegoal]
                #    pre_actions = self.generateLoosePrerequisiteActions([intention[1]],pos_term=True)
                #    addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="others")
                
                
                
                #input()
                #print("////===self.domainproblem.negative_goals")
                #for somegoal in self.domainproblem.negative_goals:
                #    #print(" [...>] [-] author goal: " + str([self.identity_predicate,[self.domainproblem._NOT_OPERATOR, somegoal]]))
                #    intention = [self.identity_predicate,somegoal]
                #    #print(intention)
                #    #print([intention[1]])
                #    pre_actions = self.generateLoosePrerequisiteActions([intention[1]],pos_term=False)
                #    addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="author")
                    
                for intention in self.all_intentions:
                    pre_actions = self.generateLoosePrerequisiteActions(intention[1])
                    addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="others")
                    
                for somegoal in self.domainproblem.positive_goals:
                    #print("self.domainproblem.positive_goals")
                    #print(somegoal)
                    pre_actions = self.generateLoosePrerequisiteActions([somegoal])
                    addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="author")
                    
                for somegoal in self.domainproblem.negative_goals:
                    pre_actions = self.generateLoosePrerequisiteActions([somegoal])
                    addNewLayer(pre_actions, current_layer, current_graph, layer, goal_flag="author")
                    #addNewLayer(pre_actions, new_layer, current_graph, layer, current_node)
                    
                #print(" [...] Layer: " + str(layer) + " : " + str(self._CURRENT_LAYER_NODES))
                #print(" [...>>] prereq_action_cache: " + str(len(self.prereq_action_cache)))
                
                #print("Drawing goal graph")
                #self.drawGoalGraph(max_layers)
                
                buildGoalGraph(current_graph, current_layer, layer+1)
                #raise Exception("Stop")
                
            else:
                # Other layers
                # 1. loop through current_graph
                new_layer = []
                self._CURRENT_LAYER_NODES = 0
                found_flag = False
                current_layer_size = len(current_layer)
                current_node_ctr = 0
                for current_node in current_layer:
                    #print(" [...] Other layer: " + current_node.action.getFunctionString())
                    #1.1 loop through preconditions
                    #print("////===current_node.action.positive_preconditions")
                    #for pos_precon in current_node.action.positive_preconditions:
                    #    #print(pos_precon)
                    #    pre_actions = self.generateLoosePrerequisiteActions([pos_precon], pos_term=True)
                    #    #all_action_count += len(pre_actions)
                    #    # 2. Populate next_layer
                    #    if len(pre_actions) > 0:
                    #        found_flag = True
                    #        addNewLayer(pre_actions, new_layer, current_graph, layer, current_node)
                    #print("////===current_node.action.negative_preconditions")
                    #for neg_precon in current_node.action.negative_preconditions:
                    #    #print(neg_precon)
                    #    pre_actions = self.generateLoosePrerequisiteActions([neg_precon], pos_term=False)
                    #    #all_action_count += len(pre_actions)
                    #    # 2. Populate next_layer
                    #    if len(pre_actions) > 0:
                    #        found_flag = True
                    #        addNewLayer(pre_actions, new_layer, current_graph, layer, current_node)
                    
                    all_preconditions = current_node.action.positive_preconditions + current_node.action.negative_preconditions
                    
                    #if "travel" in current_node.action.getFunctionString():
                    #    print(" [...] Other layer: " + current_node.action.getFunctionString())
                    #    print(" [...] all_preconditions:")
                    #    for something in all_preconditions:
                    #        print("\t" + str(something))
                    #    print("========================//?")
                    #input()
                    
                    debug = False
                    #if "travel" in current_node.action.getFunctionString():
                    #    print("=====")
                    #    print("Trying to chain with: " + current_node.action.getFunctionString())
                    #    debug = True
                    
                    pre_actions = self.generateLoosePrerequisiteActions(all_preconditions, debug=debug)
                    
                    #print("========================//? == oof")
                    #input()
                    
                    #all_action_count += len(pre_actions)
                    # 2. Populate next_layer
                    if len(pre_actions) > 0:
                        found_flag = True
                        addNewLayer(pre_actions, new_layer, current_graph, layer, current_node)
                    #else:
                    #    print("[...] No found goal graph contribution: " + current_node.action.getFunctionString())
                    #    input()
                # 3. Call buildGoalGraph(buildGoalGraph, layer+1)
                if not found_flag:
                    #
                    #input()
                    return
                    #raise Exception(" [!!!] ERROR: Ran out of road... no more prerequisite actions available")
                print(" [...] Layer: " + str(layer) + " : " + str(self._CURRENT_LAYER_NODES) + "/" + str(len(current_graph.nodes())))
                #input()
                #for somenode in new_layer:
                #    for somepredicate in somenode.partial_state:
                #        print(somepredicate)
                #    print("---")
                #input()
                #print(" [...>>] prereq_action_cache: " + str(len(self.prereq_action_cache)))
                
                #print("Drawing goal graph")
                #self.drawGoalGraph(max_layers)
                #print(str(len(gg.nodes())))
                
                buildGoalGraph(current_graph, new_layer, layer+1)
            return
            
        def createAggregateEffects():
            
            self._ACTION_AGGREGATE_EFFECTS = {}
            
            for action_instance in self.action_instance_list:
                #print(action_instance.getFunctionString())
                #input()
                
                aggregate_possible_positive_effects = str(copy.deepcopy(action_instance.possible_positive_effects))
                aggregate_possible_negative_effects = str(copy.deepcopy(action_instance.possible_negative_effects))
                
                
                # =====================================
                # [1] Create separate possible effect per !var-object pair
                if "['!" in str(action_instance.possible_positive_effects):
                
                    for replacer in self.domainproblem.objects:
                        temp_possible_positive_effects = copy.deepcopy(action_instance.possible_positive_effects)
                        _replace_flag = False
                        
                        for some_effect in temp_possible_positive_effects:
                            if "['!" in str(some_effect):
                                p_ctr = 0
                                for target in some_effect:
                                    if p_ctr == 0:
                                        pass
                                    else:
                                        if ("!" in target[0]) and (self.domainproblem.typeIsOfType(replacer[1],target[1])):
                                            some_effect[p_ctr] = copy.deepcopy(replacer)
                                            _replace_flag = True
                                    p_ctr += 1
                        
                        if _replace_flag:
                            aggregate_possible_positive_effects += ";" + str(temp_possible_positive_effects)
                            
                if "['!" in str(action_instance.possible_negative_effects):
                
                    for replacer in self.domainproblem.objects:
                        temp_possible_negative_effects = copy.deepcopy(action_instance.possible_negative_effects)
                        _replace_flag = False
                        
                        for some_effect in temp_possible_negative_effects:
                            if "['!" in str(some_effect):
                                p_ctr = 0
                                for target in some_effect:
                                    if p_ctr == 0:
                                        pass
                                    else:
                                        if ("!" in target[0]) and (self.domainproblem.typeIsOfType(replacer[1],target[1])):
                                            some_effect[p_ctr] = copy.deepcopy(replacer)
                                            _replace_flag = True
                                    p_ctr += 1
                        
                        if _replace_flag:
                            aggregate_possible_negative_effects += ";" + str(temp_possible_negative_effects)
                
                
                
                # =====================================
                # [2] Add implied effects
                
                #if "travel" in action_instance.getFunctionString():
                #    print("action_instance.getFunctionString() : " + action_instance.getFunctionString())
                #    print(aggregate_possible_positive_effects)
                #    print(aggregate_possible_negative_effects)
                #    input()
                    
                    
                
                implied_effects = []
                for some_precon in action_instance.positive_preconditions:
                    if str(some_precon) not in str(action_instance.possible_negative_effects):
                        implied_effects.append(some_precon)
                
                if implied_effects != []:        
                    aggregate_possible_positive_effects += ";"+str(implied_effects)

                #if "travel" in action_instance.getFunctionString():
                #    print(implied_effects)

                
                implied_effects = []
                for some_precon in action_instance.negative_preconditions:
                    if str(some_precon) not in str(action_instance.possible_positive_effects):
                        implied_effects.append(some_precon)
                
                if implied_effects != []:        
                    aggregate_possible_negative_effects += ";"+str(implied_effects)
                
                #if "travel" in action_instance.getFunctionString():
                #    print(implied_effects)
                    
                
                self._ACTION_AGGREGATE_EFFECTS[action_instance.getFunctionString()] = [aggregate_possible_positive_effects,aggregate_possible_negative_effects]
            
        #=============================================
            
        print(str(datetime.datetime.now()) + ": >> Start goal graph generation... update:["+str(update)+"]")
        logstr = "Start goal graph generation... [NO SAVE]"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        start_execution = datetime.datetime.now()

        #-------->> Method body        
        if update:
            self.instantiateIntentions()
            
        else:
            self.goal_graph = DiGraph()
            self.goal_graph_master_list = {}
            self.goal_graph_master_list_complement = {}
            #self.goal_graph_master_list_complement_notravel = {}
            self.action_instance_dict_travel = {}
            # TODO: Modify instantiation routine to cater to only a handful of actor variables
            #variable_dict ={}
            #variable_dict['']
            
            self.instantiateActions()
            self.instantiatePredicates()
            self.instantiateIntentions()
            
        self.all_intentions = self.domainproblem.getAllIntentions()
        
        print(" [...] All intentions: ")
        for someintention in self.all_intentions:
            print("\t" + str(someintention))
        print(" [...] Size action_instance_list: " + str(len(self.action_instance_list)))
        #actor_intentions = self.domainproblem.getActorIntentions("gargax")
        
        createAggregateEffects()
        buildGoalGraph(self.goal_graph, [], 0)
        #print("Drawing goal graph")
        #self.drawGoalGraph(max_layers)
                
        # [...] Build complement
        for some_action_instance in self.action_instance_list:
            
            # [Normal complement]
            if not (some_action_instance.getFunctionString() in self.goal_graph_master_list):
            
                self.goal_graph_master_list_complement[some_action_instance.getFunctionString()] = copy.deepcopy(some_action_instance)
            
            # [Travel-only actions]
            if some_action_instance.name == 'travel':
                #print(some_action_instance)
                self.action_instance_dict_travel[some_action_instance.getFunctionString()] = copy.deepcopy(some_action_instance)
        
        logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
        now = datetime.datetime.now()
        logfile.write(str(datetime.datetime.now()) + ": Goal graph nodes: " + str(self._GG_TOTAL_NODES) + "\n")
        _LOG_VARIABLES[0] = self._GG_TOTAL_NODES
        
        print(" [...] Size self.goal_graph: " + str(self.goal_graph.number_of_nodes()))

        logfile.write(str(datetime.datetime.now()) + ": Goal graph action inventory:\n")
        
        print(" [...] Goal graph action inventory")
        total_ctr = 0
        for key, value in self._GG_ACTION_DENSITY_DICT.items():
            print("\t" + str(key) + ":" + str(value))
            logfile.write("\t" + str(key) + ":" + str(value)+ "\n")
            total_ctr += value
        print("\t--------------")
        print("\t"+str(total_ctr))
        
        logfile.write("\t--------------\n")
        logfile.write("\t"+str(total_ctr)+"\n")
        
        logfile.close()
        
        print(str(datetime.datetime.now()) + ": >> Done goal graph generation.")
        logstr = "Done goal graph generation."
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        
        end_execution = datetime.datetime.now()
        
        elapsed_time = end_execution - start_execution
        elapsed_seconds = elapsed_time.total_seconds()
        elapsed_minutes = elapsed_time.total_seconds() / 60
        
        logstr = "\t" + str(elapsed_seconds)+ " second/s"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        logstr = "\t" + str(elapsed_minutes)+ " minute/s"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        
        print(str(datetime.datetime.now()) + ": Goal graph generation DONE\n")
        print(str(datetime.datetime.now()) + ": Goal graph generation execution time:")
        print("\t" + str(elapsed_seconds)+ " second/s")
        print("\t" + str(elapsed_minutes)+ " minute/s")
        
        #print("Drawing goal graph")
        #self.drawGoalGraph(max_layers)
        
        logstr = "Goal Graph node pairs:\n"
        
        for key, value in _GOAL_GRAPH_NODE_PAIRS.items():
            logstr += "\t" + str(key) + ":" + str(value) + "\n"
        util.log(_LOG_EXECUTION_LOGFILE[4], logstr, "line/txt", enabled=True)
        
        
        
        return

    def __filterGoalGraph(self, goal_graph:DiGraph, action_name:str, mode:int):
        result_list = []
        for somenode in goal_graph.nodes():
        
            # Mode 1: Filter out action_name
            if mode == 1:
                if goal_graph.node[somenode]['body'].action.name != action_name:
                    result_list.append(goal_graph.nodes[somenode])
            
        return result_list
        
    def filterActionInstances(self, name=None, function_string=None):
        output_list = []
        
        for some_action in self.action_instance_list:
            addFlag = False
            if not(name is None):
                if some_action.name == name:
                    output_list.append(some_action)
                    addFlag = True
            
            if not(function_string is None):
                if (some_action.getFunctionString() == function_string) and (not addFlag):
                    output_list.append(some_action)
        s
        return output_list
    
    def drawGoalGraph(self, layers):
    
        #plt.title('Decision Target: (intends  talia (not (single talia)))')
        
        #nx.draw_networkx_nodes(self.goal_graph,pos=nx.spring_layout(self.goal_graph), node_size=10, node_color='blue')
        #nx.draw_networkx_edges(self.goal_graph,pos=nx.spring_layout(self.goal_graph))
        #nx.draw_networkx_labels(self.goal_graph, pos=nx.spring_layout(self.goal_graph), font_size=6)
        
        #nx.draw(self.goal_graph, pos=nx.random_layout(self.goal_graph),node_size=10, node_color='blue', with_labels=True, font_size=10)
        
        #layer_ctr = 0
        #while layer_ctr <= layers:
        #    current_layer = []
        #    
        #    for graph_node in self.goal_graph.nodes:
        #        if graph_node['layer']
        #        pass
        #
        #
        #    layer_ctr += 1

        
        layer_dict = {}
        pos = dict()
        for label,data in self.goal_graph.nodes(data=True):
            #print(u)
            #print(v)
            #print(str(label) + ":" +str(data))
            #print(graph_node[layer])
            current_layer = data['layer']
            if current_layer not in layer_dict:
                layer_dict[current_layer] = [label]
            else:
                layer_dict[current_layer].append(label)
               
            #layer_dict
        current_layer = 0
        while current_layer < layers:
            if current_layer in layer_dict:
                pos.update( (n, (current_layer, i)) for i, n in enumerate(layer_dict[current_layer]) ) 
            current_layer += 1

        action_labels = dict()
        for n,data in self.goal_graph.nodes(data=True):
            if data['body'].action is None:
                action_labels[n] = "Current State"
            else:
                #action_labels[n] = data['body'].action.getFunctionString()            
                action_labels[n] = data['body'].label
        #pos.update( (n, (2, i)) for i, n in enumerate(Y) ) # put nodes from Y at x=2
        
        #nx.draw_networkx_nodes(self.goal_graph, pos=pos,node_size=14, node_color='blue')
        #nx.draw_networkx_labels(self.goal_graph, pos=pos, font_size=6)
        #nx.draw_networkx_edges(self.goal_graph, pos=pos, alpha=0.4)
        
        nx.draw_networkx_nodes(self.goal_graph, pos=pos,node_size=34, node_color='blue', alpha=0.4)
        nx.draw_networkx_labels(self.goal_graph, labels=action_labels, pos=pos, font_size=12)
        nx.draw_networkx_edges(self.goal_graph, pos=pos, alpha=0.4)        
        #print(layer_dict)
        
        #shells = []
        #current_layer = 0
        #while current_layer < layers:
        #    #nx.draw_networkx_nodes(self.goal_graph,nodelis
        #    shells.append(layer_dict[current_layer])
        #    current_layer += 1
        #    
        #pos = 
        #
        #nx.draw(self.goal_graph, pos=nx.shell_layout(self.goal_graph, shells),node_size=10, node_color='blue', with_labels=True, font_size=10)
        
        
        plt.show()

    def drawPlanGraph(self, plan_graph:DiGraph, goal_nodes:list, layers, mode="default"):
    
        #plt.title('Decision Target: (intends  talia (not (single talia)))')
        
        #nx.draw_networkx_nodes(self.goal_graph,pos=nx.spring_layout(self.goal_graph), node_size=10, node_color='blue')
        #nx.draw_networkx_edges(self.goal_graph,pos=nx.spring_layout(self.goal_graph))
        #nx.draw_networkx_labels(self.goal_graph, pos=nx.spring_layout(self.goal_graph), font_size=6)
        
        #nx.draw(self.goal_graph, pos=nx.random_layout(self.goal_graph),node_size=10, node_color='blue', with_labels=True, font_size=10)
        
        #layer_ctr = 0
        #while layer_ctr <= layers:
        #    current_layer = []
        #    
        #    for graph_node in self.goal_graph.nodes:
        #        if graph_node['layer']
        #        pass
        #
        #
        #    layer_ctr += 1

        
        layer_dict = {}
        pos = dict()
        for label,data in plan_graph.nodes(data=True):
            #print(u)
            #print(v)
            #print(str(label) + ":" +str(data))
            #print(graph_node[layer])
            current_layer = data['layer']
            
            if current_layer not in layer_dict:
                layer_dict[current_layer] = [label]
            else:
                layer_dict[current_layer].append(label)
               
            #layer_dict
        current_layer = 0
        
        #print("[1] layer_dict")
        #print(layer_dict)
        while current_layer < layers:
            if current_layer in layer_dict:
                pos.update( (n, (current_layer, i)) for i, n in enumerate(layer_dict[current_layer]) ) 
            current_layer += 1
            
        action_labels = dict()
        
        
        for n,data in plan_graph.nodes(data=True):
            if data['body'].last_action is None:
                action_labels[n] = "Current State"
            else:
                if mode == "default":
                    action_labels[n] = data['body'].last_action.getFunctionString()
                elif mode == "author_goal_score":
                    action_labels[n] = data['body'].author_goal_score
            
            
        color_map = []
        #for node in plan_graph:
        for n,data in plan_graph.nodes(data=True):
        
            for some_goal in goal_nodes:
                #print(" some_goal_tuple : " + str(some_goal_tuple))
                #print(str(data['body'].label) + " == " + str(some_goal))
                
                
                #if mode == "default":
                if data['body'].label == str(some_goal):
                    color_map.append('red')
                else:
                    color_map.append('blue')
                #elif mode == "author_goal_score":
                    
        #nx.draw(G,node_color = color_map,with_labels = True)
            
        #pos.update( (n, (2, i)) for i, n in enumerate(Y) ) # put nodes from Y at x=2
        
        nx.draw_networkx_nodes(plan_graph, pos=pos,node_size=34, node_color = color_map, alpha=0.4)
        nx.draw_networkx_labels(plan_graph, labels=action_labels, pos=pos, font_size=12)
        nx.draw_networkx_edges(plan_graph, pos=pos, alpha=0.4)
        
        #print(layer_dict)
        
        #shells = []
        #current_layer = 0
        #while current_layer < layers:
        #    #nx.draw_networkx_nodes(self.goal_graph,nodelis
        #    shells.append(layer_dict[current_layer])
        #    current_layer += 1
        #    
        #pos = 
        #
        #nx.draw(self.goal_graph, pos=nx.shell_layout(self.goal_graph, shells),node_size=10, node_color='blue', with_labels=True, font_size=10)
        
        
        plt.show()
        #plt.show(block=False)
        #plt.savefig("Graph.png", format="PNG")
        pass
    
    #-------->>>> Predicate and Action Methods
    def instantiatePredicates(self):
        #-------->> Internal functions
        
        #-------->> Method body
        
        #---->> Predicates
        # Generate predicate instances
        # Possibly prune unlikely / impossible predicates
        #   > based on personality and current knowledgebase
        
        self.predicate_instance_dict = {}
        
        # bulk creation
        predicate_instance_bulk = []
        bulk_ctr = 0
        for predicate_obj in self.domainproblem.predicates:
            
            predicate_def = predicate_obj.definition
            #print(" [...>>>] Predicate: " + str(predicate_def))
            
            # >>> Instantiation exceptions:
            if predicate_def[0] == self.domainproblem._EQUAL_OPERATOR:
                pass
            elif predicate_def[0] == self.domainproblem._FORALL_OPERATOR:
                pass
            elif predicate_def[0] in self.domainproblem._INTENTIONALITY_OPERATORS:
                pass
            elif    ((predicate_def[0] == self.domainproblem._IF_OPERATOR) or 
                    (predicate_def[0] == self.domainproblem._IFELSE_OPERATOR)):
                pass
            else:
                # replace variables with all combinations of object instances
                ctr = 0
                error_flag = False
                
                
                for predicate_def_elem in predicate_def:
                    
                    if ctr == 0:
                        predicate_def_name = predicate_def[ctr]
                        
                        #if predicate_def_name in self.domainproblem._INTENTIONALITY_OPERATORS:
                        #    # Intentionality has special treatment. Ignore here.
                        #    break
                        #else:
                        
                        #predicate_instance_bulk.append([predicate_def_name])
                        new_bulk_entry = []
                        new_bulk_entry.append(predicate_def_name)
                        
                    else:
                        # [predicate_def_elem_var, predicate_def_elem_type]
                        # predicate_def_elem[0] = predicate_def_elem_var
                        # predicate_def_elem[1] = predicate_def_elem_type
                        #print(" [...>>>] Term: " + str(predicate_def_elem))
                        
                        #--------------------------------------
                        predicate_def_elem_list = []
                        # All objects loop
                        for object in self.domainproblem.objects:
                            #if predicate_def_elem[1] == "place":
                            #    print(" [...>>>>>] Object: " + str(object) + " :: " + str(predicate_def_elem))
                                
                            if self.domainproblem.typeIsOfType(object[1], predicate_def_elem[1]):
                                if object not in predicate_def_elem_list:
                                    #print("[4]")
                                    predicate_def_elem_list.append(object)
                        # append all valid objects to the bulk
                        
                        if len(predicate_def_elem_list) <= 0:
                            #print("####>>>> Empty 'predicate_def_elem_list'")
                            #print(predicate_instance_bulk[bulk_ctr])
                            #print("####>>>> ")
                            error_flag = True
                            break
                        else:
                            new_bulk_entry.append(predicate_def_elem_list)
                        #--------------------------------------
                    ctr += 1
                    
                    
                if error_flag:
                    continue
                predicate_instance_bulk.append(new_bulk_entry)
        
        # [end] for predicate_obj in self.domainproblem.predicates:
        
        #print(" [...>] Predicate Bulk: ")
        # bulk definition done:
        for predicate_instance_elem in predicate_instance_bulk:
            predicate_instance_list = []
            
            #print("==========================")
            #print(" [+++]" + str(predicate_instance_elem))
            ctr = 0
            for term in predicate_instance_elem:
                if ctr == 0:
                    predicate_instance_elem_name = term
                    #print(" [... NAME -->]")
                    #print(predicate_instance_elem_name)
                    predicate_instance_list = [[predicate_instance_elem_name]]
                else:
                    object_instance_list = term
                    result_list = []
                    self.__populateWith(predicate_instance_list,object_instance_list,result_list)
                    predicate_instance_list = result_list
                    #if bulk_ctr == 5:
                    #if ctr == 3:
                    #    raise Exception("Stop")
                    
                ctr += 1
            
            result_obj_list = []
            
            #print("###>>>>>>>>>>>>>>")
            #print("predicate_instance_elem")
            #print(predicate_instance_elem)
            #print("###>>>>>>>>>>>>>>")
            #print("RESULT LIST")
            #print(result_list)
            #print("###>>>>>>>>>>>>>>")
            #print("predicate_instance_bulk")
            #for something in predicate_instance_bulk:
            #    print(something)
            #    print("____")
            
            if len(result_list) <= 0:
                #print("... empty. Continuing")
                continue
            
            
            predicate_obj = self.domainproblem.getPredicateObj(result_list[0][0])
            for result_elem in result_list:
                
                temp_result = copy.deepcopy(result_elem)
                temp_result.pop(0)
                #self.name = name
                #self.parameters = parameters
                #self.definition = definition
                #self.primary_obj = primary_obj
                #self.secondary_obj = secondary_obj
                #self.humanreadables = humanreadables
                
                new_result_obj_parameters = copy.deepcopy(temp_result)
                new_result_obj_definition = self.__replaceVariables(
                                                                predicate_obj.definition,
                                                                predicate_obj.parameters,
                                                                temp_result
                                                            )
                new_result_obj_primary_obj = self.__replaceVariables(
                                                                predicate_obj.primary_obj,
                                                                predicate_obj.parameters,
                                                                temp_result
                                                            )
                new_result_obj_secondary_obj = self.__replaceVariables(
                                                                predicate_obj.secondary_obj,
                                                                predicate_obj.parameters,
                                                                temp_result
                                                            )
                
                new_result_obj_humanreadables = self.__replaceVariables(
                                                                predicate_obj.humanreadables,
                                                                predicate_obj.parameters,
                                                                temp_result
                                                            )
                                                            
                #print("Template:")
                #print(predicate_obj.name            )
                #print(predicate_obj.parameters      )
                #print(predicate_obj.definition      )
                #print(predicate_obj.primary_obj     )
                #print(predicate_obj.secondary_obj   )
                #print(predicate_obj.humanreadables  )
                #print("=================")
                #print(predicate_obj.name            )
                #print(new_result_obj_parameters      )
                #print(new_result_obj_definition      )
                #print(new_result_obj_primary_obj     )
                #print(new_result_obj_secondary_obj   )
                #print(new_result_obj_humanreadables  )
                #
                #input()
                new_result_obj = Predicate(
                                            predicate_obj.name,
                                            new_result_obj_parameters,
                                            new_result_obj_definition,
                                            new_result_obj_primary_obj,
                                            new_result_obj_secondary_obj,
                                            new_result_obj_humanreadables
                                        )
                result_obj_list.append(new_result_obj)
                                                    
            
            #self.predicate_instance_dict.extend(result_obj_list)
            for some_result_obj in result_obj_list:
                self.predicate_instance_dict[some_result_obj.getFunctionString()] = copy.deepcopy(some_result_obj)
    
    def __replaceVariables(self, input_list:list, parameter_label_list:list, parameter_instance_list:list):
    
        temp_list = copy.deepcopy(input_list)
        output_list = []
        for temp_element in temp_list:
            if type(temp_element) is list:
                temp_element = self.__replaceVariables(temp_element, parameter_label_list, parameter_instance_list)
            elif type(temp_element) is str:
            
                p_flag = False
                if (temp_element[0] == '"') and \
                   (temp_element[-1] == '"'):
                    p_flag = True
                    temp_element = temp_element.replace('"','')
                ctr=0
                for some_label in parameter_label_list:
                    temp_element = temp_element.replace(some_label[0], parameter_instance_list[ctr][0])
                    ctr+=1
                    
                if p_flag:
                    temp_element = '"' + temp_element + '"'
            else:
                raise Exception("Type error, list or str expected; " + str(type(temp_elem)) + " found.")
            output_list.append(temp_element)
        
        return output_list
       
    def instantiateActions(self):
        
        #-------->> Internal functions
        def partialEvaluatePreconditions(action_instance:Action):
            
            valid_predicates = ['equals']
            output_flag = False
            curr_flag = False
            
            for somepos_precon in action_instance.positive_preconditions:
                if somepos_precon[0] == self.domainproblem._NOT_OPERATOR:
                    precon = somepos_precon[1]
                else:
                    precon = somepos_precon
                    
                if precon[0] in valid_predicates:
                    eval_operator = dp_parser.domainproblem._AND_OPERATOR
                    temp_state = set()
                    
                    curr_flag = self.planner_parameters['dp_parser'].evalPropositionTree(eval_operator,precon,temp_state)
                    
                    if not curr_flag:
                        #print("POSITIVE")
                        #print(precon)
                        #print("----")
                        #print(action_instance)
                        return False
                
            for someneg_precon in action_instance.negative_preconditions:
                if someneg_precon[0] == self.domainproblem._NOT_OPERATOR:
                    precon = someneg_precon[1]
                else:
                    precon = someneg_precon
                    
                if precon[0] in valid_predicates:
                    eval_operator = dp_parser.domainproblem._AND_OPERATOR
                    temp_state = set()
                    
                    curr_flag = not self.planner_parameters['dp_parser'].evalPropositionTree(eval_operator,precon,temp_state)
                    
                    if not curr_flag:
                        #print("NEGATIVE")
                        #print(precon)
                        #print("----")
                        #print(action_instance)
                        return False
            
            return True
            
            
        def instantiateAction(action_def:Action, action_instance_list:list, dp_parser:DomainProblemParser):
            parameters = action_def.parameters
         
            # [1] -->> Parameter Bulk creation
            parameter_instance_bulk = []
            for parameter_elem in parameters:
                parameter_instance = []
                # All objects loop
                for object in self.domainproblem.objects:
                    if self.domainproblem.typeIsOfType(object[1], parameter_elem[1]):
                        if object not in parameter_instance:
                            parameter_instance.append(object)
                # append all valid objects to the bulk
                parameter_instance_bulk.append(parameter_instance)
                
            # [2] -->> Parameter Bulk expansion
            #print(" [...>>] Bulk contents:")
            parameter_instance_list = []
            
            for parameter_instance_elem in parameter_instance_bulk:
                #print("[1] " + str(parameter_instance_elem))
                #print(parameter_instance_elem)
                
                result_list = []
                self.__populateWith(parameter_instance_list,parameter_instance_elem,result_list)
                parameter_instance_list = result_list
                #print("[2] " + str(result_list))
                #print("[2] ")
                #parameter_instance_list.extend(result_list)
                
            #for param_inst in parameter_instance_list:
            #    print(param_inst)
            
            instance_list_ctr = 0
            #print("..................................")
            #for parameter_instance_elem in parameter_instance_list:
            #    print(parameter_instance_elem)
            #print("..................................")
            #raise Exception("Stop")
            
            # [3] -->> Replace variables
            totalctr = 0
            successctr = 0
            for parameter_instance_elem in parameter_instance_list:
                totalctr += 1
                name = action_def.name
                parameters = parameter_instance_elem
                
                #print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                #print(parameters)
                #input()
                
                new_action_instance = dp_parser.createActionInstance(action_def, parameter_instance_elem)
                
                if new_action_instance is None:
                    #print("BREAK???")
                    break
                
                include_flag = partialEvaluatePreconditions(new_action_instance)
                
                # [6] Append to Action instance list
                if include_flag:
                    successctr += 1
                    action_instance_list.append(new_action_instance)
                    #print(" [...] Adding: " + new_action_instance.getFunctionString())
                else:
                    #action_instance_list.append(new_action_instance)
                    #print(" [...] Discarding: " + new_action_instance.getFunctionString())
                    pass
                
            pass
            
        #-------->> Method body
        
        # [IMPROVEMENT JUNCTION]
        #   generalize this?
        ignore_list = []
        ignore_list.append("trigger_itemlose")
        ignore_list.append("trigger_itemgain")
        
        # bulk creation
        #print(" [...>] Actions")
        dp_parser = DomainProblemParser(self.domainproblem)
        action_instance_list = []
        for action_def in self.domainproblem.actions:
            
            #print(" [...>>>] Name : " + action_def.name)
            if not (action_def.name in ignore_list):
                instantiateAction(action_def, action_instance_list, dp_parser)
            else:
                print(" [!..!] Ignored: " + action_def.name)
            
            #print(" [...>>>] --------------------------------------------")
            
            #somectr = 0
            #for someaction in action_instance_list:
            #    print(someaction.getFunctionString())
            #    somectr += 1
            #    if somectr >= 3:
            #        break
        
        #raise Exception("stop")
        self.action_instance_list = action_instance_list
        
        self.action_instance_dict = {}
        for some_action_instance in self.action_instance_list:
            self.action_instance_dict[some_action_instance.getFunctionString()] = copy.copy(some_action_instance)
        
        
        #action_instance_file = open("action_instance_list.txt","w+")
        #for action in action_instance_list:
        #    action_instance_file.write(action.getFunctionString() + "\n")
        #action_instance_file.close()
        
        #for action in self.action_instance_list:
        #    print(action)
        #raise Exception("Stop")
        return
    
    def instantiateIntentions(self):
        self.intentions_instance_dict = {}
        base_intention_obj = self.domainproblem.getPredicateObj(pddlglobals._INTENTIONALITY_OPERATORS[0])
        
        _ignore_list = ["adjacent"]
        
        for someactor in self.domainproblem.objects:
            #print(" [>>>]" + str(someactor))
            if self.domainproblem.isValidActor(someactor[0]):
                #print("    [V]" + str(someactor))
                for some_predicate_instance in self.predicate_instance_dict.values():

                    child_predicate_name = some_predicate_instance.name
                    if child_predicate_name in _ignore_list:
                        continue
                        
                    child_predicate_parameters = some_predicate_instance.parameters
                    child_predicate_fs = toFunctionString(child_predicate_name, child_predicate_parameters)
                    child_predicate_obj = self.predicate_instance_dict[child_predicate_fs]
                    child_predicate_hr = random.choice(child_predicate_obj.humanreadables).replace('"','')
                    

                    
                    #new_result_obj_humanreadables = self.__replaceVariables(
                    #                                                base_intention_obj.humanreadables,
                    #                                                base_intention_obj.parameters,
                    #                                                []
                    #                                            )
                    
                    #self.domainproblem.getPredicateDef
                    
                    _name             = self.domainproblem._INTENTIONALITY_OPERATORS[0]                               
                    _parameters       = [someactor, [some_predicate_instance.definition, pddlglobals._PREDICATE_TYPE]]
                    _definition       = []
                    _definition.append(_name)
                    _definition.extend(_parameters)
                    _primary_obj      = someactor
                    _secondary_obj    = []
                    
                    # Human Readable Strings
                    
                    _temp_result = self.__replaceVariables(
                                                                    base_intention_obj.humanreadables,
                                                                    base_intention_obj.parameters,
                                                                    [someactor, [child_predicate_hr, pddlglobals._PREDICATE_TYPE]]
                                                                )
                    _humanreadables   = []
                    _humanreadables.extend(_temp_result)
                    
                    intention_obj = Predicate(
                                        name            = _name             ,
                                        parameters      = _parameters       ,
                                        definition      = _definition       ,
                                        primary_obj     = _primary_obj      ,
                                        secondary_obj   = _secondary_obj    ,
                                        humanreadables  = _humanreadables
                                    )
                    
                    self.intentions_instance_dict[intention_obj.getFunctionString()] = copy.deepcopy(intention_obj)
                #<=======    
                    
        #for someintention in self.all_possible_intentions:
        #    print(someintention)
        #print(str(len(self.all_possible_intentions)))
        #input()
        #action_instance_file = open("action_instance_list.txt","w+")
        #for action in action_instance_list:
        #    action_instance_file.write(action.getFunctionString() + "\n")
        #action_instance_file.close()
        
        pass
    
    def verifyConsistency():
        return
    
    #-------->>>> Execute Planner
    
    def __hasUnexplainedStep(self, unexplained_steps: dict):
        for key, value in unexplained_steps.items():
            if unexplained_steps[key] == False:
                return True
        return False
    
    def intentionalPathModule(self, current_node:PlanGraphNode, end_node:PlanGraphNode, search_space:DiGraph, mode:str = "all", unexplained_steps:dict = {}, explained_steps:dict = {}, memoization_list:list = [] ):
        # Modes:
        #   TODO
        #   all         - Generate all paths
        #   shortest    - Return shortest paths
        #   longest     - Return longest paths
        
        # The input is a SUBGOAL node, and it will EXPLAIN the predecessors
        
        # Special mode:
        #   explain_all - Explain all nodes encountered
        
        if mode == "explain_all":
            # predecessor : PlanGraphNode instance
            #print(" [intentional] current_node.label" + str(current_node.label))
            
            for predecessor_label in search_space.predecessors(current_node.label):
                #print(search_space[predecessor])
                #print(predecessor)
                if search_space.nodes[predecessor_label] is not None:
                    predecessor_node = search_space.nodes[predecessor_label]['body']
                    #print(predecessor_node)
                    if predecessor_node.label not in memoization_list:
                        # [line 16]
                        #print(" [...] last_action: " + str(predecessor_node.last_action))
                        if not (predecessor_node.last_action is None):
                            predecessor_node_label = predecessor_node.last_action.getFunctionString()
                            if predecessor_node_label in unexplained_steps:
                                
                                # 1. Remove from unexplained_steps dict
                                del unexplained_steps[predecessor_node_label]
                                
                                # 2. Add to the explained steps dict
                                if not predecessor_node_label in explained_steps:
                                    explained_steps[predecessor_node_label] = []
                                
                                explained_steps[predecessor_node_label].append(end_node)
                                
                                #_all_simple_paths = nx.all_simple_paths(search_space,valid_start_state_label,end_node.label)
                                
                                
                                
                                #unexplained_steps[predecessor_node_label] = True
                                #    unexplained_steps.remove(predecessor_node.last_action)
                        
                        memoization_list.append(predecessor_node.label)
                        #print(" [...] " + str(predecessor_node.label) + " >> memoization_list")
                        self.intentionalPathModule(predecessor_node, end_node, search_space, mode, unexplained_steps, explained_steps, memoization_list)
                    else:
                        #print(" [.............>] " + str(predecessor_node.label) + " has already been checked")
                        pass
                else:
                    # do nothing if it's the root node (no predecessors)
                    pass
        else:
            raise Exception(" [!!!] Mode '"+mode+"' is not supported")
    
    
    def evalActionFitness(self, current_step:Action, current_state, total_goals=None, dp_parser=None):
        
        return_tuple = [0,0]
    
        #current_state = current_node.state
        result_state = dp_parser.applyAction(current_step, current_state)
        
        current_score = dp_parser.getGoalScore(current_state, total_goals)
        result_score =  dp_parser.getGoalScore(result_state, total_goals)
        #if result_score > 0:
        #    print("AHA: " + str(result_score) + " " + current_step.getFunctionString())
        #    input()
        delta = result_score - current_score
        
        return_tuple[0] = result_score
        return_tuple[1] = delta
        
        return return_tuple
    
    def __planningRoutineBFS(self, search_space:DiGraph, parameters:dict, max_runtime_mins=0, algorithm=None, ):
        
        def __evalStopCondition(search_space:DiGraph, parameters:dict, remaining_goals=None):
        
            #current_node                    = parameters['current_node']        
            unexplained_steps               = parameters['unexplained_steps']
            #found_intention_node_list       = parameters['found_intention_node_list']
            #current_layer                   = parameters['current_layer']
            #max_depth                       = parameters['max_depth']     
            #dp_parser                       = parameters['dp_parser']         
            #plan_root_node                  = parameters['plan_root_node']
            #personal_goals                  = parameters['personal_goals']    # identity's goals
            #achieved_intentions             = parameters['achieved_intentions']
            achieved_authors_goals          = parameters['achieved_authors_goals']
            found_authors_goals_node_list   = parameters['found_authors_goals_node_list']
            #nextstepsize                    = parameters['nextstepsize']
            #nextsteprange                   = parameters['nextsteprange']
            #mode                            = parameters['mode']
            
            # Goal count
            #if not (len(achieved_authors_goals) >= self.domainproblem.goal_count):
            #    print("GC fail: " + str(len(achieved_authors_goals)) + "/" + str(self.domainproblem.goal_count) + " -- " + str(len(search_space)))
            #    #print(achieved_authors_goals)
            #    return False
                
            #print(remaining_goals)
            
            if len(found_authors_goals_node_list) < self.personality.solutions_per_goal:
                #print("GC fail: No search space nodes fulfilled ALL author goals")
                #print("SPG fail: " + str(len(found_authors_goals_node_list)) + "/" + str(self.personality.solutions_per_goal) + " -- " + str(len(search_space)))
                #for something in achieved_authors_goals:
                #    print(something)
                return False
            
            # Solutions per goal
            #for key, value in achieved_authors_goals.items():
            #    if value < self.personality.solutions_per_goal:
            #        #print("SPG fail")
            #        return False
            
            # TODO-BOOKMARK
            # Unexplained steps
            # - Check for actions that have NO consent or actor type = nature (doesnt need to be explained)
            for some_node in found_authors_goals_node_list:
                total_ctr = 0
                unexplained_ctr = 0
                
                # [???] Has catch
                #try:
                #    for some_action_tuple in search_space.nodes[some_node[0]]['body'].plan:
                #        #print(some_action_tuple)
                #        #input()
                #        some_action_label = some_action_tuple[1].getFunctionString()
                #        
                #        total_ctr += 1
                #        if some_action_label in unexplained_steps:
                #            if unexplained_steps[some_action_label] == False:
                #                #print(some_action_tuple[1].getFunctionString())
                #                
                #                # << OLD APPROACH: Terminate if there is ONE unexplained step
                #                #return False
                #                
                #                # << TRY APPROACH: Set a thresholds
                #                unexplained_ctr += 1
                #except Exception:
                #    print("WARNING - Key Error: " + str(some_node[0]))
                #    print("---")
                #    for key, value in search_space.nodes.items():
                #        print(str(key))
                #    print("---")
                #    print(search_space.nodes[some_node[0]]['body'].plan)
                #    print("---")
                #    print(unexplained_steps)
                #    print("---")
                #    print(some_action_label)
                #    print("---")
                #    
                #    #print("Something went wrong, press any key")
                #    #input()
                #    pass
                
                # [???] No catch catch
                for some_action_tuple in search_space.nodes[some_node[0]]['body'].plan:
                    #print(some_action_tuple)
                    #input()
                    some_action_label = some_action_tuple[1].getFunctionString()
                    
                    total_ctr += 1
                    if some_action_label in unexplained_steps:
                        if unexplained_steps[some_action_label] == False:
                            #print(some_action_tuple[1].getFunctionString())
                            
                            # << OLD APPROACH: Terminate if there is ONE unexplained step
                            #return False
                            
                            # << TRY APPROACH: Set a thresholds
                            unexplained_ctr += 1
                
                if total_ctr == 0:
                    logstr = "[..!] Zero-action chapter found"
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    
                    return True
                    
                unexplained_percentage = (unexplained_ctr / total_ctr) * 100
                #print(str(unexplained_percentage) + " > " + str(_UNEXPLAINED_THRESHOLD))

                if unexplained_percentage > self.personality.unexplained_threshold:
                    print(" [...] Unexplained steps: "+str(unexplained_ctr)+"/"+str(total_ctr)+ " "+str(unexplained_percentage)+"%; FAILED")
                    return False
            
            

                
            # Passed all tests
            print("PASSED ALL TESTS")
            return True
                
        #def __evalActionFitness(current_step:Action):
        #    
        #    return_tuple = [0,0]
        #
        #    current_state = current_node.state
        #    result_state = dp_parser.applyAction(current_step, current_state)
        #    
        #    current_score = dp_parser.getGoalScore(current_state, total_goals)
        #    result_score =  dp_parser.getGoalScore(result_state, total_goals)
        #    #if result_score > 0:
        #    #    print("AHA: " + str(result_score) + " " + current_step.getFunctionString())
        #    #    input()
        #    delta = result_score - current_score
        #    
        #    return_tuple[0] = result_score
        #    return_tuple[1] = delta
        #    
        #    return return_tuple
        
        def __evalAllGoalsAchieved(
            search_space=None, 
            current_node=None, 
            author_goals_list=None,
            achieved_authors_goals=None,
            found_authors_goals_node_list=None,
            unexplained_steps=None, 
            explained_steps=None
        ):
            
            goal_remove_list = []
            temp_author_goals_list = copy.deepcopy(author_goals_list)
            #print(temp_author_goals_list)
            #print("//")
            # [line 11]
            # [start] loop through all known goals of the new node
            
            goal_count = 0
            
            temp_goal_list = []
            #current_node.achieved_author_goals = []
            
            #for some_goal in current_node.known_goals:
            #    temp_goal_list.append(some_goal)
            
            # [O] 
            for some_goal in temp_author_goals_list:
                _temp = [self.identity, [some_goal,"predicate"]]
                if _temp not in temp_goal_list:
                    temp_goal_list.append(copy.copy(_temp))

            #print(current_node.known_goals)
            #print(temp_author_goals_list)
            #print("===")
            #print(temp_goal_list)
            #input()
            author_goals_list
            #print(current_node.known_goals)
            #input()
            
            for some_goal in temp_goal_list:
            #for some_goal in current_node.known_goals:
                #print("known goal: " + str(some_goal))
                some_name = "goal_parsing"
                # ['heather', [['not', ['alive', ['rory', 'person']]], 'predicate']]
                not_flag = False
                
                #print(some_goal)
                #print("////")
                if some_goal[1][0][0] == dp_parser.domainproblem._NOT_OPERATOR:
                    temp_parameters = copy.deepcopy(some_goal[1][0][1])
                    temp_name = temp_parameters.pop(0)
                    not_flag = True
                else:
                    temp_parameters = copy.deepcopy(some_goal[1][0])
                    temp_name = temp_parameters.pop(0)
                    
                
                eval_operator = dp_parser.domainproblem._AND_OPERATOR
                eval_operand = some_goal[1][0]
                eval_value = dp_parser.evalPropositionTree(eval_operator, eval_operand, current_node.state, 1, name = some_name)
                
                if eval_value == True:
                    #print("true!")
                    #print("temp_author_goals_list")
                    #print(temp_author_goals_list)
                    if some_goal[1][0] in temp_author_goals_list:
                        #print("---")
                        #temp_author_goals_list.remove(some_goal[1][0])
                        
                        #print("found author goal: " + str(some_goal[1][0]) + " ("+str(type(some_goal[1][0]))+")")
                        #for _something in current_node.achieved_author_goals:
                        #    print("\t"+str(_something)+" ("+str(type(_something))+")")
                        
                        goal_count += 1
                        if(some_goal[1][0] not in current_node.achieved_author_goals):
                            current_node.achieved_author_goals.append(copy.deepcopy(some_goal[1][0]))
                        
                        some_goal_str = str(some_goal[1][0])
                        if not (some_goal_str in achieved_authors_goals):
                            achieved_authors_goals[some_goal_str] = 1
                        else:
                            achieved_authors_goals[some_goal_str] += 1
                        
                        
                    fulfilled_intention_function_str = toFunctionString(temp_name, temp_parameters)
                    goal_remove_list.append(some_goal)
                    
                    #if (current_node.label,some_goal) not in found_intention_node_list:
                    #    found_intention_node_list.append((current_node.label, some_goal))
                    
                    # [1] Update achieved_intentions -- a per-predicate list
                    if some_goal[1][0] not in achieved_intentions:
                        achieved_intentions.append(some_goal[1][0])
                    
                    # [X] Deactivated step explanation
                    self.intentionalPathModule(current_node, current_node, search_space, "explain_all", unexplained_steps, explained_steps, [])
                    
                    if fulfilled_intention_function_str in self.predicate_instance_dict:
                        current_node.intentions_achieved.append(( some_goal[1][0], self.predicate_instance_dict[fulfilled_intention_function_str], not_flag ))
                    
                    elif fulfilled_intention_function_str in self.intentions_instance_dict:
                        current_node.intentions_achieved.append(( some_goal[1][0], self.intentions_instance_dict[fulfilled_intention_function_str], not_flag ))
                    else:
                        raise Exception("AAAAAAAAAAAAA")
                    
                else:
                    #print(" [.......>] some_goal not met : " + str(some_goal))
                    pass
                    
            current_node.author_goal_score = goal_count + len(current_node.achieved_author_goals)
            # [2] Update found_intention_node_list -- a list of nodes that achieved ALL author goals
            
            
            remaining_goals =[]
            for some_goal in  author_goals_list:
                if some_goal not in current_node.achieved_author_goals:
                    remaining_goals.append(copy.deepcopy(some_goal))
            
            if remaining_goals == []:
            #if goal_count >= len(author_goals_list):
                if current_node.label not in found_intention_node_list:
                    print("FOUND: " + str(current_node.label) + " | " + str(current_node.layer))
                    found_intention_node_list.append(current_node.label)
                    
                print(">>>>>>>>>>>: " + str(current_node.label))
                found_authors_goals_node_list.append(
                    (   copy.copy(current_node.label), 
                        None, 
                        copy.deepcopy(current_node.plan),
                        copy.deepcopy(plan_root_node.state)
                    )
                )
                
                #found_authors_goals_node_list.append(current_node.label)
                    
            # [end] loop through all known goals of the new node
            
            # [line 13] - delayed removal. May affect the previous loop if removed immediately
            #print("goal_remove_list:")
            #print(goal_remove_list)
            #print("---")
            #print("current_node.known_goals:")
            #print(current_node.known_goals)
            #print("---")
            for some_goal in goal_remove_list:
                #print(some_goal)
                if some_goal in current_node.known_goals:
                    current_node.known_goals.remove(some_goal)
                    
        #--------------------------------------------------------------------------------------------------------
        
        # Timer start
        bfs_start_execution = datetime.datetime.now()
        
        unexplained_steps               = parameters['unexplained_steps']
        explained_steps                 = parameters['explained_steps']
        found_intention_node_list       = parameters['found_intention_node_list']
        #current_layer                   = parameters['current_layer']
        max_depth                       = parameters['max_depth']     
        dp_parser                       = parameters['dp_parser']
        plan_root_node                  = parameters['plan_root_node']
        personal_goals                  = parameters['personal_goals']    # identity's goals
        achieved_intentions             = parameters['achieved_intentions']
        achieved_authors_goals          = parameters['achieved_authors_goals']
        found_authors_goals_node_list   = parameters['found_authors_goals_node_list']
        nextstepsize                    = parameters['nextstepsize']
        nextsteprange                   = parameters['nextsteprange']
        mode                            = parameters['mode']
        raffle_list                     = parameters['raffle_list']
        coreplanner_start_execution     = parameters['coreplanner_start_execution']
        chapter_str                     = parameters['chapter_str']
        
        bfs_queue = []
        discovered_nodes = []
        terminate_flag = False
        total_goals = []
        total_goals.extend(self.domainproblem.positive_goals)
        total_goals.extend(self.domainproblem.negative_goals)
        
        bfs_queue.append((plan_root_node.label, 0,0))
        
        author_goals_list = self.domainproblem.goals
        
        
        parameters['self']  = self
        parameters['total_goals'] = total_goals
        
        loop_back_ctr = 0
        plateau = -1
        
        run_id = self.run_id
        #========================================
        # Early author goal evaluation
        
        # [Check] : Evaluate author's goal
        #author_goals_list = dp_parser.domainproblem.goals
        author_goals_list = self.domainproblem.goals
        
        current_node = plan_root_node
        some_name = "goal_parsing"

        
        #__evalAllGoalsAchieved(author_goals_list, search_space)
        
        _temp_goal_list = []
        for some_goal in current_node.known_goals:
            _temp_goal_list.append(some_goal)
        
        for some_goal in author_goals_list:
            _temp = [self.identity, [copy.deepcopy(some_goal),"predicate"]]
            if _temp not in _temp_goal_list:
                _temp_goal_list.append(copy.copy(_temp))
        
        
        current_node.known_goals = copy.deepcopy(_temp_goal_list)
        
        #print("[Pre-start Known goals:")
        #for something in current_node.known_goals:
        #    print("\n" + str(something))
        #print("===============")
        __evalAllGoalsAchieved(
                    search_space                    = search_space                  ,
                    current_node                    = current_node                  ,
                    author_goals_list               = author_goals_list             ,
                    achieved_authors_goals          = achieved_authors_goals        ,
                    found_authors_goals_node_list   = found_authors_goals_node_list ,
                    unexplained_steps               = unexplained_steps             ,
                    explained_steps                 = explained_steps              
                )

        # Add node to database
        self.saveNodeToDB(run_id, chapter_str, current_node)
                
        #print("[Post-start Known goals:")
        #for something in current_node.known_goals:
        #    print("\n" + str(something))
        #print("===============")
        plateau = current_node.author_goal_score
        
        
        #========================================
        #loop_try_ctr = 0
        #loop_back_ctr = 0
        
        #========================================
        _TIMING_DEBUG = {}
        _TIMING_DEBUG['section_01a'] = 0
        _TIMING_DEBUG['section_01b'] = 0
        _TIMING_DEBUG['section_02'] = 0
        _TIMING_DEBUG['section_03'] = 0
        _TIMING_DEBUG['section_04'] = 0
        _TIMING_DEBUG['section_05'] = 0
        _TIMING_DEBUG['section_06'] = 0
        _TIMING_DEBUG['section_07'] = 0
        
        while len(bfs_queue) > 0:
            
            # [TIMING SECTION 01a - START]
            _current_section01a_start = datetime.datetime.now()
            
            # Long-running kill-switch
            if max_runtime_mins > 0:
                bfs_current_execution = datetime.datetime.now()
                bfs_elapsed_time = bfs_current_execution - bfs_start_execution
                
                bfs_elapsed_seconds = bfs_elapsed_time.total_seconds()
                bfs_elapsed_minutes = bfs_elapsed_time.total_seconds() / 60
                
                if bfs_elapsed_minutes>max_runtime_mins:
                    logstr = " [....] Runtime threshold breached"
                    logstr += " [....>] bfs_queue: " + str(len(bfs_queue)) + "\n"
                    logstr += " [....>] achieved_authors_goals: \n"
                    for something in achieved_authors_goals:
                        logstr += str(something) + "\n"
                    logstr += " [....>] search space: " + str(len(search_space.nodes()))
                    print(logstr)
                    util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
                    
                    break
        #<----------break
            
            start_execution = datetime.datetime.now()
            
            temp_exclude_list = []
            
            bfs_queue_pop = bfs_queue.pop(0)
            current_node_label = bfs_queue_pop[0]
            current_node = search_space.node[current_node_label]['body']
            goal_remove_list = []
            
            
            #__evalAllGoalsAchieved(
            #            search_space                    = search_space                  ,
            #            current_node                    = current_node                  ,
            #            author_goals_list               = author_goals_list             ,
            #            achieved_authors_goals          = achieved_authors_goals        ,
            #            found_authors_goals_node_list   = found_authors_goals_node_list ,
            #            unexplained_steps               = unexplained_steps             ,
            #            explained_steps                 = explained_steps              
            #        )
        
            
            now = datetime.datetime.now()
            if (now.minute % 2) == 0:
                
                current_log_entry_hh_mm = str(now.hour) + ":" + str(now.minute)
                
                if _LOG_LAST_ENTRY_TIMESTAMP[0] == current_log_entry_hh_mm:
                    pass
                else:
                    _LOG_LAST_ENTRY_TIMESTAMP[0] = current_log_entry_hh_mm
                    graph_nodes_str = str(search_space.number_of_nodes())
                    
                    #logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
                    #now = datetime.datetime.now()
                    #logfile.write(str(datetime.datetime.now()) + ": layer: "+str(current_layer)+"; nodes: "+graph_nodes_str+";\n")
                    #logfile.close()
                    
                    logstr = "layer: "+str(current_node.layer)+"; nodes: "+graph_nodes_str
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=True)
            
            
            #print(">>>----")
            #print("current_node.address : " + str(current_node.address))
            #print("current_node.achieved_author_goals:")
            #for something in current_node.achieved_author_goals:
            #    print("\t"+ str(something))
            

            
            remaining_goals =[]
            for some_goal in  author_goals_list:
                if some_goal not in current_node.achieved_author_goals:
                    remaining_goals.append(copy.deepcopy(some_goal))
            
            
            if __evalStopCondition(search_space, parameters, remaining_goals=remaining_goals):
                print(" [...] Done! __evalStopCondition")
                terminate_flag = True
                break
            else:
                logstr = "search_space: ["+str(len(search_space.nodes()))+"]  || bfs_queue: ["+str(len(bfs_queue))+"] || remaining_goals: ["+str(len(remaining_goals))+"] || \n" + str(remaining_goals)
                print(logstr)
                util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)

                #print("search_space: ["+str(len(search_space.nodes()))+"]  || bfs_queue: ["+str(len(bfs_queue))+"] || remaining_goals: ["+str(len(remaining_goals))+"]")
            
            # [TIMING SECTION 01a - END]
            #_current_section_start = datetime.datetime.now()
            _current_section01a_end = datetime.datetime.now()
            _current_section_elapsed = _current_section01a_end - _current_section01a_start
            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
            _TIMING_DEBUG['section_01a'] += _current_section_elapsed_seconds
            
            # [start][COREPROCESS]
            
            # [TIMING SECTION 01b - START]
            _current_section01b_start = datetime.datetime.now()
            
            # Goal Graph Single Path
            if algorithm in ["goalgraphpaths","ggp_dr1_hybrid"]:
                temp_state = copy.deepcopy(current_node.state)
                next_step_list = self.getRigidNextSteps(
                    current_state   = temp_state, 
                    size            = nextstepsize, 
                    mode            = 0, 
                    seed            = 0, 
                    steprange       = nextsteprange, 
                    dp_parser       = dp_parser
                )
            # Goal Graph Multiple Paths    
            elif algorithm in ["goalgraphmultipath"]:
                temp_state = copy.deepcopy(current_node.state)
                
                #remaining_goals = author_goals_list.difference(current_node.achieved_author_goals)
                
                #print(author_goals_list)
                #print(current_node.achieved_author_goals)
                #print(remaining_goals)
                #print("====")
                #input()
                
                next_step_list = self.getAllPaths(
                    current_state   = temp_state, 
                    #dp_parser       = dp_parser,
                    current_node    = current_node,
                    remaining_goals = remaining_goals,
                    max_runtime_mins = max_runtime_mins
                )
                #print("\tnext_step_list: " + str(len(next_step_list)))
                
                #if len(next_step_list) > 100:
                #    print("[1]")
                #    print("Current State:")
                #    print(temp_state)
                #    
                #    print("[2]")
                #    print("Remaining Goals:")
                #    print(remaining_goals)
                #    
                #    print("[3]")
                #    print("next_step_list")
                #    
                #    for somepath in next_step_list:
                #        _path = "\t [>] "
                #        for somestep in somepath:
                #            _path += somestep.getFunctionString() + ","
                #        print(_path)
                    
                #print(next_step_list)
                #input()
                
            child_number = 0
            
            spawn_children = True
            action_cache_flag = False
            
            loop_try_ctr = 0
            #loop_back_ctr = 0
            
            tried_actions = []
            
            
            # [TIMING SECTION 01b - END]
            #_current_section_start = datetime.datetime.now()
            _current_section01b_end = datetime.datetime.now()
            _current_section_elapsed = _current_section01b_end - _current_section01b_start
            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
            _TIMING_DEBUG['section_01b'] += _current_section_elapsed_seconds

            
            if algorithm in ["goalgraphmultipath"]:
                
                # [TIMING SECTION 02 - START]
                _current_section02_start = datetime.datetime.now()
                
                if max_runtime_mins > 0:
                    bfs_current_execution = datetime.datetime.now()
                    bfs_elapsed_time =bfs_current_execution - coreplanner_start_execution
                    
                    bfs_elapsed_seconds = bfs_elapsed_time.total_seconds()
                    bfs_elapsed_minutes = bfs_elapsed_time.total_seconds() / 60
                    
                    if bfs_elapsed_minutes>max_runtime_mins:
                        logstr = " [....] Runtime threshold breached"
                        print(logstr)
                        util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
                        
                        
                        logstr = ""
                        logstr += "," + str(_TIMING_DEBUG['section_01a']) 
                        logstr += "," + str(_TIMING_DEBUG['section_01b']) 
                        logstr += "," + str(_TIMING_DEBUG['section_02']) 
                        logstr += "," + str(_TIMING_DEBUG['section_03']) 
                        logstr += "," + str(_TIMING_DEBUG['section_04']) 
                        logstr += "," + str(_TIMING_DEBUG['section_05']) 
                        logstr += "," + str(_TIMING_DEBUG['section_06']) 
                        logstr += "," + str(_TIMING_DEBUG['section_07']) 
                        
                        print(logstr)
                        util.log(_LOG_EXECUTION_LOGFILE[3], logstr, "line/txt", enabled=True)

                        
                        
                        return False
                # [goalgraphmultipath 1.] Cycle through the goal graph paths
                
                # DEBUG
                _debug = False
                #if len(next_step_list) > 100:
                #    _debug = True
                
                # [O] Guarantee a next step loop
                _terminate_guarantee_loop = False
                _guarantee_loop_ctr = 0
                while True:
                    if len(next_step_list) == 0:
                        print("[...] [WARNING] next_step_list is empty")
                        # Get random next step?
                        
                        # [Alt 1] Blind random next step.
                        
                        # [Alt 2] First step with +delta
                        action_pool = list(self.goal_graph_master_list.keys())
                        random.shuffle(action_pool)
                        
                        next_step_list = self.getNextSteps(current_node.state, action_pool, quantity=3, mode="random", dp_parser=dp_parser)
                        soft_plan_source = "RANDOM"
                        # [Alt 3] Highest +delta? --- seems like too much work for a random step.
                    else:
                        soft_plan_source = "GOAL GRAPH"
                    #print("...")
                    #for something in next_step_list:
                    #    stuff = ""
                    #    for some_action in something:
                    #        stuff += some_action.getFunctionString() + ","
                    #    print(stuff)
                    #print("...")
                    if _guarantee_loop_ctr > 2:
                        for something in next_step_list:
                            stuff = ""
                            for some_action in something:
                                stuff += some_action.getFunctionString() + ","
                            print("STUFF: " + stuff)
                        return False
                        print("Press any key")
                        input()
                    
                    _has_valid_step = False
                    _path_ctr = 0
                    for some_path in next_step_list:
                        _path_ctr += 1
                        
                        #if _debug:
                        #print("["+str(current_node.layer)+"] Current path: " + str(_path_ctr) + "/" + str(len(next_step_list)))
                        #_path = "\t [>] "
                        #for somestep in some_path:
                        #    _path += somestep.getFunctionString() + ","
                        #print(_path)
                        
                        # [TIMING SECTION 03 - START]
                        _current_section03_start = datetime.datetime.now()
                        
                        # [X] Disable loop_back_ctr
                        #if loop_back_ctr >= _MAX_LOOP_BACK:
                        #    #bfs_queue = [] #completely terminate chapter search
                        #    _terminate_guarantee_loop = True
                        #    _has_valid_step = True
                        #    break   # terminate search for current node, continue with the bfs_queue
                        
                        parent_node_address = current_node.address
                        #parent_node = search_space.nodes[current_node.label]['body']
                        parent_node = current_node
                        
                        # [goalgraphmultipath 2.] Per path, create a sequence of nodes without action_cache
                        next_step_ctr = 0
                        new_goal_graph_soft_plan = copy.deepcopy(some_path)
                        for next_step in some_path:
                        
                            # [TIMING SECTION 04 - END]
                            _current_section04_start = datetime.datetime.now()
                        
                            next_step_ctr += 1
                            # [goalgraphmultipath 3.] Per step (Action object), 
                            
                            #   [ggmp 3.0] Apply step/action to current node and create a new_node
                            #   [ggmp 3.0.1] Create new_node
                            #print("[...] next_step_ctr" + str(next_step_ctr))
                            child_number = len(list(search_space.successors(parent_node.label)))
                            new_node_address = parent_node_address + "-" + util.zeroStringPad(str(child_number),4)
                            parent_node_address = new_node_address
                            
                            current_layer = parent_node.layer+1
                            
                            if (current_layer >= (max_depth)):
                                #logstr = "Max depth reached. search_space: ["+str(len(search_space.nodes()))+"]  || bfs_queue: ["+str(len(bfs_queue))+"] || remaining_goals: ["+str(len(remaining_goals))+"]"
                                #print(logstr)
                                #util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
                                _terminate_guarantee_loop = True
                                _has_valid_step = True
                                break
                            
                            new_node_plan = copy.deepcopy(parent_node.plan)
                            new_node_last_action = next_step
                            new_node_state = copy.deepcopy(parent_node.state)
                            new_node_known_goals = copy.deepcopy(parent_node.known_goals)
                            new_node_layer = current_layer
                            new_node_label = ""
                            new_node_achieved_author_goals = copy.deepcopy(parent_node.achieved_author_goals)
                            
                            #[20201014-A-before]
                            #   [ggmp 3.0.2] Do some checks
                            if (dp_parser.preconditionSatisfied(next_step,parent_node.state)):
                                pass
                            else:
                                
                                #print("[....] Precondition not satisfied (step "+str(next_step_ctr)+"): " + next_step.getFunctionString())
                                #for something in parent_node.state:
                                #    print(something)
                                #print("====")
                                #for something in new_node.state:
                                #    print(something)
                                #print("====")
                                #input()
                                # [ggmp 3.0.1][break] Aborting path
                                break
                            
                            # [TIMING SECTION 04 - END]
                            #_current_section_start = datetime.datetime.now()
                            _current_section04_end = datetime.datetime.now()
                            _current_section_elapsed = _current_section04_end - _current_section04_start
                            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                            _TIMING_DEBUG['section_04'] += _current_section_elapsed_seconds
                            
                            
                            
                            # [TIMING SECTION 05 - START]
                            _current_section05_start = datetime.datetime.now()
                            
                            #   [ggmp 3.0.3] Apply the current action
                            
                            new_state = dp_parser.applyAction(next_step, new_node_state)
                            
                            if _debug:
                                print("\t\tApplied: " + next_step.getFunctionString())
                            
                            _has_valid_step = True
                            
                            raw_state_str = str(frozenset(sorted(new_state)))
                            new_node_label = str(hash(raw_state_str)) + "_" \
                                           + hashlib.blake2s(raw_state_str.encode('utf-8'),salt=run_id[0:8].encode('utf-8')).hexdigest()
                                         
                            new_node_state = frozenset(copy.copy(new_state))
                            _delete_allowed = False
                            
                            
                            new_node_plan.append((run_id + "_" + chapter_str + "|" + new_node_label, copy.deepcopy(next_step)))
                            new_action_cache = []
                            
                            # [Prune condition] : New state is the same as the root state
                            if new_node_label == plan_root_node.label: 
                                #print(" [...][Prune condition] : New state is the same as the root state : " + next_step.getFunctionString())
                                loop_back_ctr += 1
                                break
                                
                            # [Attach to an Existing Node]
                            elif new_node_label in search_space:
                                
                                existing_node = search_space.nodes[new_node_label]['body']
                                
                                if existing_node.layer <= parent_node.layer:
                                    #print(" [...] Attempting to add a node that has already been encountered")
                                    loop_back_ctr += 1
                                    break
                                elif existing_node.label == parent_node.label:
                                    #print(" [...][Prune condition][Same label] : Step has no effect to current state : " + next_step.getFunctionString())
                                    continue
                                else:
                                    
                                    #print(" [...] Attaching edge from layer " + str(parent_node.layer) + " to layer " + str(parent_node.layer))
                                    if not search_space.has_edge(parent_node, existing_node):
                                        search_space.add_edge(parent_node.label, existing_node.label)
                                        
                                        # Add edge to database
                                        from_node_label = run_id + "_" + chapter_str + "|" + parent_node.label
                                        to_node_label = run_id + "_" + chapter_str + "|" + existing_node.label
                                        
                                        self.saveEdgeToDB(run_id, from_node_label, to_node_label)
                                        
                                    parent_node = existing_node
                                    continue   
                            # [major step] Attach to Plan Graph
                            else:
                                #loop_back_ctr = 0
                                child_number += 1
                                _delete_allowed = True
                                new_node = PlanGraphNode(new_node_label, new_node_address, new_node_plan, new_node_state, new_node_last_action, new_node_known_goals, new_node_layer, new_goal_graph_soft_plan, soft_plan_source)
                                new_node.state = copy.deepcopy(new_node_state)
                                new_node.achieved_author_goals = new_node_achieved_author_goals
                                new_node.author_goal_score = -1
                                
                                # Serial approach
                                #print(" [...] Normally adding node and edge")
                                search_space.add_node(new_node.label, body=new_node, layer=current_layer)
                                search_space.add_edge(parent_node.label, new_node.label)
                                
                                
                                
                                # Add edge to database
                                from_node_label = run_id + "_" + chapter_str + "|" + parent_node.label
                                to_node_label = run_id + "_" + chapter_str + "|" + new_node.label

                                
                                
                                parent_node = new_node



                            # [TIMING SECTION 05 - END]
                            #_current_section_start = datetime.datetime.now()
                            _current_section05_end = datetime.datetime.now()
                            _current_section_elapsed = _current_section05_end - _current_section05_start
                            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                            _TIMING_DEBUG['section_05'] += _current_section_elapsed_seconds

                                    
                            # [TIMING SECTION 06 - START]
                            _current_section06_start = datetime.datetime.now()
                                    
                            #   [ggmp 3.3] goals have been met
                            #new_goal_list = dp_parser.getAllIntentions(new_state)
                            #new_node.known_goals = copy.deepcopy(new_goal_list)
                            #new_node.author_goal_score = -1
                            
                            #print("[Pre-in progress Known goals:")
                            #for something in current_node.known_goals:
                            #    print("\n" + str(something))
                            #print("===============")
                            __evalAllGoalsAchieved(
                                        search_space                    = search_space                  ,
                                        current_node                    = new_node                      ,
                                        author_goals_list               = author_goals_list             ,
                                        achieved_authors_goals          = achieved_authors_goals        ,
                                        found_authors_goals_node_list   = found_authors_goals_node_list ,
                                        unexplained_steps               = unexplained_steps             ,
                                        explained_steps                 = explained_steps              
                                    )

                            # Add node to database
                            self.saveNodeToDB(run_id, chapter_str, new_node)                                
                            self.saveEdgeToDB(run_id, from_node_label, to_node_label)



                            if __evalStopCondition(search_space, parameters, remaining_goals=remaining_goals):
                                print(" [...] Done! __evalStopCondition")
                                terminate_flag = True
                                break
                            else:
                                #logstr = "search_space: ["+str(len(search_space.nodes()))+"]  || bfs_queue: ["+str(len(bfs_queue))+"] || remaining_goals: ["+str(len(remaining_goals))+"]"
                                #print(logstr)
                                #util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
                                pass
                                    
                                    
                            #print("[Post-in progress Known goals:")
                            #for something in current_node.known_goals:
                            #    print("\n" + str(something))
                            #print("===============")
                            #if new_node.author_goal_score > plateau:
                            #    plateau = new_node.author_goal_score
                            
                            #if new_node.author_goal_score < plateau:
                            #    print("-----")
                            #    print(plan_root_node.label)
                            #    print(new_node.label)
                            #    print(len(search_space))
                            #    print(str(new_node.author_goal_score) + "/" + str(plateau))
                            #    print("-----")
                            #    search_space.remove_node(new_node.label)
                            #    child_number -= 1
                            #    break
                            #else:
                            #    plateau = new_node.author_goal_score
                            
                            # [TIMING SECTION 06 - END]
                            #_current_section_start = datetime.datetime.now()
                            _current_section06_end = datetime.datetime.now()
                            _current_section_elapsed = _current_section06_end - _current_section06_start
                            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                            _TIMING_DEBUG['section_06'] += _current_section_elapsed_seconds


                            # [TIMING SECTION 07 - START]
                            _current_section07_start = datetime.datetime.now()                        
                            
                            # [line 8] Step explanation
                            if len(next_step.agents) > 0:
                                next_step_label = next_step.getFunctionString()
                                
                                #print("----")
                                #print(next_step.agents)
                                #print(new_node.known_goals)
                                #print("----")
                                #input()
                                
                                has_goal = False
                                for some_goal in new_node.known_goals:
                                    for some_agent in next_step.agents:
                                        #print(some_agent[0] + " == " + some_goal[0])
                                        if some_agent[0] == some_goal[0]:
                                            has_goal = True
                                            break
                                    if has_goal:
                                        break
                                        
                                #input()
                                
                                if not has_goal:
                                    print("Skipped explanation: " + next_step_label)
                                    pass
                                    
                                else:
                                    if not (next_step_label in unexplained_steps):
                                        unexplained_steps[next_step_label] = False
                                #unexplained_steps.append(next_step)
                             
                            #   [ggmp 3.2] append to bfs_queue
                            
                            _insert_flag = False
                            
                            # [X] Disable plateau for now
                            plateau = -1
                            if parent_node.author_goal_score >= plateau:
                                plateau = parent_node.author_goal_score
                                _insert_flag = True
                            elif _delete_allowed:
                                print("DELETED A NODE : " +parent_node.label+ " : " + str(parent_node.author_goal_score) + "/" + str(plateau))
                                child_number -= 1
                                search_space.remove_node(new_node.label)
                                
                                if new_node_label in search_space:
                                    print("new_node_label in search_space")
                                    input()
                                
                                break
                            
                            if not (new_node.label in discovered_nodes):
                                if search_space.nodes[new_node.label]['body'].layer == current_layer:
                                    discovered_nodes.append(copy.copy(new_node.label))
                                    if _insert_flag:
                                        bfs_queue.insert(0,(new_node.label, current_layer, 0))
                                    else:
                                        bfs_queue.append((new_node.label, current_layer, 0))
                            
                            # [X] Deactivate _MAX_PLAN_NODE_CHILDREN
                            #if child_number >= _MAX_PLAN_NODE_CHILDREN:
                                #print(" MAX CHILDREN ACHIEVED")
                            #    break
                            
                            #   [ggmp 3.4] explanation threshold met
                            # N/A
                            
                            # [TIMING SECTION 07 - END]
                            #_current_section_start = datetime.datetime.now()
                            _current_section07_end = datetime.datetime.now()
                            _current_section_elapsed = _current_section07_end - _current_section07_start
                            _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                            _TIMING_DEBUG['section_07'] += _current_section_elapsed_seconds
                           
                        #if _debug:
                        #    input()
                           
                        if terminate_flag:
                            print("Cascading out [1]")
                            break
                            
                        # [TIMING SECTION 03 - END]
                        #_current_section_start = datetime.datetime.now()
                        _current_section03_end = datetime.datetime.now()
                        _current_section_elapsed = _current_section03_end - _current_section03_start
                        _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                        _TIMING_DEBUG['section_03'] += _current_section_elapsed_seconds
                    
                    
                    if _has_valid_step:
                        _terminate_guarantee_loop = True
                    
                    else:
                        print("[...] [WARNING] next_step_list has no valid actions")
                        # Get random next step?
                        
                        # [Alt 1] Blind random next step.
                        
                        # [Alt 2] First step with +delta
                        action_pool = list(self.goal_graph_master_list.keys())
                        random.shuffle(action_pool)
                        
                        next_step_list = self.getNextSteps(current_node.state, action_pool, quantity=3, mode="random", dp_parser=dp_parser)
                        _terminate_guarantee_loop = False
                    
                    
                    if _terminate_guarantee_loop:
                        break
                    else:
                        _guarantee_loop_ctr += 1
                        print("[...] Continuing guarantee loop : " + str(_guarantee_loop_ctr))
                        print("search_space: ["+str(len(search_space.nodes()))+"]  || bfs_queue: ["+str(len(bfs_queue))+"] || remaining_goals: ["+str(len(remaining_goals))+"]")
                        
                if terminate_flag:
                    print("Cascading out [2]")
                    break
                
                # [TIMING SECTION 02 - END]
                #_current_section_start = datetime.datetime.now()
                _current_section02_end = datetime.datetime.now()
                _current_section_elapsed = _current_section02_end - _current_section02_start
                _current_section_elapsed_seconds = _current_section_elapsed.total_seconds()
                _TIMING_DEBUG['section_02'] += _current_section_elapsed_seconds
                # [goalgraphmultipath 4.]

            
            # [end][COREPROCESS]
            
            end_execution = datetime.datetime.now()
            elapsed_time = end_execution - start_execution
            elapsed_seconds = elapsed_time.total_seconds()
            logstr = " [...!] [Time check 0-1] ," + str(elapsed_seconds)
            #print(logstr)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            
            
            
            #print(search_space.nodes.label)
            #for somelabel in search_space.nodes:
            #    if search_space.nodes[somelabel]['body'].last_action is not None:
            #        print(search_space.nodes[somelabel]['body'].last_action.getFunctionString())
            #print(" [...] Drawing plan graph ...")
            #self.drawPlanGraph(search_space, parameters['found_intention_node_list'], self.personality.plan_graph_depth)
            
            
            #if len(search_space) > 200:
            #    print(" [...] Drawing plan graph ...")
            #    self.drawPlanGraph(search_space, parameters['found_intention_node_list'], self.personality.plan_graph_depth)
                
            #input()
            
        print(" [...] Drawing plan graph ...")
        #self.drawPlanGraph(search_space, parameters['found_intention_node_list'], self.personality.plan_graph_depth, mode="author_goal_score")
        #self.drawPlanGraph(search_space, parameters['found_intention_node_list'], self.personality.plan_graph_depth, mode="default")
        
        logstr = ""
        logstr += "," + str(_TIMING_DEBUG['section_01a']) 
        logstr += "," + str(_TIMING_DEBUG['section_01b']) 
        logstr += "," + str(_TIMING_DEBUG['section_02']) 
        logstr += "," + str(_TIMING_DEBUG['section_03']) 
        logstr += "," + str(_TIMING_DEBUG['section_04']) 
        logstr += "," + str(_TIMING_DEBUG['section_05']) 
        logstr += "," + str(_TIMING_DEBUG['section_06']) 
        logstr += "," + str(_TIMING_DEBUG['section_07']) 
        
        print(logstr)
        util.log(_LOG_EXECUTION_LOGFILE[3], logstr, "line/txt", enabled=True)
        
        #print("====")
        #print(explained_steps)
        #print("====")
        #input()
        
        if terminate_flag:
            #print(" [...] Drawing plan graph ...")
            #self.drawPlanGraph(search_space, parameters['found_intention_node_list'], self.personality.plan_graph_depth)

            return True
        
        else:
            print("FAILED: " + str(len(search_space)))
            print("achieved_authors_goals:")
            print(achieved_authors_goals)
            return False
    
    #-------->>>> Debugging Methods
    def __getActionInstance(self,action_name:str, parameter_list:list):
    
        for someaction in self.action_instance_list:
            if (someaction.name == action_name) and (someaction.isMatch(parameter_list)):
                return someaction
        return None
        
    #-------->>>>
    def __getRandomPlanPath(self, search_space:DiGraph, someplan_node, length):
        
        length_ctr = 0
        path = []
        current_node = someplan_node
        while length_ctr < length:
            successor_list = list(search_space.successors(current_node))
            predecessor_list = list(search_space.predecessors(current_node))
            if (len(successor_list) > 0) :
                next_step = random.sample(list(successor_list),1).pop()
                
                #print(search_space.nodes[next_step]['body'])
                #input()
                
                path.append(search_space.nodes[next_step]['body'].last_action.function_string)
                
                #print()
                #input(" AAAAAAAAAHH: ")
            else:
                
                #print(current_node)
                #print(" [>>!]" + str(successor_list) + ":" + str(len(successor_list)))
                #print(" [>>!]" + str(predecessor_list) + ":" + str(len(predecessor_list)))
                #input()
                break
            length_ctr += 1
            current_node = next_step
        return path
    #-------->>>>
    
    def execute(self, 
                mode:str, 
                cycle_code="0000-000000", 
                _DEBUG_ENABLE=False, 
                max_runtime_minutes=0,
                algorithm=None,
                parameters={}
                ):
        
        all_start_execution = datetime.datetime.now()
        run_id = self.run_id
        
        print(" ["+cycle_code+"...] Initializing planner . . .")
        #current_mode = "GLOBAL"
        logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
        now = datetime.datetime.now()
        logfile.write(str(datetime.datetime.now()) + ": ["+cycle_code+"...] Initializing planner . . .""\n")
        logfile.close()    
        
        goal_graph_depth = self.personality.goal_graph_depth


        logstr = "\t [raw]" + str(self.domainproblem.goals)
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=True)
        print(logstr)
        
        dp_parser = DomainProblemParser(self.domainproblem)
        personal_goals = []
        for goal in self.domainproblem.positive_goals:
            personal_goals.append([self.identity,goal])
            logstr = "\t [+]" + str(goal)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=True)
            print(logstr)
            
        for goal in self.domainproblem.negative_goals:
            personal_goals.append([self.identity,goal])
            logstr = "\t [-]" + str(goal)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=True)
            print(logstr)
            
        

        
        # 1. Define search space graph
        search_space = DiGraph()
        
        # 2. Get all intentions (from ALL actors)
        all_known_intentions = dp_parser.getAllIntentions(self.domainproblem.state)
        
        # 3. Define root node
        raw_state_str = str(frozenset(sorted(self.domainproblem.state)))
        plan_root_node_label = str(hash(raw_state_str)) + "_" \
                             + hashlib.blake2s(raw_state_str.encode('utf-8'),salt=run_id[0:8].encode('utf-8')).hexdigest()
                            
        plan_root_node_address = str(util.zeroStringPad("0",4))
        plan_root_node = PlanGraphNode(plan_root_node_label, plan_root_node_address, [],frozenset(self.domainproblem.state), None, all_known_intentions, 0)
        
        search_space.add_node(plan_root_node_label, body=plan_root_node,layer=0)
        
        
        very_initial_state = copy.deepcopy(plan_root_node.state)
        
        # 4. Define supporting data structures and parameters
        achieved_intentions = []
        achieved_authors_goals = {}
        unexplained_steps = {}
        explained_steps = {}
        found_intention_node_list = []
        found_authors_goals_node_list = []
        current_layer = 1
        
        #   >> Personality-related parameters
        plan_graph_depth = self.personality.plan_graph_depth
        nextstepsize = self.personality.nextstepsize
        nextsteprange = self.personality.nextsteprange
        
        
        planner_parameters = dict()
        planner_parameters['current_node']                  = plan_root_node
        planner_parameters['unexplained_steps']             = unexplained_steps
        planner_parameters['explained_steps']               = explained_steps
        planner_parameters['found_intention_node_list']     = found_intention_node_list
        planner_parameters['current_layer']                 = current_layer
        planner_parameters['max_depth']                     = plan_graph_depth
        planner_parameters['dp_parser']                     = dp_parser
        planner_parameters['plan_root_node']                = plan_root_node
        planner_parameters['personal_goals']                = personal_goals        # identity's goals
        planner_parameters['achieved_intentions']           = achieved_intentions
        planner_parameters['achieved_authors_goals']        = achieved_authors_goals
        planner_parameters['found_authors_goals_node_list'] = found_authors_goals_node_list
        planner_parameters['nextstepsize']                  = nextstepsize
        planner_parameters['nextsteprange']                 = nextsteprange        
        planner_parameters['mode']                          = ""
        planner_parameters['raffle_list']                   = []
        planner_parameters['coreplanner_start_execution']   = all_start_execution
        planner_parameters['search_space_audit']            = {}
        planner_parameters['chapter_str']                   = parameters['chapter_str']
        #----------------------------------
        # 5. Test state changes
        #----------------------------------
        

        # 6. Start planning
        logstr = "Starting plan cycle: ["+cycle_code+"] + "
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        try_ctr = 0
        for try_ctr in range(0,7):
            plan_start_execution = datetime.datetime.now()
            #print(try_ctr)
            
            if algorithm in ["directedrandom1","ggp_dr1_hybrid"]:
                if try_ctr == 0:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                elif try_ctr == 1:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                elif try_ctr == 2:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_ggcomplement')
                elif try_ctr == 3:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('random_travel')
                elif try_ctr == 4:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_ggcomplement')
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                    planner_parameters['raffle_list'].append('random_travel')
                elif try_ctr == 5:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                    planner_parameters['raffle_list'].append('highestDelta_travel')
                    planner_parameters['raffle_list'].append('highestDelta_ggcomplement')
                    planner_parameters['raffle_list'].append('random_travel')
                elif try_ctr == 6:
                    planner_parameters['raffle_list'] = []
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_gg')
                    planner_parameters['raffle_list'].append('highestDelta_ggcomplement')
                    planner_parameters['raffle_list'].append('random_travel')
                    planner_parameters['raffle_list'].append('random_travel')
            else:
                planner_parameters['raffle_list'] = []
                planner_parameters['raffle_list'].append('fullrandom')
                
            
            return_flag = self.__planningRoutineBFS(search_space, planner_parameters, max_runtime_mins=int(round(max_runtime_minutes)),algorithm=algorithm)
            
            plan_end_execution = datetime.datetime.now()
            plan_elapsed_time = plan_end_execution - plan_start_execution
            
            plan_elapsed_seconds = plan_elapsed_time.total_seconds()
            plan_elapsed_minutes = plan_elapsed_time.total_seconds() / 60
                
            print("[Try #"+str(try_ctr+1)+"]Plan graph generation execution time:")
            print("\t" + str(plan_elapsed_seconds)+ " second/s")
            print("\t" + str(plan_elapsed_minutes)+ " minute/s")
            
            util.log(_LOG_EXECUTION_LOGFILE[0], "[Try #"+str(try_ctr+1)+"]Plan graph generation execution time:", "line/txt")
            util.log(_LOG_EXECUTION_LOGFILE[0], "\t" + str(plan_elapsed_seconds)+ " second/s", "line/txt")
            util.log(_LOG_EXECUTION_LOGFILE[0], "\t" + str(plan_elapsed_minutes)+ " minute/s", "line/txt")
            
            all_end_execution = datetime.datetime.now()
            all_elapsed_time = all_end_execution - all_start_execution
            
            all_elapsed_seconds = all_elapsed_time.total_seconds()
            all_elapsed_minutes = all_elapsed_time.total_seconds() / 60
            
            if all_elapsed_minutes >= int(round(max_runtime_minutes)):
                logstr =    str(run_id)    + ";"                 \
                        +   str(algorithm) + ";"                 \
                        +   str(try_ctr+1) + ";"                                                \
                        +   str(len(planner_parameters['found_authors_goals_node_list'])) + ";" \
                        +   str(len(search_space.nodes())) + ";"                                \
                        +   str(all_elapsed_seconds) + ";"                                      \
                        +   str(all_elapsed_minutes) + ";Exceeded max run time allowance"
                print(logstr)
                util.log(_LOG_EXECUTION_LOGFILE[4], logstr, "line/txt", enabled=True,header="sep=;\nDatetime;Run ID;Algorithm;Try Ctr;Total Goal Nodes;Total Nodes Explored;Elapsed seconds;Elapsed minutes")
                
                return False
            
            if len(planner_parameters['found_authors_goals_node_list']) != 0:
                #print(" [...] Drawing plan graph ...")
                #self.drawPlanGraph(search_space, planner_parameters['found_authors_goals_node_list'], self.personality.plan_graph_depth)
                break
            else:
                print(" [...] Try #" + str(try_ctr+1) + "; No solution found, restarting. ")
                #self.drawPlanGraph(search_space, planner_parameters['found_authors_goals_node_list'], plan_graph_depth)
            
            
        
            if algorithm not in ["directedrandom","ggp_dr1_hybrid"]:
                break
                
        if _DEBUG_ENABLE:
            logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
            now = datetime.datetime.now()
            
            logfile.write(str(datetime.datetime.now()) + ": Completed plan cycle: ["+cycle_code+"]\n")
            logfile.write(str(datetime.datetime.now()) + ": Total nodes    : " + str(len(search_space)) + "\n")
            logfile.write(str(datetime.datetime.now()) + ": Goal nodes     : " + str(len(found_authors_goals_node_list)) + "\n")
            logfile.write(str(datetime.datetime.now()) + ": Author's Goals  : " + str(self.domainproblem.goals) + "\n")
            logfile.write(str(datetime.datetime.now()) + ": Achieved intentions : \n")
            
            _LOG_VARIABLES[1] = str(len(search_space))
            _LOG_VARIABLES[2] = str(len(found_authors_goals_node_list))
            
            print(" ["+cycle_code+"...] Completed plan cycle: ["+cycle_code+"]")
            print(" ["+cycle_code+"...] Total nodes    : " + str(len(search_space)))
            print(" ["+cycle_code+"...] Goal nodes     : " + str(len(found_authors_goals_node_list)))
            print(" ["+cycle_code+"...] Author's Goals  : " + str(self.domainproblem.goals))
            print(" ["+cycle_code+"...] Achieved intentions : ")
            
            for some_goal in planner_parameters['achieved_intentions']:
                print(some_goal)
                logfile.write("\t" + str(some_goal) + "\n")
                
            logfile.write(str(datetime.datetime.now()) + ": Achieved author's goals : \n")
            print(" ["+cycle_code+"...] Achieved author's goals : ")
            
            for key, value in planner_parameters['achieved_authors_goals'].items():
                print(key + ":" + str(value))
                logfile.write("\t" + key + ":" + str(value) + "\n")
                
            logfile.write(str(datetime.datetime.now()) + ": Action breakdown:\n")
            print(" ["+cycle_code+"...] Action breakdown:")
        
            action_breakdown = {}
            for somenode in search_space.nodes():
                #print(search_space.nodes[somenode])
                #input()
                if search_space.nodes[somenode]['body'].last_action is not None:
                    action_name = search_space.nodes[somenode]['body'].last_action.name
                else:
                    action_name = "None"
                if action_name in action_breakdown:
                    action_breakdown[action_name] += 1
                else:
                    action_breakdown[action_name] = 1
            
            for key, value in action_breakdown.items():
                print("         " + key + ":" + str(value))
                logfile.write("\t" + key + ":" + str(value) + "\n")
                
        
        goal_nodes_ctr = 0
        
        #ytfgjgfhj gdfhj rgfh dgfh dfg
        
        #   cycle through planner_parameters['found_authors_goals_node_list']
        #   look for nodes that fulfilled ALL of of the author's goals   
        #   perhaps look for a way to encode found_authors_goals_node_list better
        
        for found_intention_tuple in planner_parameters['found_authors_goals_node_list']:
            
            
            #print(found_intention_tuple)
            #input()
            
            #solution_path = nx.shortest_path(search_space, plan_root_node_label, found_intention_tuple[0])
            # Add solution path to solution list
            error_flag = False
            new_solution = []
            initial_state = copy.deepcopy(very_initial_state)
            plan_graph_node_parent = ""
            
            for some_action_tuple in found_intention_tuple[2]:
            #for some_action in search_space.nodes[found_intention_tuple[0]]['body'].plan:
                #print("trying..." + some_action.getFunctionString())
                action_instance = some_action_tuple[1]
                #initial_state = initial_state
                try:
                    final_state = dp_parser.applyAction(action_instance  , initial_state)
                except Exception:
                    parameters['faulty_action_count'] = parameters['faulty_action_count'] + 1
                    print(" [ERROR:] Faulty action detected [coreplanner action queue]: " + action_instance.getFunctionString())
                    error_flag = True
                    break
                    
                initial_state_hrparagraph = dp_parser.convertToHRParagraph(initial_state)
                negative_change_hrparagraph = dp_parser.convertToHRParagraph(initial_state - final_state)
                positive_change_hrparagraph = dp_parser.convertToHRParagraph(final_state - initial_state)
                
                filter = {"adjacency":True, "intentions":True, "normal":True}
                final_state_hrparagraph_all              = dp_parser.convertToHRParagraph(final_state,filter=filter)
                filter = {"adjacency":False, "intentions":False, "normal":True}
                final_state_hrparagraph_norm_only        = dp_parser.convertToHRParagraph(final_state,filter=filter)
                filter = {"adjacency":True, "intentions":False, "normal":False}
                final_state_hrparagraph_adjacency_only   = dp_parser.convertToHRParagraph(final_state,filter=filter)
                filter = {"adjacency":False, "intentions":True, "normal":False}
                final_state_hrparagraph_intentions_only  = dp_parser.convertToHRParagraph(final_state,filter=filter)
                        
                #initial_state_hrparagraph               = ""
                #negative_change_hrparagraph             = ""
                #positive_change_hrparagraph             = ""
                #final_state_hrparagraph_all             = ""
                #final_state_hrparagraph_norm_only       = ""
                #final_state_hrparagraph_adjacency_only  = ""
                #final_state_hrparagraph_intentions_only = ""
                        
                        
                if "(" in str(final_state_hrparagraph_all):
                    raise Exception("Potato")
                if "(" in str(final_state_hrparagraph_norm_only):
                    raise Exception("Potato")
                if "(" in str(final_state_hrparagraph_adjacency_only):
                    raise Exception("Potato")
                if "(" in str(final_state_hrparagraph_intentions_only):
                    raise Exception("Potato")
                
                
                # print(action_instance.getFunctionString())
                #print("....|")
                #print(explained_steps)
                #input()
                # print("....|")
                # print(planner_parameters['explained_steps'])
                explained_by_list = []
                
                print(planner_parameters['explained_steps'])
                print("---------")
                #input()
                
                if action_instance.getFunctionString() in planner_parameters['explained_steps']:
                    #print("EXPLAINED:")
                    #print(planner_parameters['explained_steps'][action_instance.getFunctionString()])
                    explanation_node = planner_parameters['explained_steps'][action_instance.getFunctionString()]
                    _generator_object = nx.all_simple_paths(search_space,plan_root_node.label,explanation_node[0].label)
                    
                    explanation_paths = []
                    
                    for somepath in _generator_object:
                        new_path = []
                        for somestep in somepath:
                            _someaction = search_space.nodes[somestep]['body'].last_action
                            new_path.append(copy.copy(_someaction))
                        explanation_paths.append(copy.deepcopy(new_path))
                    
                    
                else:
                    #print("NOT EXPLAINED")
                    explanation_paths = None
                
                
                if action_instance.getFunctionString() in explained_steps:
                
                    _plan_node_list = explained_steps[action_instance.getFunctionString()]
                    
                    for some_plan_node in _plan_node_list:
                        # TODO: Filter the steps by the active actor in /action_instance/
                        explained_by_list.extend(copy.deepcopy(some_plan_node.intentions_achieved))
                        
                    #explained_by_list = copy.deepcopy(explained_steps[action_instance.getFunctionString()])
                    #print("HIT")
                    #print(explained_by_list)
                else:
                    pass
                
                
                
                #print(explained_by_list)
                #input()
                
                
                plan_graph_node_label = some_action_tuple[0].split('|')[1]
                #print(search_space.nodes.keys())
                #print(search_space.nodes[plan_graph_node_label]['body'])
                #input()
                goal_graph_soft_plan = search_space.nodes[plan_graph_node_label]['body'].goal_graph_soft_plan
                soft_plan_source = search_space.nodes[plan_graph_node_label]['body'].soft_plan_source
                new_solution_action_instance = SolutionActionInstance(
                
                                                    action_instance                            = action_instance,
                                                    initial_state                              = copy.deepcopy(initial_state),
                                                    final_state                                = copy.deepcopy(final_state), 
                                                    initial_state_hrparagraph                  = initial_state_hrparagraph, 
                                                    negative_change_hrparagraph                = negative_change_hrparagraph, 
                                                    positive_change_hrparagraph                = positive_change_hrparagraph, 
                                                    final_state_hrparagraph_all                = final_state_hrparagraph_all,
                                                    final_state_hrparagraph_norm_only          = final_state_hrparagraph_norm_only,
                                                    final_state_hrparagraph_adjacency_only     = final_state_hrparagraph_adjacency_only,
                                                    final_state_hrparagraph_intentions_only    = final_state_hrparagraph_intentions_only,
                                                    explained_by_list                          = explained_by_list,
                                                    plan_graph_node_label                      = plan_graph_node_label,
                                                    plan_graph_node_parent                     = plan_graph_node_parent,
                                                    explanation_paths                          = copy.deepcopy(explanation_paths),
                                                    goal_graph_soft_plan                       = goal_graph_soft_plan,
                                                    soft_plan_source                           = soft_plan_source
                                                )
                                                
                plan_graph_node_parent = some_action_tuple[0]
                
                new_solution.append(new_solution_action_instance)
                
                #===
                initial_state = copy.deepcopy(final_state)
                #===
            
            if error_flag:
                continue
            else:
                #print("Yes I found a solution.")
                #input()
                self.solutions.append(copy.deepcopy(new_solution))
                goal_nodes_ctr += 1
            
            #if _DEBUG_ENABLE:
            #    print(" ["+cycle_code+"...] Solution for: " + str(found_intention_tuple[1]))
            logfile.write(str(datetime.datetime.now()) + ": Solution for: " + str(found_intention_tuple[1]) + "\n")
            
            #print(search_space.nodes[found_intention_tuple[0]]['body'].plan)
            #for some_action in search_space.nodes[found_intention_tuple[0]]['body'].plan:
            #    if some_action is None:
            #        if _DEBUG_ENABLE:
            #            print("\t\tCurrent state" )
            #        logfile.write("\tCurrent state\n")
            #    else:
            #        if _DEBUG_ENABLE:
            #            print("\t\t" + str(some_action.getFunctionString()))
            #        logfile.write("\t" + str(some_action.getFunctionString()) + "\n")
                
                        
                  
        #self.drawPlanGraph(search_space, planner_parameters['found_authors_goals_node_list'], plan_graph_depth)
        #drawPlanGraph(self, plan_graph:DiGraph, goal_nodes:list, layers)
        
        logstr =    str(run_id)    + ";"                 \
                +   str(algorithm) + ";"                 \
                +   str(try_ctr+1) + ";"                 \
                +   str(goal_nodes_ctr) + ";"            \
                +   str(len(search_space.nodes())) + ";" \
                +   str(all_elapsed_seconds) + ";"       \
                +   str(all_elapsed_minutes)
        #print(logstr)
        util.log(_LOG_EXECUTION_LOGFILE[4], logstr, "line/txt", enabled=True,header="sep=;\nDatetime;Run ID;Algorithm;Try Ctr;Total Goal Nodes;Total Nodes Explored;Elapsed seconds;Elapsed minutes")
        
        if goal_nodes_ctr > 0:
            return True
        else:
            return False
    

#------------------------------------------------
#    main() function

def main(argv, test_arg):

    #print(argv)
    #input()
    
    if len(argv) < 2:
        load_mode = ""
    elif len(argv) == 2:
        if argv[1].upper() == "SAVE":
            load_mode = argv[1]
        elif argv[1].upper() == "LOAD":
            load_mode = argv[1]
        #elif argv[1].upper() == "TEST":
        #    load_mode = argv[1]
        else:
            print(" [!!!] ERROR: Unrecognized commandline parameter: " + argv[1])
            
    else:
        load_mode = argv[1]
        print(" [..!] WARNING: Excess paramters detected")
        ctr = 0
        for somearg in argv:
            if ctr > 1:
                print("\t" + str(somearg))
            ctr+=1
        
            
    #_INPUT_DOMAIN_FULL_LABEL = "fantasy"
    #_INPUT_SERIES = "05"
    
    _INPUT_DOMAIN_FULL_LABEL = test_arg[8]
    #_INPUT_SERIES = test_arg[9]
    
    inp_domain = _INPUT_DIR + _INPUT_DOMAIN_FULL_LABEL + "-domain-" + str(_INPUT_SERIES) + ".pddl"
    inp_problem = _INPUT_DIR + _INPUT_DOMAIN_FULL_LABEL + "-problem-" + str(_INPUT_SERIES) + ".pddl"
    #inp_problem = _INPUT_DIR + "fantasy-problem-08-villainy1_vstealp_01.pddl"


    # Start logging
    now = datetime.datetime.now()
    now_str = now.strftime("%Y%m%d_%H%M%S")
    
    _PERSONALITY_SERIES = ""
    _PERSONALITY_SERIES += "GG" + util.zeroStringPad(str(test_arg[1]),2)
    _PERSONALITY_SERIES += "PG" + util.zeroStringPad(str(test_arg[2]),2)
    _PERSONALITY_SERIES += "NS" + util.zeroStringPad(str(test_arg[3]),2)
    _PERSONALITY_SERIES += "NSR"+ util.zeroStringPad(str(test_arg[4]),2)
    _PERSONALITY_SERIES += "SPG"+ util.zeroStringPad(str(test_arg[5]),2)
    
    ctr = 0
    
    _LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "Results 001/" + str(ctr) + "/LOG_coreplanner_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _INPUT_SERIES + "-" + _PERSONALITY_SERIES + "-" + now_str + ".txt"
    _LOG_EXECUTION_LOGFILE[1] = _LOG_DIR + "Results 001/" + str(ctr) + "/CONSOLIDATEDLOG_coreplanner_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _INPUT_SERIES + "-" + _PERSONALITY_SERIES + ".csv"
    _LOG_EXECUTION_LOGFILE[2] = _LOG_DIR + "Results 001/" + str(ctr) + "/LOG_discardpile_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _INPUT_SERIES + "-" + _PERSONALITY_SERIES + "-" + now_str + ".txt"
    
    
    logfile = open(_LOG_EXECUTION_LOGFILE[0], "w")
    now = datetime.datetime.now()
    logfile.write(str(datetime.datetime.now()) + ": Begin execution\n")
    logfile.close()
    
    start_execution = now
    
    try:
        consolidatedlogfile =  open(_LOG_EXECUTION_LOGFILE[1], "r")
        consolidatedlogfile.close()
    except FileNotFoundError:
        consolidatedlogfile =  open(_LOG_EXECUTION_LOGFILE[1], "w")
        consolidatedlogfile.close()
    
    #inp_domain = _INPUT_DIR + "/tests/aladdin-domain.pddl"
    inp_problem  = _INPUT_DIR + "/20190521_185654/fantasy-problem-01-villainy1_vstealp_01.pddl"
    
    print(" [...] inp_domain : " + inp_domain)
    print(" [...] inp_problem : " + inp_problem)
    
    logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
    now = datetime.datetime.now()
    logfile.write(str(datetime.datetime.now()) + ": inp_domain : " + inp_domain + "\n")
    logfile.write(str(datetime.datetime.now()) + ": inp_problem : " + inp_problem + "\n")
    logfile.close()
    
    domprob = DomainProblem()
    domprob.parseDomain(inp_domain)
    domprob.parseProblem(inp_problem)
    

    # self, alignment="", goal_graph_depth=6, plan_graph_depth=6, nextstepsize=6, nextsteprange=2, solutions_per_goal=1
    personality_01 = Personality(test_arg[0],test_arg[1],test_arg[2],test_arg[3],test_arg[4],test_arg[5],test_arg[6])
    personality_01.setAlignmentValues(0,0)
    
    #print("Personality values:")
    #print("   Lawfulness : " + str(personality_01.lawfulness_val) + " ("+personality_01.lawfulness_str+")") 
    #print("   Goodness   : " + str(personality_01.goodness_val) + " ("+personality_01.goodness_str+")") 
    #print("   Alignment  : " + personality_01.alignment)
    
    identity = "author"
    #if domprob.isValidActor(identity):
    #    pass
    #else:
    #    logstr = " [!!!] ERROR: Invalid actor: " + identity
    #    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
    #    raise Exception(" [!!!] ERROR: Invalid actor: " + identity)
    
    #domprob.setInitialState(domprob.state)
    
    #domprob.saveProblem(inp_problem + ".BAK")
    
    parameters = dict()
    parameters['input_category'] = _INPUT_DOMAIN_FULL_LABEL
    parameters['input_series'] = _INPUT_SERIES
    planner_01 = BasicFCPlanner(identity, domprob, personality_01, load_mode, parameters)
    
    planner_01.instantiateActions()
    
    # [DEBUGGING]
    
    # getGoalScore(self, current_state:set, total_goals:list):

    
    
    #for someaction in planner_01.action_instance_list:
    #    #if (someaction.name == "steal") and (str(someaction.parameters) == str([['talia', 'person'], ['gargax', 'monster'], ['treasure', 'valuable'], ['cave', 'place']])):
    #    if (someaction.getFunctionString() == "steal(talia, gargax, sword, cave)"):
    #        #print(someaction.getFunctionString())
    #        action_to_apply = someaction
    #        print(someaction.getFunctionString())
    #        print("[+]")
    #        for someeffect in someaction.possible_positive_effects:
    #            print("\t" + str(someeffect))
    #        print("[-]")
    #        for someeffect in someaction.possible_negative_effects:
    #            print("\t" + str(someeffect))
    #        #input()
            
    print("----[done retrieving sample action")
    
    start_state = domprob.state
    #total_goals = []
    #total_goals.extend(planner_01.domainproblem.positive_goals)
    #total_goals.extend(planner_01.domainproblem.negative_goals)
    #
    #goal_score = planner_01.planner_parameters['dp_parser'].getGoalScore(start_state, total_goals)
    #print(goal_score)
    #print()
    #
    #result_state = planner_01.planner_parameters['dp_parser'].applyAction(action_to_apply, start_state)
    #
    #goal_score = planner_01.planner_parameters['dp_parser'].getGoalScore(result_state, total_goals)
    #print(goal_score)
    #print()
    #input()
    
    #for somestate in start_state:
    #    print(somestate)
    #print("----||")
    
    #result_state = planner_01.planner_parameters['dp_parser'].applyAction(action_to_apply, start_state)

    #print("----xx")
    #for somestate in result_state:
    #    print(somestate)
    #print("----[DONE]")
    
    #print(start_state - result_state)
    #print(result_state - start_state)
    #
    #input()
    
    planner_01.generateRigidGoalGraph(personality_01.goal_graph_depth)
    
    planner_01.execute("GLOBAL", "0000-000000", True)
    

    logfile = open(_LOG_EXECUTION_LOGFILE[0], "a+")
    now = datetime.datetime.now()
    end_execution = now
    
    elapsed_time = end_execution - start_execution
    elapsed_seconds = elapsed_time.total_seconds()
    elapsed_minutes = elapsed_time.total_seconds() / 60
    
    logfile.write(str(datetime.datetime.now()) + ": Total execution time:\n")
    logfile.write("\t" + str(elapsed_seconds)+ " second/s" + "\n")
    logfile.write("\t" + str(elapsed_minutes)+ " minute/s" + "\n")
    logfile.close()
    
    print("Total execution time:")
    print("\t" + str(elapsed_seconds)+ " second/s")
    print("\t" + str(elapsed_minutes)+ " minute/s")
    
    
    _LOG_VARIABLES[3] = str(elapsed_seconds)
    _LOG_VARIABLES[4] = str(elapsed_minutes)    
    
    # Consolidated log entry:

    consolidatedlogfile =  open(_LOG_EXECUTION_LOGFILE[1], "a+")
    consolidatedlog_entry = ""
    consolidatedlog_entry += str(_LOG_VARIABLES[0]) + ","
    consolidatedlog_entry += str(_LOG_VARIABLES[1]) + ","
    consolidatedlog_entry += str(_LOG_VARIABLES[2]) + ","
    consolidatedlog_entry += str(_LOG_VARIABLES[3]) + ","
    consolidatedlog_entry += str(_LOG_VARIABLES[4]) + "\n"
    
    consolidatedlogfile.write(consolidatedlog_entry)
    consolidatedlogfile.close()
    
if __name__ == '__main__':

    # Test loop
    # test_arg[]:
    #   alignment
    #   goal_graph_depth
    #   plan_graph_depth
    #   nextstepsize
    #   nextsteprange
    #   solutions_per_goal
    #   _INPUT_DOMAIN_FULL_LABEL
    #   _INPUT_SERIES

    #for d_ctr in range(6,7):
    #    for gg_ctr in range(0,3):
    #        for pg_ctr in range(2,4):
    #            test_arg = ["", 4+gg_ctr,4+pg_ctr,6,2,2, "fantasy",util.zeroStringPad(str(d_ctr),2)]
    #            for ctr in range(0,10):
    #                main(sys.argv, test_arg)
               
    # Single execution
    #test_arg = ["", 5,6,6,2,3, "fantasy","08"]
    #main(sys.argv, test_arg)
    
    # Multiple execution
    #test_arg = ["", 1,5,16,1,1, 40, "fantasy","08"]
    test_arg = ["", 5,5,8,3,1,51,80,"fantasy","01"]
    for ctr in range(0,1):
        main(sys.argv, test_arg)
    
    
    
                
                