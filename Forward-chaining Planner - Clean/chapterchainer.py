import sys
import copy
import networkx as nx
import utility as util
import datetime
import random
import os
import secrets
import hashlib
import multiprocessing as mp
from networkx.drawing.nx_agraph import write_dot, graphviz_layout
from networkx import Graph, DiGraph
from pddllib import Action
from pddllib import DomainProblem
from pddllib import DomainProblemParser
from coreplanner import BasicFCPlanner
#from coreplanner_20190802 import BasicFCPlanner
from personality import Personality
from ncsparser import NarrativeChapterStructure

from flask_sqlalchemy import SQLAlchemy                             
from flask_app.models import    User,                           \
                                Post,                           \
                                NarrativeInstance,              \
                                PlanChapterInstance,            \
                                PlanChapterInstanceAction,      \
                                SolutionChapterInstance,        \
                                SolutionChapterInstanceAction,  \
                                Domains,                        \
                                StoryPattern,                   \
                                SolutionHRSequence,             \
                                UserActivePlanners,             \
                                NarrativeUserReview,            \
                                ObjectTypes,                    \
                                StatePredicateDef,              \
                                ActionDef,                      \
                                Action_Parameters,              \
                                Action_Predicates,              \
                                ActorTypes,                     \
                                ChapterPattern,                 \
                                SequenceTerms,                  \
                                SequenceTermActors,             \
                                SequenceTermObjects,            \
                                SequenceTermCategories,         \
                                LocationMap,                    \
                                LocationNode,                   \
                                LocationEdges,                  \
                                PredicateDescriptors,           \
                                ObjectNames

from sqlalchemy.orm   import  aliased
from sqlalchemy       import and_, or_, update, select 
                                
#------------------------------------------------
#    GLOBAL DECLARATIONS 
_INPUT_DIR = "./domainproblem/"
#_INPUT_DIR = "/home/sarrozadj/ISLA_online/domainproblem/"
#_INPUT_CATEGORY = "fantasy"
#_INPUT_SERIES = "01"

_LOG_EXECUTION_LOGFILE = ["","","",""]

_LOCATION_DIR = "./domainproblem/locations/"
#_LOCATION_DIR = "/home/sarrozadj/ISLA_online/domainproblem/locations/"

_LOG_DIR = "./logs/"
#_LOG_DIR = "/home/sarrozadj/ISLA_online/logs/"

_CHAPTERCHAIN_EXECUTE_TRY = 2
_PLAN_EXECUTE_TRY = 2

_RUNTIME_THRESHOLD_MINUTES = 10

_FAULTY_ACTION_COUNT = 0

#------------------------------------------------
#    FUNCTION DECLARATIONS 

#------------------------------------------------
#    CLASS DECLARATIONS 


# For a different approach
class ChapterNode:
    'Chapter graph node'
    
    def __init__(self, 
            label:str,
            address:str,
            chapter_label:str,
            domainproblem:DomainProblem,
            personality:Personality,
            initial_state:set,
            solution_steps:list,
            expected_state:set
            ):
    
        self.label = copy.deepcopy(label)
        self.address = copy.deepcopy(address)
        self.chapter_label = copy.deepcopy(chapter_label)
        self.domainproblem = domainproblem
        self.personality = copy.deepcopy(personality)
        self.initial_state = copy.deepcopy(initial_state)
        self.solution_steps = copy.deepcopy(solution_steps)
        self.expected_state = copy.deepcopy(expected_state)
        


class ChapterChainer:

    def __init__(self, id=None, user_id=None, domain_full_label=None, db=None):
    
        self.chapters = {}        # dict of dictionaries  (planner_instance)
        self.ncs = None
        
        if domain_full_label is None:
            raise Exception("Domain Label is None")

        #if series is None:
        #    raise Exception("Series is None")
            
        self.db = db
        self.domain_full_label = domain_full_label
        self._faulty_action_count = 0
        
        #now = datetime.datetime.now()
        #now_str = now.strftime("%Y%m%d_%H%M%S")
        #self.id = secrets.token_hex(8) + "_" + now_str
        
        self.id = id
        self.user_id = user_id
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
        print("run_id: " + str(self.id))
        pass
    
    def __planningRoutineDFS(self, chainer_search_space:DiGraph, parameters:dict):
        
        current_node            = parameters['current_node']
        ncs                     = parameters['ncs']
        identity                = parameters['identity']
        root_node               = parameters['root_node']
        neutral_obj_count       = parameters['neutral_obj_count']
        current_layer           = parameters['current_layer']
        run_id                  = parameters['run_id']
        personality             = parameters['personality']
        max_children            = parameters['max_children']
        cc_start_execution      = parameters['cc_start_execution']
        runtime_threshold       = parameters['runtime_threshold']
        algorithm               = parameters['algorithm']
        faulty_action_count     = parameters['faulty_action_count']
        
        domprob = current_node.domainproblem
        error_flag = False
        
        # [DATABASE]
        #id = db.Column(db.String(128), primary_key=True)
        #narrative_instance_id = db.Column(db.Integer, db.ForeignKey('narrative_instance.id'))
        #chapter_number = db.Column(db.Integer, nullable=False)
        #chapter_address = db.Column(db.String(64), nullable=False)
        #chapter_label = db.Column(db.String(128), nullable=False)
        #initial_state = db.Column(db.Text)
        #final_state = db.Column(db.Text)
        #parent_chapter = db.Column(db.Integer)
    
        #class ChapterNode:
        #    'Chapter graph node'
        #    
        #    def __init__(self, 
        #            label:str,
        #            address:str,
        #            chapter_label:str,
        #            domainproblem:DomainProblem,
        #            personality:Personality,
        #            initial_state:set,
        #            solution_steps:list,
        #            expected_state:set
        #            ):
        try:
            sequence_grouping_label = ncs.chapter_sequence[current_layer]
        except IndexError:
            logstr = "END OF THE CHAIN WE HAVE FOUND A COMPLETE SOLUTION"
            print(logstr)
            util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=False)
            
            return(current_node)
            
        predecessor_list = list(chainer_search_space.predecessors(current_node.label))
        if not predecessor_list:
            parent_node = None
        else:
            parent_node = chainer_search_space.nodes[predecessor_list[0]]['body']
            
        parent_node_dbid = run_id+"_"+current_node.address
        
        #sequence_grouping_label in ncs.chapter_sequence:

        
        threshold_end_execution = datetime.datetime.now()
        
        threshold_elapsed_time = threshold_end_execution - cc_start_execution
        threshold_elapsed_seconds = threshold_elapsed_time.total_seconds()
        threshold_elapsed_minutes = threshold_elapsed_time.total_seconds() / 60
        
        # [...] Disable chapterchainer runtime throtlling
        if threshold_elapsed_minutes >= runtime_threshold:
            logstr = "Runtime exceeded threshold"
            print(logstr)
            util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
            util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt", enabled=True)
            return False
        
        logstr = " [...] Chapter " + str(current_layer+1) + " : " + str(sequence_grouping_label)
        print(logstr)
        util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
        
        logstr = str(current_node.expected_state)
        util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=True)
        
        print(current_node.expected_state)
        
        #subchapter_ctr  = 0
        
        #for sequence_term_label in self.ncs.sequence_term['sequence_grouping_lookup'][sequence_grouping_label][1]:
            
        # Current iteration identification string
        iteration_id = sequence_grouping_label
        
        #self.chapters.append({})
        current_chapter_dict = {}
        
        
        problem_filename = _INPUT_DIR + run_id + "/" + str(current_node.address) + "-" + self.domain_full_label + "-problem-" + iteration_id + ".pddl"

        # -- Problem Goals
        
        settings = {"mode":"overwrite"}
        domprob.setInitialState(current_node.expected_state)
        
        
        if current_layer == 0:
            retro_update_target_statepreds = True
        else:
            retro_update_target_statepreds = False
            
        ncs.buildProblemGoal(domprob, ncs.chapter_sequence, current_layer, settings, retro_update_target_statepreds)
        
        #print(domprob.goals)
        #input()
        
        planner_parameters = dict()
        planner_parameters['input_domain_full_label'] = self.domain_full_label
        
        
        domprob.saveProblem(problem_filename)
        domprob.parseProblem(problem_filename)
        
        #print("////////////////")
        
        # [...] Check if domain goals are achievable
        
        self.positive_goals = []
        
        # [...>] Positive goals
        for some_goal in domprob.positive_goals:
            #print(type(some_goal))
            #print(some_goal)
            
            if str(some_goal) not in domprob.state:
                
                #print("potat")
                #input()
                predicate_label = some_goal[0]
                
                goal_state_predicate = self.db.session.query(StatePredicateDef) \
                    .filter(StatePredicateDef.domain_id == self.domain_id) \
                    .filter(StatePredicateDef.predicate_label == predicate_label) \
                    .first()
                    
                if goal_state_predicate is not None:
                    print(type(goal_state_predicate.eval_predicate_pos_mutability))
                    if goal_state_predicate.eval_predicate_pos_mutability <= 0:
                        logstr = " [...] Unsolvable current state. Predicate <"+str(some_goal)+"> is impossible to produce; eval_predicate_pos_mutability == " + str(goal_state_predicate.eval_predicate_pos_mutability)
                        util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                        print(logstr)
                        return False
                else:
                    raise Exception(str(predicate_label) + " is not recognized")
                    
        # [...>] Negative goals
        for some_goal in domprob.negative_goals:
            #print(type(some_goal))
            #print(some_goal)
            
            if str(some_goal) in domprob.state:
                
                #print("potat")
                #input()
                predicate_label = some_goal[0]
                
                goal_state_predicate = self.db.session.query(StatePredicateDef) \
                    .filter(StatePredicateDef.domain_id == self.domain_id) \
                    .filter(StatePredicateDef.predicate_label == predicate_label) \
                    .first()
                    
                if goal_state_predicate is not None:
                    #print(type(goal_state_predicate.eval_predicate_p_mutability))
                    if goal_state_predicate.eval_predicate_neg_mutability <= 0:
                        logstr = " [...] Unsolvable current state. Predicate <"+str(some_goal)+"> is impossible to remove; eval_predicate_neg_mutability == " + str(goal_state_predicate.eval_predicate_neg_mutability)
                        util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                        print(logstr)
                        return False
                else:
                    raise Exception(str(predicate_label) + " is not recognized")
        
        saved_initial_state = copy.deepcopy(domprob.state)
        
        planner_instance = BasicFCPlanner(identity, domprob, personality, "", planner_parameters, neutral_obj_count, run_id=run_id,db=self.db)
        planner_instance.generateRigidGoalGraph(personality.goal_graph_depth, False)
        
        #===
        old_state = copy.deepcopy(current_node.initial_state)
        for some_solnaction_instance in current_node.solution_steps:
            some_action = some_solnaction_instance.action_instance
            logstr = " [...][Post] Applying: " + some_action.getFunctionString()
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            print(logstr)
            
            try:
                new_state = planner_instance.planner_parameters['dp_parser'].applyAction(some_action, old_state)
            except Exception:
                faulty_flag = True
                logstr = " [.!!] Faulty action [post][solution action queue]: " + some_action.getFunctionString()
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt", enabled=False)
                print(logstr)
                break
            old_state = copy.deepcopy(new_state)
        
        #result_state = old_state
        
        #somediff1 = result_state - current_node.expected_state
        #somediff2 = current_node.expected_state - result_state
        #
        #
        #if (len(somediff1) > 0) or (len(somediff2) > 0):
        #    print("ANOTHER ERROR")
        #    print(somediff1)
        #    print("----")
        #    print(somediff2)
        #===
        
        try_ctr = 0
        while try_ctr < _PLAN_EXECUTE_TRY:
        
            # ==============================================
            
            #if (len(diff1) > 0) or (len(diff2) > 0):
            #
            #    print(diff1)
            #    print("----")
            #    print(diff2)
            #
            #    print("ERRRROOOORRRRR!!@!@!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
            #    input()

            # ==============================================
            # POTATO_BOOKMARK
            planner_parameters = dict()
            planner_parameters['faulty_action_count']   = faulty_action_count
            #planner_parameters['chapter_str']   = util.zeroStringPad(str(current_layer+1), 2)
            planner_parameters['chapter_str']   = current_node.address
            
            planner_instance.solutions = []
            #try:
            success_flag = planner_instance.execute(
                                            "GLOBAL", 
                                            util.zeroStringPad(str(current_layer+1), 2), 
                                            _DEBUG_ENABLE=True, 
                                            #max_runtime_minutes=int(round(runtime_threshold * 0.9)),
                                            max_runtime_minutes=runtime_threshold,
                                            algorithm=algorithm,
                                            parameters=planner_parameters
                                            )
            
            faulty_action_count = planner_parameters['faulty_action_count']
            
            self._faulty_action_count = faulty_action_count
            
            #except Exception:
            #    return False
            
            if len(planner_instance.solutions) == 0:
                try_ctr += 1
                
                if try_ctr < _PLAN_EXECUTE_TRY:
                    logstr = "[...] No solutions found, retrying ("+str(try_ctr+1)+"/"+str(_PLAN_EXECUTE_TRY)+")"
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr + "\n")

                else:
                    logstr = "[!!!] ERROR: No solutions found after ("+str(try_ctr)+"/"+str(_PLAN_EXECUTE_TRY)+") tries."
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    
                    logstr = ";" + run_id               +              \
                             ";[!!!] ERROR: No solutions found after ("+str(try_ctr)+"/"+str(_PLAN_EXECUTE_TRY)+") tries."
                    util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                    print(logstr)
                    error_flag = True
                    break
            else:
                #try_ctr = _PLAN_EXECUTE_TRY + 1
                
            
                #print(planner_instance.solutions)    # list of lists of Action objects
                #print("???")
                #for somesolution in planner_instance.solutions:
                #    print("Solution ")
                #    for someaction in somesolution:
                #        print("\t" + someaction.getFunctionString())
                break
            #input()
            
            # [IMPROVEMENT JUNCTION: Can add heuristic to choose a solution]
        print("=========")    
        if error_flag:
            #raise Exception("No solution found")
            logstr = "Dead-end on " + current_node.address
            util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
            print(logstr)
            return False
            
        else:
        
            spawned_children = 0
            
            for somesolution in planner_instance.solutions:
                
                spawned_children += 1
                if spawned_children >= max_children:
                    break
                
                old_state = copy.deepcopy(saved_initial_state)
                faulty_flag = False
                
                for some_solnaction_instance in somesolution:
                    some_action = some_solnaction_instance.action_instance
                    logstr = " [...][Pre] Applying: " + some_action.getFunctionString()
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    
                    try:
                        new_state = planner_instance.planner_parameters['dp_parser'].applyAction(some_action, old_state)
                    except Exception:
                    
                        faulty_action_count += 1
                        faulty_flag = True
                        logstr = " [.!!] Faulty action [pre][solution action queue]: " + some_action.getFunctionString()
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt", enabled=False)
                        print(logstr)
                        break
                    old_state = copy.deepcopy(new_state)
                
                result_state = old_state
                
                if faulty_flag:
                    print("FAULTY ACTION: Continuing")
                    continue
                else:
                    new_parameters = {}
                    
                    
                    raw_state_str = str(frozenset(sorted(result_state)))
                    new_label = str(util.zeroStringPad(str(current_layer+1),2)) + "-"  \
                              + str(hash(raw_state_str)) + "_" \
                              + hashlib.blake2s(raw_state_str.encode('utf-8'),salt=run_id[0:8].encode('utf-8')).hexdigest()
                                         
                   #new_label = str(util.zeroStringPad(str(current_layer+1),2)) + "-" + str(hash(frozenset(sorted(result_state))))
                    new_address = current_node.address + "-" + str(util.zeroStringPad(str(spawned_children),2))
                    new_domprob = copy.deepcopy(domprob)
                    new_initial_state = copy.deepcopy(saved_initial_state)
                    new_solution_steps = copy.deepcopy(somesolution)
                    new_expected_state = copy.deepcopy(result_state)
                    new_chapter_label = copy.copy(sequence_grouping_label)
                    #new_chapter_label = copy.copy(name_label_string)
                    
                    # [Check] : Evaluate individual intentions and update the state
                    for someintention in new_domprob.all_intentions:
                        eval_operator = planner_instance.planner_parameters['dp_parser'].domainproblem._AND_OPERATOR
                        eval_operand = someintention[1][0]
                        eval_value = planner_instance.planner_parameters['dp_parser'].evalPropositionTree(eval_operator, eval_operand, new_expected_state, 1, name = "goal_parsing")
                        
                        if eval_value:
                            #print(someintention)
                            #print("someintention[1][0] : " + str(someintention[1][0]))
                            #print(new_initial_state)
                            
                            #if str(eval_operand) in new_node.state:
                            #    print("[>>>] Remove from state")
                            #    new_node.state.remove(str(eval_operand))
                            #else:
                            #    print("[>>>] Not in state")
                            
                            #temp_state = set(new_node.state)
                            
                            
                            _intention_str = "['intends', "+str(someintention[0])+ ", " + str(someintention[1]) + "]"
                            #print(_intention_str)
                            if _intention_str in new_expected_state:
                                #print("[>>>] Remove from state")
                                new_expected_state.remove(_intention_str)
                                #new_initial_state.remove(str(someintention))
                                #frozenset(sorted(self.domainproblem.state))
                                #new_node.state = copy.copy(temp_state)
                            #else:
                            #    print("[>>>] Not in state")
                            
                            #if str(eval_operand) in new_node
                            
                            #print(new_domprob.all_intentions)
                            #print("========================")
                            new_domprob.all_intentions.remove(someintention)
                            
                            #print(new_domprob.all_intentions)
                            #print("========================")
                            #input()
                    
                    new_node = ChapterNode(new_label,new_address,new_chapter_label,new_domprob,personality,new_initial_state,new_solution_steps,new_expected_state)
                    
                    #for something in sorted(new_initial_state):
                    #    print(something)
                    #    
                    #print("----------------")
            
                    # Create a child for each one
                    
                    new_parameters['current_node']              = new_node
                    new_parameters['ncs']                       = ncs
                    new_parameters['identity']                  = identity
                    new_parameters['root_node']                 = root_node
                    new_parameters['neutral_obj_count']         = neutral_obj_count
                    new_parameters['current_layer']             = current_layer+1
                    new_parameters['run_id']                    = run_id
                    new_parameters['personality']               = personality
                    new_parameters['max_children']              = max_children
                    new_parameters['cc_start_execution']        = cc_start_execution
                    new_parameters['initial_state']             = copy.deepcopy(saved_initial_state)
                    new_parameters['final_state']               = copy.deepcopy(result_state)
                    new_parameters['runtime_threshold']         = runtime_threshold
                    new_parameters['algorithm']                 = algorithm
                    new_parameters['faulty_action_count']       = faulty_action_count
                    
                    chainer_search_space.add_node(new_label,body=new_node,layer=current_layer+1)
                    chainer_search_space.add_edge(current_node.label, new_node.label)
                    
                    #===================================
                    #print("parent_node_dbid : " + str(parent_node_dbid))
                    #print("...................")
                    diff1 = str(saved_initial_state.difference(result_state))
                    diff2 = str(result_state.difference(saved_initial_state))
                    
                    chapter_entry = PlanChapterInstance(
                                        id=run_id+"_"+new_node.address,
                                        narrative_instance_id=run_id, 
                                        chapter_number=current_layer+1, 
                                        chapter_address=new_node.address,
                                        chapter_label=new_node.chapter_label,
                                        initial_state=str(saved_initial_state),
                                        final_state=str(result_state),
                                        parent_chapter=parent_node_dbid,
                                        diff1=diff1,
                                        diff2=diff2,
                                        extra2=str(domprob.positive_goals),
                                        extra3=str(domprob.negative_goals)
                                    )
                    self.db.session.add(chapter_entry)
                    self.db.session.commit()
                    #try:
                    #    self.db.session.commit()
                    #except Exception:
                    #    print("COMMIT ERROR")
                    
                    some_action_ctr = 0
                    for some_action in new_node.solution_steps:
                        some_action_ctr += 1
                        #class ChapterInstanceAction(db.Model):
                        #    id = db.Column(db.String(128), primary_key=True)
                        #    chapter_id = db.Column(db.String(128), db.ForeignKey('chapter_instance.id'))
                        #    
                        #    action_string = db.Column(db.String(64))
                        #    action_string_hr = db.Column(db.String(128))
                        
                        
                        chapter_inst_action_entry = PlanChapterInstanceAction(
                                            id=run_id+"_"+new_node.address+"_"+str(some_action_ctr),
                                            chapter_id=run_id+"_"+new_node.address,
                                            narrative_instance_id=run_id,
                                            action_string=some_action.action_instance.getFunctionString()
                                        )
                                        
                        self.db.session.add(chapter_inst_action_entry)
                        self.db.session.commit()
                    
                    #===================================
                    
                    print("DIVING...")
                    result_flag = self.__planningRoutineDFS(chainer_search_space, new_parameters)
                    if(result_flag == False):
                        continue
                    else:
                        return result_flag
        
        
        
        
        #new_node_address = current_node.address + "-" + util.zeroStringPad(str(child_number),2)
        
        logstr = "TOTAL FAILURE : "
        for something in planner_instance._PG_ACTION_DENSITY_DICT.keys():
            print(something)
        util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
        print(logstr)
        
        #input()
        return False
        
    def generateSequenceTermFile(self, domain_full_label=None, sequence_term_filename=None):
        
        sequence_term_file = open(sequence_term_filename, "a+")
        
        stc_result = self.db.session.query(SequenceTermCategories) \
            .filter(SequenceTermCategories.domain == domain_full_label) \
            .all()
            
        for some_stc in stc_result:
            st_result = self.db.session.query(SequenceTerms) \
                .filter(SequenceTerms.sequence_term_cat_label == some_stc.sequence_term_cat_label) \
                .all()
            
            for some_st in st_result:
                line_output = ","
                
                line_output += (some_st.sequence_term_cat_label          if some_st.sequence_term_cat_label          is not None else "") + ","
                line_output += (some_st.main_label                       if some_st.main_label                       is not None else "") + ","
                line_output += (some_st.main_label_str                   if some_st.main_label_str                   is not None else "") + ","
                line_output += (some_st.sub_label                        if some_st.sub_label                        is not None else "") + ","
                line_output += (some_st.sub_label_str                    if some_st.sub_label_str                    is not None else "") + ","
                line_output += (some_st.name_label_str                   if some_st.name_label_str                   is not None else "") + ","
                line_output += (some_st.term_sequence                    if some_st.term_sequence                    is not None else "") + ","
                line_output += (some_st.term_sequence_grouping_label     if some_st.term_sequence_grouping_label     is not None else "") + ","
                line_output += (some_st.series                           if some_st.series                           is not None else "") + ","
                line_output += (some_st.sequence_term_full_label         if some_st.sequence_term_full_label         is not None else "") + ","
                line_output += (some_st.is_flavor                        if some_st.is_flavor                        is not None else "") + ","
                line_output += (some_st.is_variant                       if some_st.is_variant                       is not None else "") + ","
                line_output += (some_st.vacant1                          if some_st.vacant1                          is not None else "") + ","
                line_output += (some_st.main_object                      if some_st.main_object                      is not None else "") + ","
                line_output += (some_st.supporting_objects               if some_st.supporting_objects               is not None else "") + ","
                line_output += (some_st.intention_actor                  if some_st.intention_actor                  is not None else "") + ","
                line_output += (some_st.intention_target_state_predicate if some_st.intention_target_state_predicate is not None else "") + ","
                line_output += (some_st.intention_full_str               if some_st.intention_full_str               is not None else "") + ","
                line_output += (some_st.intention_type                   if some_st.intention_type                   is not None else "") + ","
                line_output += (some_st.predecessor_terms                if some_st.predecessor_terms                is not None else "") + ","
                line_output += (some_st.direct_chained_with              if some_st.direct_chained_with              is not None else "") + ","
                line_output += (some_st.successors                       if some_st.successors                       is not None else "") + ","
                line_output += (some_st.prerequisite_present_predicates  if some_st.prerequisite_present_predicates  is not None else "") + ","
                line_output += (some_st.prerequisite_target_predicates   if some_st.prerequisite_target_predicates   is not None else "") + ","
                line_output += (some_st.required_objects                 if some_st.required_objects                 is not None else "") + ","
                line_output += (some_st.in_chapter_pattern               if some_st.in_chapter_pattern               is not None else "") + ","
                line_output += (some_st.vacant2                          if some_st.vacant2                          is not None else "") + ","
                line_output += (some_st.vacant3                          if some_st.vacant3                          is not None else "") + ","
                line_output += (some_st.status                           if some_st.status                           is not None else "") + ","
                line_output += (some_st.notes                            if some_st.notes                            is not None else "")
                line_output += "\n"
                
                sequence_term_file.write(line_output)
        
        sequence_term_file.close()
            
    def generateChapterPatternsFile(self, domain_full_label=None, chapter_patterns_filename=None):
        
        chapter_patterns_file = open(chapter_patterns_filename, "a+")
        
        cp_result = self.db.session.query(ChapterPattern) \
            .filter(ChapterPattern.domain == domain_full_label) \
            .order_by(ChapterPattern.pattern_full_label.asc()) \
            .all()
            
        for some_cp in cp_result:

            line_output = ","
            
            line_output += (some_cp.chapter_pattern_cat_label if some_cp.chapter_pattern_cat_label is not None else "") + ","
            line_output += (some_cp.main_label                if some_cp.main_label                is not None else "") + ","
            line_output += (some_cp.main_label_str            if some_cp.main_label_str            is not None else "") + ","
            line_output += (some_cp.sub_label                 if some_cp.sub_label                 is not None else "") + ","
            line_output += (some_cp.sub_label_str             if some_cp.sub_label_str             is not None else "") + ","
            line_output += (some_cp.name_label_str            if some_cp.name_label_str            is not None else "") + ","
            line_output += (some_cp.vacant1                   if some_cp.vacant1                   is not None else "") + ","
            line_output += (some_cp.vacant2                   if some_cp.vacant2                   is not None else "") + ","
            line_output += (some_cp.pattern_sequence          if some_cp.pattern_sequence          is not None else "") + ","
            line_output += (some_cp.sequence_grouping_label   if some_cp.sequence_grouping_label   is not None else "") + ","
            line_output += (some_cp.series                    if some_cp.series                    is not None else "") + ","
            line_output += (some_cp.pattern_full_label        if some_cp.pattern_full_label        is not None else "") + ","
            line_output += (some_cp.sequence_term_cat_label   if some_cp.sequence_term_cat_label   is not None else "") + ","
            line_output += (str(some_cp.sequence_term_count)       if some_cp.sequence_term_count       is not None else "") + ","
            line_output += (str(some_cp.sequence_term_min_density) if some_cp.sequence_term_min_density is not None else "") + ","
            line_output += (str(some_cp.sequence_term_max_density) if some_cp.sequence_term_max_density is not None else "") + ","
            line_output += (str(some_cp.sequence_term_min_count)   if some_cp.sequence_term_min_count   is not None else "") + ","
            line_output += (str(some_cp.sequence_term_max_count)   if some_cp.sequence_term_max_count   is not None else "") + ","
            line_output += (some_cp.duplicates_allowed        if some_cp.duplicates_allowed        is not None else "") + ","
            line_output += (some_cp.vacant3                   if some_cp.vacant3                   is not None else "") + ","
            line_output += (some_cp.vacant4                   if some_cp.vacant4                   is not None else "") + ","
            line_output += "" + ","
            line_output += (some_cp.status                    if some_cp.status                    is not None else "") + ","
            line_output += (some_cp.notes                     if some_cp.notes                     is not None else "")
            
            line_output += "\n"
            
            chapter_patterns_file.write(line_output)
        
        chapter_patterns_file.close()
        
    def generatePredicateDescriptorsFile(self, domain_full_label=None, predicate_descriptors_filename=None):
        predicate_descriptors_file = open(predicate_descriptors_filename, "a+")
        
        pd_result = self.db.session.query(PredicateDescriptors) \
            .filter(PredicateDescriptors.domain == domain_full_label) \
            .order_by(PredicateDescriptors.term_sequence_grouping_label.asc()) \
            .all()
            
        for some_pd in pd_result:

            line_output = ","
            
            line_output += (some_pd.domain                       if some_pd.domain                       is not None else "") + ","
            line_output += (some_pd.main_label                   if some_pd.main_label                   is not None else "") + ","
            line_output += (some_pd.main_label_str               if some_pd.main_label_str               is not None else "") + ","
            line_output += (some_pd.sub_label                    if some_pd.sub_label                    is not None else "") + ","
            line_output += (some_pd.sub_label_str                if some_pd.sub_label_str                is not None else "") + ","
            line_output += (some_pd.name_label_str               if some_pd.name_label_str               is not None else "") + ","
            line_output += (some_pd.term_sequence                if some_pd.term_sequence                is not None else "") + ","
            line_output += (some_pd.term_sequence_grouping_label if some_pd.term_sequence_grouping_label is not None else "") + ","
            line_output += (some_pd.parameter_label              if some_pd.parameter_label              is not None else "") + ","
            line_output += (some_pd.parameter_type               if some_pd.parameter_type               is not None else "") + ","
            line_output += (str(some_pd.likelihood)              if some_pd.likelihood                   is not None else "") + ","
            line_output += (some_pd.min_unique                   if some_pd.min_unique                   is not None else "") + ","
            line_output += (some_pd.max_unique                   if some_pd.max_unique                   is not None else "") + ","
            line_output += (some_pd.duplicates_allowed           if some_pd.duplicates_allowed           is not None else "") + ","
            line_output += (some_pd.notes                        if some_pd.notes                        is not None else "") + ","
            line_output += ","
            
            line_output += "\n"
            
            predicate_descriptors_file.write(line_output)
        
        predicate_descriptors_file.close()
         
    def generateObjectNamesFile(self, domain_full_label=None, object_names_filename=None):
        object_names_file = open(object_names_filename, "a+")
        
        on_result = self.db.session.query(ObjectNames) \
            .filter(ObjectNames.domain == domain_full_label) \
            .all()
            
        for some_on in on_result:
        
            line_output = ","
            
            # [X] MAIN LABEL
            #line_output += (some_on.main_label  if some_on.main_label   is not None else "") + ","
            
            # [O] READABLE LABEL
            line_output += (some_on.readable_label  if some_on.readable_label is not None else "") + ","
            line_output += (some_on.object_type     if some_on.object_type    is not None else "") + ","
            line_output += (some_on.attribute1      if some_on.attribute1     is not None else "") + ","
            line_output += (some_on.attribute2      if some_on.attribute2     is not None else "") + ","
            line_output += (some_on.attribute3      if some_on.attribute3     is not None else "")
            line_output += "\n"
            
            object_names_file.write(line_output)
        
        object_names_file.close()
    
    def generate_location_file(self, run_id, location_map):

        existing_edges = self.db.session.query(LocationEdges) \
            .filter(LocationEdges.map_label == location_map) \
            .all()
            
        location_filename = _LOCATION_DIR + "location_map_" + run_id + ".txt"
        location_file = open(location_filename, "w")
        
        for someedge in existing_edges:
            
            from_node = self.db.session.query(LocationNode) \
                .filter(LocationNode.node_label == someedge.from_node) \
                .first()
                
            to_node = self.db.session.query(LocationNode) \
                .filter(LocationNode.node_label == someedge.to_node) \
                .first()
                
            location_file.write("['"+from_node.node_label+"', '"+from_node.node_type+"']|['"+to_node.node_label+"', '"+to_node.node_type+"']\n")
            
        #print("=================================================")
        location_file.close()
        return location_filename
        
    def generate_intention_template_file(self, run_id, domain_full_label):
        
        intention_template_filename = _INPUT_DIR + run_id + "/ncs_intentions_" + domain_full_label + ".csv"
        intention_template_file = open(intention_template_filename, "w")
        
        print(domain_full_label)
        
        domain_id_lookup = self.db.session.query(Domains.id) \
            .filter(Domains.domain_full_label == domain_full_label) \
            .as_scalar()
        
        self.domain_id = domain_id_lookup
        print("//----")
        print(domain_id_lookup)
        
        all_predicates = self.db.session.query(StatePredicateDef) \
            .filter(StatePredicateDef.domain_id.in_(domain_id_lookup)) \
            .filter(StatePredicateDef.mutability != "DEFAULT") \
            .all()
            
            
        output_str = "//,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,\n"
        intention_template_file.write(output_str)
        
        output_str = "//,Domain,Main Label,Secondary Label,Chapter Pattern,Grouping,Grouping_label,Series,Series_label,Intention Predicate Object Predicates,Intention Actor,Intention Predicate,Intention Full String,Likelihood,,,,,,\n"
        intention_template_file.write(output_str)
        
        group_ctr = 1
        for somepredicate in all_predicates:
            series_ctr = 1
            group_ctr_str = util.zeroStringPad(group_ctr, 4)
            series_ctr_str = util.zeroStringPad(group_ctr, 2)
            
            grouping_label_str = domain_full_label + "_" + somepredicate.predicate_label + "_" + group_ctr_str
            series_label = grouping_label_str + "_" + series_ctr_str
            
            parameter = []
            
            if (somepredicate.parameter1_label is not None) and (somepredicate.parameter1_label != ""):
                parameter.append([somepredicate.parameter1_label,somepredicate.parameter1_type])
            if (somepredicate.parameter2_label is not None) and (somepredicate.parameter2_label != ""):
                parameter.append([somepredicate.parameter2_label,somepredicate.parameter2_type])
            if (somepredicate.parameter3_label is not None) and (somepredicate.parameter3_label != ""):
                parameter.append([somepredicate.parameter3_label,somepredicate.parameter3_type])
            if (somepredicate.parameter4_label is not None) and (somepredicate.parameter4_label != ""):
                parameter.append([somepredicate.parameter4_label,somepredicate.parameter4_type])
            if (somepredicate.parameter5_label is not None) and (somepredicate.parameter5_label != ""):
                parameter.append([somepredicate.parameter5_label,somepredicate.parameter5_type])
            if (somepredicate.parameter6_label is not None) and (somepredicate.parameter6_label != ""):
                parameter.append([somepredicate.parameter6_label,somepredicate.parameter6_type])
            
            intention_object_predicates = "(?actor - actor)"
            
            for ctr in range(0,len(parameter)):
                intention_object_predicates += ";("+parameter[ctr][0]+" - "+parameter[ctr][1]+")"
            
            intention_actor = "?actor"
            
            for ctr in range(0,len(parameter)):
                if ctr == 0:
                    intention_predicate = "(" + somepredicate.predicate_label + " " + parameter[ctr][0]
                else:
                    intention_predicate += " " + parameter[ctr][0]
            intention_predicate += ")"
            
            intention_full_str = "(intends " + intention_actor + " " + intention_predicate + ")"
            
            likelihood = somepredicate.initial_intention_affinity
            
            output_str =    ""                                  + "," + \
                            domain_full_label                   + "," + \
                            somepredicate.predicate_label       + "," + \
                            ""                                  + "," + \
                            ""                                  + "," + \
                            group_ctr_str                       + "," + \
                            grouping_label_str                  + "," + \
                            series_ctr_str                      + "," + \
                            series_label                        + "," + \
                            intention_object_predicates         + "," + \
                            intention_actor                     + "," + \
                            intention_predicate                 + "," + \
                            intention_full_str                  + "," + \
                            str(likelihood)                     + "," + \
                            ",,,,,\n"
                            
            intention_template_file.write(output_str)
        
        intention_template_file.close()
        
        return intention_template_filename
            
    def execute(self,
                neutral_obj_count=0, 
                story_pattern="", 
                custom_story_pattern=None,
                random_story_pattern=None, 
                check_session=1,
                runtime_threshold=_RUNTIME_THRESHOLD_MINUTES,
                algorithm="goalgraphpaths",
                location_map="",
                p_arg=[]
                ):
        
        #======================================================================

        #======================================================================
        
        #print("Number of processors: ", mp.cpu_count())
        #input()
        cc_start_execution = datetime.datetime.now()
        for cc_try in range(1,_CHAPTERCHAIN_EXECUTE_TRY):
            
            if random_story_pattern is None:
                raise Exception("random_story_pattern is none")
                
            now = datetime.datetime.now()
            now_str = now.strftime("%Y%m%d_%H%M%S")
            
            _LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/LOG_ncsparser_" + now_str + ".txt"                                                         
            _LOG_EXECUTION_LOGFILE[1] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/LOG_chapterchainer_" + now_str + ".txt"                                                    
            _LOG_EXECUTION_LOGFILE[2] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_chapterchainer_" + self.domain_full_label + ".csv"          
            _LOG_EXECUTION_LOGFILE[3] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/CONSOLIDATEDLOG_chapterchainer_summary_" + self.domain_full_label + ".csv"  
            
            #======================================================================
            run_id = self.id + "_" + str(cc_try)
            user_id = self.user_id
            
            if not os.path.exists(_INPUT_DIR + run_id + "/"):
                os.makedirs(_INPUT_DIR + run_id + "/")
            
            #======================================================================
            
            # 0. Initialization
            logstr = "[...] Start ChapterChainer.execute()"
            
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=False)
            print(logstr + "\n")
            # [IMPROVEMENT JUNCTION]
            #   Remove hardcoded stuffs
            
            if p_arg == []:
                print("[...] Applying default p_args")
                alignment                   = ""
                goal_graph_depth            = 6
                plan_graph_depth            = 6
                nextstepsize                = 8
                nextsteprange               = 2
                solutions_per_goal          = 1
                unexplained_threshold       = 0   #Higher means more relaxed
                author_goal_branching_alloc = 50
                
                p_arg = [
                    alignment                   ,
                    goal_graph_depth            ,
                    plan_graph_depth            ,
                    nextstepsize                ,
                    nextsteprange               ,
                    solutions_per_goal          ,
                    unexplained_threshold       ,
                    author_goal_branching_alloc 
                ]
            
            #now = datetime.datetime.now()
            #now_str = now.strftime("%Y%m%d_%H%M%S")
            
            solution_filename = _LOG_DIR + "SOLUTION_" + self.domain_full_label + "-" + str(run_id) + ".txt"
            
            
            

            
            # 1. Read domain and pre-build problem common elements
            domain_filename = _INPUT_DIR + self.domain_full_label + ".pddl"
            domprob = DomainProblem()
            #print(domain_filename)
            domprob.parseDomain(domain_filename)
            
            dp_parser = DomainProblemParser(domprob)
            
            
            
            # 2. Construct Chapter Patterns and other supporting descriptors
            self.ncs = NarrativeChapterStructure(self.domain_full_label,neutral_obj_count)
            
            sequence_term_filename = _INPUT_DIR + run_id + "/ncs_terms_" + self.domain_full_label + ".csv"
            self.generateSequenceTermFile(self.domain_full_label, sequence_term_filename)
            self.ncs.readSequenceTermsFromFile(sequence_term_filename)
            
            chapter_patterns_filename = _INPUT_DIR + run_id + "/ncs_patterns_" + self.domain_full_label + ".csv"
            self.generateChapterPatternsFile(self.domain_full_label, chapter_patterns_filename)
            self.ncs.readChapterPatternsFromFile(chapter_patterns_filename)
            
            if random_story_pattern:
                self.ncs.setChapterPattern(mode1="random")
            else:
                self.ncs.setChapterPattern(mode1="like",chapter_pattern_str=story_pattern)
            
            predicate_descriptors_filename = _INPUT_DIR + run_id + "/ncs_predicate_descriptors_" + self.domain_full_label + ".csv"
            self.generatePredicateDescriptorsFile(self.domain_full_label, predicate_descriptors_filename)
            self.ncs.readPredicateDescriptorsFromFile(predicate_descriptors_filename)
            
            object_names_filename = _INPUT_DIR + run_id + "/ncs_object_names_" + self.domain_full_label + ".csv"
            self.generateObjectNamesFile(self.domain_full_label, object_names_filename)
            self.ncs.readObjectNamesLookupFromFile(object_names_filename)
            
            intention_template_filename = self.generate_intention_template_file(run_id, self.domain_full_label)
            self.ncs.readIntentionTemplatesFromFile(intention_template_filename)
            
            # -- Chapter Sequences
            self.ncs.buildChapterSequenceInstance()
            # -- Problem Objects
            settings = {}
            
            if location_map == "":
                raise Exception("Invalid location map label: <empty>")
            
            #location_file = _INPUT_DIR + "location_map_" + self.domain_full_label + ".txt"
            location_filename = self.generate_location_file(run_id, location_map)
            self.ncs.buildProblemObjects(domprob, neutral_obj_count=neutral_obj_count,location_file=location_filename)
            
            # -- Problem State
            settings = {}
            self.ncs.buildProblemState(domprob, settings)
            
            
            chapter_pattern_category_label = self.ncs.chapter_pattern['chapter_pattern_category_label']
            sequence_grouping_label = self.ncs.chapter_pattern['sequence_grouping_label']
            _category = self.ncs.chapter_pattern['category_grouping_lookup'][chapter_pattern_category_label]
            _sequence_group = self.ncs.chapter_pattern['sequence_grouping_label']
            
            for _some_key in self.ncs.chapter_pattern['lookup'].keys():
                if _sequence_group in _some_key:
                    _sequence_item = self.ncs.chapter_pattern['lookup'][_some_key]
            narrative_label = _sequence_item[1] + " - " + _sequence_item[2]
            
            if check_session!=0:
                active_planners = self.db.session.query(
                    UserActivePlanners.narrative_id, UserActivePlanners.status
                ).filter(
                    and_(
                        (UserActivePlanners.user_id == self.user_id),
                        (UserActivePlanners.status == "IN_PROGRESS")
                    )
                ).all()
                
                if ((len(active_planners) > 0) and (check_session==1)):
                    existing_planner_session = UserActivePlanners.query.filter_by(narrative_id=run_id).update(dict(status="FAILED", date_end=datetime.datetime.utcnow()))
                    self.db.session.commit()
                    
                    logstr = "User '" + self.user_id + "' has an active session; Terminating planner."
                    util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                    print(logstr)
                    return False
                elif (cc_try <= 1):
                    #====[ Database session entries
                    narrative_entry = NarrativeInstance(
                                            narrative_id=run_id, 
                                            story_pattern=sequence_grouping_label,
                                            user_id=user_id, 
                                            narrative_label=narrative_label,
                                            algorithm=algorithm,
                                            map_label=location_map
                                            )
                    self.db.session.add(narrative_entry)
                    self.db.session.commit()
                    
                    new_planner_session = UserActivePlanners(user_id=self.user_id,narrative_id=run_id,status="IN_PROGRESS")
                    self.db.session.add(new_planner_session)
                    self.db.session.commit()
            
            
            logstr = " [...] Chapters "
            util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=False)
            print(logstr)
            for somechapter in self.ncs.chapter_sequence:
                logstr = "\t" + str(somechapter)
                util.log(_LOG_EXECUTION_LOGFILE[1], logstr, "line/txt", enabled=False)
                print(logstr)        
            #input()
            chapter_ctr = 0
            self.chapters = []
            

            
            # Planner settings
            identity = "author"
            personality_01 = Personality(p_arg[0],p_arg[1],p_arg[2],p_arg[3],p_arg[4],p_arg[5], p_arg[6], p_arg[7])
            personality_01.setAlignmentValues(0,0)
            load_mode = ""
            
            #----------------------------------------------------------------------------
            #--- [Start] DFS Chapter Chainer
            
            chainer_search_space = DiGraph()
            
            parameters = {}
            
            raw_state_str = str(frozenset(sorted(domprob.state)))
            label     = str(util.zeroStringPad("0",2)) + "-"  \
                      + str(hash(raw_state_str)) + "_" \
                      + hashlib.blake2s(raw_state_str.encode('utf-8'),salt=run_id[0:8].encode('utf-8')).hexdigest()
                                  
           #label = str(util.zeroStringPad("0",2)) + "-" + str(hash(frozenset(sorted(domprob.state))))
            address = str(util.zeroStringPad("1",2))
            initial_state = copy.deepcopy(domprob.state)
            
            print("-------------------------------")
            print(initial_state)
            print("-------------------------------")
            #input()
            
            solution_steps = []
            expected_state = copy.deepcopy(domprob.state)
            chapter_label = "NONE"
            chainer_search_space_root = ChapterNode(label,address,chapter_label,domprob,personality_01,initial_state,solution_steps,expected_state)
            
            parameters['current_node']              = chainer_search_space_root
            parameters['ncs']                       = self.ncs
            parameters['identity']                  = identity
            parameters['root_node']                 = chainer_search_space_root
            parameters['neutral_obj_count']         = neutral_obj_count
            parameters['current_layer']             = 0
            parameters['run_id']                    = run_id
            parameters['personality']               = personality_01
            #parameters['max_children']              = int(personality_01.solutions_per_goal + (personality_01.solutions_per_goal * 0.4))
            parameters['max_children']              = 5
            parameters['cc_start_execution']        = cc_start_execution
            parameters['initial_state']             = copy.deepcopy(initial_state)
            parameters['final_state']               = copy.deepcopy(expected_state)
            parameters['runtime_threshold']         = runtime_threshold
            parameters['algorithm']                 = algorithm
            parameters['faulty_action_count']       = 0
            
            chainer_search_space.add_node(label,body=chainer_search_space_root,layer=0)
            
            chapter_entry = PlanChapterInstance(
                                id=run_id+"_"+chainer_search_space_root.address,
                                narrative_instance_id=run_id, 
                                chapter_number=0, 
                                chapter_address=chainer_search_space_root.address,
                                chapter_label=chainer_search_space_root.chapter_label,
                                initial_state=str(initial_state),
                                final_state=str(initial_state),
                                extra1="Initial shiet"
                            )
            self.db.session.add(chapter_entry)
            self.db.session.commit()
            
            
            result_flag = self.__planningRoutineDFS(chainer_search_space, parameters)
            
            #print("---// breakpoint")
            #input()
            #except Exception:
            #    existing_planner_session = UserActivePlanners.query.filter_by(narrative_id=run_id).update(dict(status="FAILED", date_end=datetime.datetime.utcnow()))
            #    self.db.session.commit()            
            #    return False
            
            #--- [End] DFS Chapter Chainer
            #----------------------------------------------------------------------------
            
            cc_end_execution = datetime.datetime.now()
            elapsed_time = cc_end_execution - cc_start_execution
            elapsed_seconds = elapsed_time.total_seconds()
            elapsed_minutes = elapsed_time.total_seconds() / 60
            
            
            error_flag = not result_flag
            if error_flag:
                success_str = "ERROR"
            else:
                success_str = "SUCCESS"
                end_node = result_flag
            

            return_string = ""
            if error_flag:
                
                try:
                    existing_planner_session = UserActivePlanners.query.filter_by(narrative_id=run_id).update(dict(status="FAILED", date_end=datetime.datetime.utcnow()))
                    self.db.session.commit()            
                except Exception:
                    print("UserActivePlanners(narrative_id='"+str(run_id)+"') does not exists")
                #return False
                continue
                
            else:
                solution_path = nx.shortest_path(chainer_search_space, chainer_search_space_root.label, end_node.label)
                
                
                
                parent_node_dbid = None
                
                hr_loop_ctr = 0
                na_alternator_ctr = 0
                
                roles_hr = ""
                
                for some_value in self.ncs.hr_problem_objvar_dict.values():
                    roles_hr += some_value + ";"
                
                solution_node_ctr = 0
                parent_address = ""
                from_node_label = ""
                to_node_label = ""
                
                plan_graph_node_parent = ""
                first = True
                for some_node in solution_path:
                    
                    solution_node_ctr += 1
                    if first:
                        first = False
                    else:
                    
                        subchapter_solution = chainer_search_space.nodes[some_node]['body'].solution_steps
                        chapter_ctr = chainer_search_space.nodes[some_node]['layer']
                        chapter_label = chainer_search_space.nodes[some_node]['body'].chapter_label
                        current_node = chainer_search_space.nodes[some_node]['body']
                        
                        
                        
                        chapter_entry = SolutionChapterInstance(
                                            id=run_id+"_"+current_node.address,
                                            narrative_instance_id=run_id, 
                                            chapter_number=chapter_ctr, 
                                            chapter_address=current_node.address,
                                            chapter_label=current_node.chapter_label,
                                            initial_state=str(current_node.initial_state),
                                            final_state=str(current_node.expected_state)
                                        )
                        self.db.session.add(chapter_entry)
                        self.db.session.commit()
                        
                        
                        if len(subchapter_solution) <= 0:
                                logstr =    ";" + run_id                        +  \
                                            ";Chapter " + str(chapter_ctr)      +  \
                                            ";" + chapter_label                 +  \
                                            ";No action taken"
                                util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                                
                                add_str =   "Chapter " + str(chapter_ctr)    +  \
                                            ";" + chapter_label              +  \
                                            ";No action taken"
                                return_string += add_str + "|"
                                                        
                                filter = {"adjacency":True, "intentions":True, "normal":True}
                                initial_state_hrparagraph_all              = dp_parser.convertToHRParagraph(current_node.initial_state,filter=filter)
                                filter = {"adjacency":False, "intentions":False, "normal":True}
                                initial_state_hrparagraph_norm_only        = dp_parser.convertToHRParagraph(current_node.initial_state,filter=filter)
                                filter = {"adjacency":True, "intentions":False, "normal":False}
                                initial_state_hrparagraph_adjacency_only   = dp_parser.convertToHRParagraph(current_node.initial_state,filter=filter)
                                filter = {"adjacency":False, "intentions":True, "normal":False}
                                initial_state_hrparagraph_intentions_only  = dp_parser.convertToHRParagraph(current_node.initial_state,filter=filter)
                                
                                
                                chapter_inst_action_entry = SolutionChapterInstanceAction(
                                                    id=run_id+"_"+prev_node.address+"_0",
                                                    chapter_id=run_id+"_"+prev_node.address,
                                                    narrative_instance_id=run_id,
                                                    action_string="none",
                                                    action_string_hr="no actions performed.",
                                                    initial_state_hrparagraph=initial_state_hrparagraph_all,
                                                    negative_change_hrparagraph="",
                                                    positive_change_hrparagraph="",
                                                    final_state_hrparagraph_all             = initial_state_hrparagraph_all             ,
                                                    final_state_hrparagraph_norm_only       = initial_state_hrparagraph_norm_only       ,
                                                    final_state_hrparagraph_adjacency_only  = initial_state_hrparagraph_adjacency_only  ,                                         
                                                    final_state_hrparagraph_intentions_only = initial_state_hrparagraph_intentions_only ,                                         
                                                    
                                                    
                                                    explained_by="none",
                                                    explained_by_hr="no actions performed.",
                                                    
                                                    roles = roles_hr,
                                                    reserved1 = ""
                                                )
                            
                                
                                
                                
                                self.db.session.add(chapter_inst_action_entry)
                                self.db.session.commit()
                                
                        else:
                            some_action_ctr = 0
                            #===============================
                            # Raw Solution Actions
                            
                            
                            for some_step in subchapter_solution:
                                some_action_ctr += 1
                                
                                logstr = ";" + run_id                        +  \
                                         ";Chapter " + str(chapter_ctr)      +  \
                                         ";" + chapter_label                 +  \
                                         ";" + some_step.action_instance.getFunctionString()
                                util.log(_LOG_EXECUTION_LOGFILE[2], logstr, "line/txt")
                                
                                add_str =   "Chapter " + str(chapter_ctr)    +  \
                                            ";" + chapter_label              +  \
                                            ";" + some_step.action_instance.getFunctionString()
                                            
                                return_string += add_str + "|"
            
                                if len(some_step.action_instance.humanreadables) > 0:
                                    action_string_hr = str(random.choice(some_step.action_instance.humanreadables))
                                else:
                                    action_string_hr = some_step.action_instance.getFunctionString()
                                
                                # Explained by:
                                explained_by_str = ""
                                explained_by_hr_str = ""
                                if some_step.explanation_paths is not None:
                                    for _somepath in some_step.explanation_paths:
                                        # Can have multiple explanation paths
                                        for _someaction in _somepath:
                                            if str(_someaction).lower() != "none":
                                                explained_by_str += _someaction.getFunctionString() + ";"
                                                explained_by_hr_str += _someaction.humanreadables[0]+ ";"
                                # Soft plan:
                                goal_graph_soft_plan = ""
                                goal_graph_soft_plan_hr_str = ""
                                
                                for _someaction in some_step.goal_graph_soft_plan:
                                    goal_graph_soft_plan += _someaction.getFunctionString() + ";"
                                    goal_graph_soft_plan_hr_str += _someaction.humanreadables[0] + ";"
                                # =====
                                
                                some_step.initial_state_hrparagraph = dp_parser.convertToHRParagraph(some_step.initial_state)
                                some_step.negative_change_hrparagraph = dp_parser.convertToHRParagraph(some_step.initial_state - some_step.final_state)
                                some_step.positive_change_hrparagraph = dp_parser.convertToHRParagraph(some_step.final_state - some_step.initial_state)
                                
                                _filter = {"adjacency":True, "intentions":True, "normal":True}
                                some_step.final_state_hrparagraph_all              = dp_parser.convertToHRParagraph(some_step.final_state,filter=_filter)
                                _filter = {"adjacency":False, "intentions":False, "normal":True}
                                some_step.final_state_hrparagraph_norm_only        = dp_parser.convertToHRParagraph(some_step.final_state,filter=_filter)
                                _filter = {"adjacency":True, "intentions":False, "normal":False}
                                some_step.final_state_hrparagraph_adjacency_only   = dp_parser.convertToHRParagraph(some_step.final_state,filter=_filter)
                                _filter = {"adjacency":False, "intentions":True, "normal":False}
                                some_step.final_state_hrparagraph_intentions_only  = dp_parser.convertToHRParagraph(some_step.final_state,filter=_filter)
                                
                                plan_graph_node_label = current_node.label
                                chapter_inst_action_entry = SolutionChapterInstanceAction(
                                                    id=run_id+"_"+prev_node.address+"_"+str(some_action_ctr),
                                                    chapter_id=run_id+"_"+prev_node.address,
                                                    narrative_instance_id=run_id,
                                                    
                                                    action_string                           = some_step.action_instance.getFunctionString(),
                                                    action_string_hr                        = action_string_hr,
                                                    initial_state_hrparagraph               = some_step.initial_state_hrparagraph,
                                                    negative_change_hrparagraph             = some_step.negative_change_hrparagraph,
                                                    positive_change_hrparagraph             = some_step.positive_change_hrparagraph,
                                                    final_state_hrparagraph_all             = some_step.final_state_hrparagraph_all,
                                                    final_state_hrparagraph_norm_only       = some_step.final_state_hrparagraph_norm_only,
                                                    final_state_hrparagraph_intentions_only = some_step.final_state_hrparagraph_intentions_only,
                                                    final_state_hrparagraph_adjacency_only  = some_step.final_state_hrparagraph_adjacency_only,
                                                    
                                                    explained_by                            = explained_by_str,
                                                    explained_by_hr                         = explained_by_hr_str,
                                                    
                                                    roles                                   = roles_hr,
                                                    
                                                    plan_graph_node_label                   = some_step.plan_graph_node_label,
                                                    plan_graph_node_parent                  = some_step.plan_graph_node_parent,
                                                    goal_graph_soft_plan                    = goal_graph_soft_plan,
                                                    reserved1                               = goal_graph_soft_plan_hr_str,
                                                    reserved2                               = str(some_step.soft_plan_source)
                                                    
                                                )
                            
                                plan_graph_node_parent = current_node.label
                                
                                self.db.session.add(chapter_inst_action_entry)
                                self.db.session.commit()
                            
                            #===============================
                            # HR Sequence
                            
                            
                            for chapter_instance_action in subchapter_solution:
                                last_cia = chapter_instance_action
                                hr_loop_ctr += 1
                                
                                hrparagraph = ""
                                #===========================
                                if hr_loop_ctr==1:
                                
                                    # Paragraph 0
                                    hrparagraph = "[Intro - Roles ]" + "<br>" + roles_hr.replace(";","<br>")
                                    hr_sequence_entry = SolutionHRSequence(
                                                        #id=run_id+"_"+current_node.address+"_"+str(some_action_ctr) + "_a",
                                                        chapter_id=run_id+"_"+current_node.address,
                                                        narrative_instance_id=run_id,
                                                        hrparagraph=hrparagraph,
                                                        explained_by_hr=""
                                                    )
                                    self.db.session.add(hr_sequence_entry)
                                    self.db.session.commit()
                                    
                                    # Paragraph 1
                                    hrparagraph = "[Intro - Initial State] " + chapter_instance_action.final_state_hrparagraph_norm_only
                                    hr_sequence_entry = SolutionHRSequence(
                                                        #id=run_id+"_"+current_node.address+"_"+str(some_action_ctr) + "_a",
                                                        chapter_id=run_id+"_"+current_node.address,
                                                        narrative_instance_id=run_id,
                                                        hrparagraph=hrparagraph,
                                                        explained_by_hr=""
                                                    )
                                    self.db.session.add(hr_sequence_entry)
                                    self.db.session.commit()
                                    
                                    # Paragraph 2
                                    hrparagraph = "[Intro - Character Intentions] " + chapter_instance_action.final_state_hrparagraph_intentions_only
                                    hr_sequence_entry = SolutionHRSequence(
                                                        #id=run_id+"_"+current_node.address+"_"+str(some_action_ctr) + "_b",
                                                        chapter_id=run_id+"_"+current_node.address,
                                                        narrative_instance_id=run_id,
                                                        hrparagraph=hrparagraph,
                                                        explained_by_hr=""
                                                    )
                                    self.db.session.add(hr_sequence_entry)
                                    self.db.session.commit()
                                    
                                    
                                else:
                                    
                                    if chapter_instance_action.action_instance is None:
                                    
                                        if na_alternator_ctr == 0:
                                            hrparagraph = "[NA] " + chapter_instance_action.final_state_hrparagraph_intentions_only
                                            na_alternator_ctr = 1
                                            
                                        elif na_alternator_ctr == 1:
                                            hrparagraph = "..."
                                            na_alternator_ctr = 0
                                        explained_by_hr=""
                                    else:   
                                    
                                        hrparagraph = "[Norm] " + random.choice(chapter_instance_action.action_instance.humanreadables).replace('"','')
                                        
                                        if chapter_instance_action.negative_change_hrparagraph != "":
                                            hrparagraph += "[-] " + chapter_instance_action.negative_change_hrparagraph.replace('"','').replace('.','') + "-- is no longer true. "
                                        
                                        if chapter_instance_action.positive_change_hrparagraph != "":
                                            hrparagraph += "[+] " + chapter_instance_action.positive_change_hrparagraph.replace('"','').replace('.','') + "."
                                            
                                        explained_by_hr = ""
                                        contributary_hr = ""
                                        _done_set = []
                                        
                                        #print("POTATO")
                                        #print(type(chapter_instance_action))
                                        #print(chapter_instance_action.explained_by_list)
                                        #for something in chapter_instance_action.explained_by_list:
                                        #    print(something)
                                        
                                        for some_step_tuple in chapter_instance_action.explained_by_list:
                                            #print(some_step_tuple)
                                            # some_step_tuple :
                                            # [('talia', <pddllib.Predicate object at 0x00000207655EB3C8>, False)]
                                            #print(type(chapter_instance_action.action_instance.agents))
                                            #print(chapter_instance_action.action_instance.agents)
                                            #input()
                                            
                                            _found_flag = False
                                            for _some_agent in chapter_instance_action.action_instance.agents:
                                                if some_step_tuple[0] == _some_agent[0]:
                                                    _found_flag = True
                                                    break
                                                    
                                            if _found_flag:
                                                explained_by_hr += "intention of " + str(some_step_tuple[0]) + " that: " + random.choice(some_step_tuple[1].humanreadables) + ";"
                                            else:
                                                contributary_hr += "intention of " + str(some_step_tuple[0]) + " that: " + random.choice(some_step_tuple[1].humanreadables) + ";"
                                            
                                        #input()
                                        
                                        
                                    hr_sequence_entry = SolutionHRSequence(
                                                        #id=run_id+"_"+current_node.address+"_"+str(some_action_ctr),
                                                        chapter_id=run_id+"_"+current_node.address,
                                                        narrative_instance_id=run_id,
                                                        hrparagraph=hrparagraph,
                                                        explained_by_hr = explained_by_hr,
                                                        contributary_hr = contributary_hr
                                                    )
                                    self.db.session.add(hr_sequence_entry)
                                    self.db.session.commit()
                                            
                            
                            print("solution_node_ctr:" + str(solution_node_ctr) + " == len(solution_path):" + str(len(solution_path)))
                            if solution_node_ctr == len(solution_path):
                            
                                #===========================    
                                # Last chapter final state

                                hrparagraph = "[Finale - Final State] " + chapter_instance_action.final_state_hrparagraph_norm_only
                                hr_sequence_entry = SolutionHRSequence(
                                                    #id=run_id+"_"+current_node.address+"_"+str(some_action_ctr) + "_a",
                                                    chapter_id=run_id+"_"+current_node.address,
                                                    narrative_instance_id=run_id,
                                                    hrparagraph=hrparagraph
                                                )
                                self.db.session.add(hr_sequence_entry)
                                self.db.session.commit()
            
                    prev_node = chainer_search_space.nodes[some_node]['body']
                    
                logstr = "[...] End ChapterChainer.execute() "
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr + "\n")
            
            existing_planner_session = UserActivePlanners.query.filter_by(narrative_id=run_id).update(dict(status="SUCCESS", date_end=datetime.datetime.utcnow()))
            self.db.session.commit()
            break

        logstr = ";" + run_id                                       +               \
                 ";" + self.ncs.chapter_pattern['sequence_grouping_label'] +        \
                 ";" + str(elapsed_seconds)                         +               \
                 ";" + str(elapsed_minutes)                         +               \
                 ";" + str(len(chainer_search_space.nodes()))       +               \
                 ";" + str(neutral_obj_count)                       +               \
                 ";" + success_str                                  +               \
                 ";" + algorithm                                    +               \
                 ";" + str(runtime_threshold)                       +               \
                 ";" + str(self._faulty_action_count)               +               \
                 ";" + str(location_map)
                 
        util.log(_LOG_EXECUTION_LOGFILE[3], logstr, "line/txt", header="sep=;\nDatetime;Run ID;Story Template;Elapsed-Seconds;Elapsed-Minutes;Chapter Chainer Search Space Nodes;Neutral Object Count;Status;Algorithm;Runtime Threshold;Faulty Action Count;Location Map")
        return return_string
        
        
#------------------------------------------------
#    Execute



#------------------------------------------------
#    Main

def main(self):

    from flask_app import db
            
    # 0. Logging setup
    for main_loop_ctr in range(0,999):
        for neutral_obj_count in [0]:
            for try_ctr in range(0,1):
                #for algorithm in ["goalgraphpaths", "ggp_dr1_hybrid", "fullrandom", "directedrandom1"]:
                #for algorithm in ["fullrandom"]:
                #for algorithm in ["directedrandom1"]:
                for algorithm in ["goalgraphmultipath"]:
                    for domain_loc_tuple in [
                        #("fantasy_default_01","fantasy4loccircular")
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular")
                        #("sciencefiction_aliensandmecha_03","scififvamap001")
                        #("sliceoflife__06","solsimplermap")
                        
                        #("anjicustom_lightfantasy_08","lifmediummaze")
                        #("anjicustom_lightfantasy_08","fantasy4loccircular")
                        
                        
                        #("fantasy_default_01","fantasy4loccircular", "thequest")
                        
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","smalltest")
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","smalltest")
                        
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","zerocriticalitypositivetest") ,
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","zerocriticalitynegativetest") ,
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","zeromutabilitypositivetest")  ,
                        #("fantasy_defaultpetdomainsmall_10","fantasy4loccircular","zeromutabilitynegativetest")  ,
                        
                        
                        #("fantasy_defaultpetdomainsmallquest_11","testlinear3","smallquesttest")   ,
                        #("fantasy_defaultpetdomainsmallquest_11","testlinear4","smallquesttest")   ,
                        #("fantasy_defaultpetdomainsmallquest_11","testlinear5","smallquesttest")   ,
                        #("fantasy_defaultpetdomainsmallquest_11","testcomplete3","smallquesttest") ,
                        #("fantasy_defaultpetdomainsmallquest_11","testcomplete4","smallquesttest") ,
                        #("fantasy_defaultpetdomainsmallquest_11","testcomplete5","smallquesttest")
                        
                        
                        #("fantasy_default_01","fantasy4loccircular","overcomemonster") ,
                        #("fantasy_default_01","fantasy4loccircular","overcomevillain") ,
                        #("fantasy_default_01","fantasy4loccircular","ragstoriches"   ) ,
                        #("fantasy_default_01","fantasy4loccircular","thequest"       ) ,
                        #("fantasy_default_01","fantasy4loccircular","tragedy"        ) ,
                        #("fantasy_default_01","fantasy4loccircular","voyageandreturn")
                        
                        
                        #("anjicustom_lightfantasy_08","lifmediummaze","anjlfexploringthemaze01"),
                        #("anjicustom_lightfantasy_08","lifmediummaze","anjlfexploringthemaze02"),
                        #("anjicustom_lightfantasy_08","lifmediummaze","anjlfexploringthemaze03"),
                        
                        #("sliceoflife__06","solsimplermap","solconflicttofriendship"),
                        #("sliceoflife__06","solsimplermap","solfriendshiptoconflict")
                        
                        #("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsfsimplemission1"),
                        #("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsfextractionmission1")
                        #("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsftellabilitytest")
                        
                        #("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsftellabilitytest_nsfs_1"),
                        #("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsftellabilitytest_ns_2")
                        ("anjicustom_sciencefictionaliensvsmarines_09","avmterraformingfacilitysmall","anjsftellabilitytest2_1")
                        
                        #("sciencefiction_aliensandmecha_03","scififvamap001", "fvafarmervictorysimple01"        ) ,
                        #("sciencefiction_aliensandmecha_03","scififvamap001", "fvaalienvictorysimple01"         ) ,
                        #("sciencefiction_aliensandmecha_03","scififvamap001", "fvafarmervictoryintermediate01"  ) ,
                        #("sciencefiction_aliensandmecha_03","scififvamap001", "fvaalienvictoryintermediate01"   )
                        
                    ]:
                                    #location_map="scififvamap001",
                                    #location_map="fantasy4loccircular",
                                    #location_map="solsimplermap",

                        # for now, runtime_threshold only throtlles coreplanner
                        #for runtime_threshold in [8,60]:
                        for runtime_threshold in [30]:
                        
                            #for story_pattern in [
                                    #"rebirth"         ,
                                    #"overcomemonster" ,
                                    #"overcomevillain" ,
                                    #"ragstoriches"    ,
                                    #"thequest"        ,
                                    #"tragedy"         ,
                                    #"voyageandreturn"
                                    #
                                    #"ragstoriches"
                                    #"test"
                                    
                                    #"overcomemonster"
                                    
                                    #"overcomemonster_normal"   ,
                                    #"overcomevillain_normal"   ,
                                    #"thequest_normal"          ,
                                    #"overcomemonster_refinery" ,
                                    #"overcomevillain_refinery" ,
                                    #"thequest_refinery"        
                                    
                                    # FVA"
                                    #"fvainitialtest"
                                    #"phase1test"   
                                    #"phase2test"
                                    #"phase3test"
                                    #"macrotest"
                                    #"fvafarmervictorysimple01"         ,
                                    #"fvaalienvictorysimple01"          ,
                                    #"fvafarmervictoryintermediate01"   ,
                                    #"fvaalienvictoryintermediate01"
                                    
                                    
                                    # HMC
                                    #"hmctest1"
                                    #"hmctest2"
                                    #"hmctest3"
                                    #"foralltest2"
                                    
                                    #SOL
                                    #"solconflicttofriendship"
                                    #"solsimplertest01"
                                    #"solsimplertest02"
                                    #"solconflicttofriendship",
                                    #"solfriendshiptoconflict"
                                    #"solfriendtest"
                                    #"solfriendtest2"
                                    #"solfriendtest3"
                                    
                                    
                                    #ANJI_LF_LIF
                                    #"anjlfexploringthemaze01",
                                    #"anjlfexploringthemaze02",
                                    #"anjlfexploringthemaze03"
                                    
                            #]:
                            
                            story_pattern = domain_loc_tuple[2]
                            
                            now = datetime.datetime.now()
                            now_str = now.strftime("%Y%m%d_%H%M%S")
                            
                            run_id = now_str + "_" + secrets.token_hex(4)
                            #domain_full_label = "fantasy_default_01"
                            #domain_full_label = "sciencefiction_aliensandmecha_03"
                            #domain_full_label = "fantasy_fable_05"
                            domain_full_label = domain_loc_tuple[0]
                            
                            user_id = "dj.isla"
                            chainer = ChapterChainer(
                                id=run_id, 
                                user_id=user_id,
                                domain_full_label=domain_full_label, 
                                db=db
                            )
                            
                            random_story_pattern = False
                            
                            alignment                   = ""
                            goal_graph_depth            = 4
                            plan_graph_depth            = 6
                            nextstepsize                = 6
                            nextsteprange               = 2
                            solutions_per_goal          = 2
                            unexplained_threshold       = 100   #Higher means more relaxed
                            author_goal_branching_alloc = 70
                            
                            p_arg = [
                                alignment                   ,
                                goal_graph_depth            ,
                                plan_graph_depth            ,
                                nextstepsize                ,
                                nextsteprange               ,
                                solutions_per_goal          ,
                                unexplained_threshold       ,
                                author_goal_branching_alloc 
                            ]
                            
                            success_flag = chainer.execute(
                                neutral_obj_count=neutral_obj_count,
                                story_pattern=story_pattern,
                                random_story_pattern=random_story_pattern,
                                check_session=2,
                                runtime_threshold=runtime_threshold,
                                algorithm=algorithm,
                                location_map=domain_loc_tuple[1],
                                #location_map="scififvamap001",
                                #location_map="fantasy4loccircular",
                                #location_map="solsimplermap",
                                p_arg=p_arg
                            )
            
        
    # 1. Run everything
    
    #for main_loop in range(0,999):
    #    for neutral_obj_count in range(0,1):
    #        for algorithm in ["goalgraphmultipath"]:
    #            for setup_tuple in [
    #                
    #                #"fantasy_default_01"
    #                #   "overcomemonster" ,
    #                #   "overcomevillain" ,
    #                #   "ragstoriches"    ,
    #                #   "thequest"        ,
    #                #   "tragedy"         ,
    #                #   "voyageandreturn"
    #                ()
    #                
    #                #"sciencefiction_aliensandmecha_03"
    #                #"sliceoflife__06"
    #            
    #            ]:
    #        
    #        
    #            for try_ctr in range(0,999):
        
        
if __name__ == '__main__':
    main(sys.argv)