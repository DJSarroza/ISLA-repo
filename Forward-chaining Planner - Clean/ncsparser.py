import sys
import copy
import networkx as nx
import random
import pickle
import datetime
import ast
import utility as util
import terrainutil as tu
import pddlglobals

from pddllib import DomainProblem

_COMMENT_STRING = "//"


_LOG_EXECUTION_LOGFILE = ["",""]
_LOG_DIR = "./logs/"
#_LOG_DIR = "/home/sarrozadj/ISLA_online/logs/"

class NarrativeChapterStructure:
    'Object that represents chapter sequences and structures'

    def __isComment(self, somestring:str):
        tempstring = somestring.lstrip()
        
        #print(tempstring)
        
        if(len(tempstring) < 2):
            #print("False")
            #input()
            return False
        elif(tempstring[0:2] == _COMMENT_STRING):
            #print("True")
            #input()
            return True
        else:
            #print("False")
            #input()
            return False

    
    def __init__(self, domain_full_label:str, neutral_obj_count=0):
        #       Cheat sheet:
        #           sequence_term_lookup
        #               tuple   : 0-20
        #               self.sequence_term['lookup'][<sequence_term_label>][0]  # //
        #               self.sequence_term['lookup'][<sequence_term_label>][1]  # [PK] Category Label
        #               self.sequence_term['lookup'][<sequence_term_label>][2]  # Main label
        #               self.sequence_term['lookup'][<sequence_term_label>][3]  # Main label string
        #               self.sequence_term['lookup'][<sequence_term_label>][4]  # Sub label
        #               self.sequence_term['lookup'][<sequence_term_label>][5]  # Sub label string
        #               self.sequence_term['lookup'][<sequence_term_label>][6]  # Name Label string
        #               self.sequence_term['lookup'][<sequence_term_label>][7]  # Sequence Term
        #               self.sequence_term['lookup'][<sequence_term_label>][8]  # Sequence Grouping Label
        #               self.sequence_term['lookup'][<sequence_term_label>][9]  # Series
        #               self.sequence_term['lookup'][<sequence_term_label>][10] # Full Sequence Term Label
        #               self.sequence_term['lookup'][<sequence_term_label>][11] # Is flavor
        #               self.sequence_term['lookup'][<sequence_term_label>][12] # Is variant
        #               self.sequence_term['lookup'][<sequence_term_label>][13] # <blank>
        #               self.sequence_term['lookup'][<sequence_term_label>][14] # Main object
        #               self.sequence_term['lookup'][<sequence_term_label>][15] # Supporting objects
        #               self.sequence_term['lookup'][<sequence_term_label>][16] # Intention actor
        #               self.sequence_term['lookup'][<sequence_term_label>][17] # Intention target state
        #               self.sequence_term['lookup'][<sequence_term_label>][18] # Intention full string
        #               self.sequence_term['lookup'][<sequence_term_label>][19] # Intention type
        #               self.sequence_term['lookup'][<sequence_term_label>][20] # <blank>
        #               self.sequence_term['lookup'][<sequence_term_label>][21] # Notes
        #
        #           category_grouping_lookup
        #               list    : 0-1
        #               [0]     : category_label:str
        #               [1]     : sequence_term_label_list:list     : list of labels, can be used to lookup actual seuqence
        #                                                             term from <sequence_term_lookup>
        #           sequence_grouping_lookup
        #               list    : 0-1
        #               [0]     : sequence_label:str
        #               [1]     : sequence_term_label_list:list     : list of labels, can be used to lookup actual seuqence
        #                                                             term from <sequence_term_lookup>
    
        # p_arg stuff
        self._INPUT_DIR = "./domainproblem/"
        #self._INPUT_DIR = "/home/sarrozadj/ISLA_online/domainproblem/"
        self._INPUT_DOMAIN_FULL_LABEL = domain_full_label
        #self._INPUT_SERIES = input_series
        
        
        # Self loggin stuff
        now = datetime.datetime.now()
        now_str = now.strftime("%Y%m%d_%H%M%S")
    
        _LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "Results 001/" + str(neutral_obj_count) + "/LOG_ncsparser_" + now_str + ".txt"
        
        self.sequence_term = {}
        self.sequence_term['lookup'] = {}
        self.sequence_term['category_grouping_lookup'] = {}
        self.sequence_term['sequence_grouping_lookup'] = {}

        self.chapter_pattern = {}
        self.chapter_pattern['lookup'] = {}
        self.chapter_pattern['category_grouping_lookup'] = {}
        self.chapter_pattern['sequence_grouping_lookup'] = {}
        
        self.chapter_pattern['chapter_pattern_category_label'] = None
        self.chapter_pattern['sequence_grouping_label'] = None
        
        self.predicate_def = {}
        self.predicate_def['lookup'] = {}
        self.predicate_def['category_grouping_lookup'] = {}
        self.predicate_def['name_grouping_lookup'] = {}
        
        self.name_lookup = {}
        
        self.intention_templates = {}
        self.intention_templates['lookup'] = {}
        self.intention_templates['sequence_grouping_lookup'] = {}
        
        self.default_intention_strings = []
        self.obj_type_count = {}
        
        # Chapter sequence instance list ordered
        self.chapter_sequence = []

        # Domain-Problem: 
        # -- Problem strings
        self.problem_objects_str_string = []    # These will probably be common elements on all chapters (like the Domain)
        self.problem_state_str = []
        self.problem_problem_string = []
        
        self.problem_objects_str_per_chapter = []
        self.all_problem_objects_str = []
        self.all_problem_objects_list = []
        self.all_problem_objvar_list = []
        self.all_problem_objvar_str = []
        self.problem_objvar_dict = {}
        self.hr_problem_objvar_dict = {}

    # --- DEBUGGING ---
    def consoleDisplay(self, mode=""):
        
        if (mode == "") or (mode == "all"):
            
            print("sequence_term['lookup']:")
            for key,value in self.sequence_term['lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
            print("sequence_term['category_grouping_lookup']:")
            for key,value in self.sequence_term['category_grouping_lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
            print("sequence_term['sequence_grouping_lookup']:")
            for key,value in self.sequence_term['sequence_grouping_lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
            print("chapter_pattern['lookup']:")
            for key,value in self.chapter_pattern['lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
            print("chapter_pattern['category_grouping_lookup']:")
            for key,value in self.chapter_pattern['category_grouping_lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
            print("chapter_pattern['sequence_grouping_lookup']:")
            for key,value in self.chapter_pattern['sequence_grouping_lookup'].items():
                print("    " + str(key) + " : " + str(value))
            print("----")
            
        elif (mode == "chaptersequenceinstance"):
            print("self.chapter_sequence:")
            for value in self.chapter_sequence:
                print("    " + str(value))
            print("----")
    
    # --- Input from file ---
        
    def readSequenceTermsFromFile(self, input_filename:str, mode=""):

        #       Cheat sheet:
        #           sequence_term_lookup
        #               tuple   : 0-30
        #               split_input_line[0]   # //
        #               split_input_line[1]   # Category Label
        #               split_input_line[2]   # Main label
        #               split_input_line[3]   # Main label string
        #               split_input_line[4]   # Sub label
        #               split_input_line[5]   # Sub label string
        #               split_input_line[6]   # Name Label string
        #               split_input_line[7]   # Term Sequence
        #               split_input_line[8]   # Term Sequence Grouping Label
        #               split_input_line[9]   # Series
        #               split_input_line[10]  # Term Full Label
        #               split_input_line[11]  # Is flavor
        #               split_input_line[12]  # Is variant
        #               split_input_line[13]  # <blank>
        #               split_input_line[14]  # Main object
        #               split_input_line[15]  # Supporting objects
        #               split_input_line[16]  # Intention actor
        #               split_input_line[17]  # Intention target state predicate
        #               split_input_line[18]  # Intention full string
        #               split_input_line[19]  # Intention type
        #               split_input_line[20]  # Predecessor Terms
        #               split_input_line[21]  # Direct Chained With (Grouping Label)* multiple terms is treated as an OR
        #               split_input_line[22]  # Successors (Grouping Label)* multiple terms is treated as an OR
        #               split_input_line[23]  # Prerequisite present predicates (aside from negative of Intention target state predicate)
        #               split_input_line[24]  # Prerequisite target state predicates
        #               split_input_line[25]  # Required Objects Present
        #               split_input_line[26]  # Chapter Pattern
        #               split_input_line[27]  # <blank>
        #               split_input_line[28]  # <blank>
        #               split_input_line[29]  # <blank>
        #               split_input_line[30]  # Notes

        #
        #           category_grouping_lookup
        #               list    : 0-1
        #               [0]     : category_label:str
        #               [1]     : sequence_term_label_list:list     : list of labels, can be used to lookup actual seuqence
        #                                                             term from <sequence_term_lookup>
        #           sequence_grouping_lookup
        #               list    : 0-1
        #               [0]     : sequence_label:str
        #               [1]     : sequence_term_label_list:list     : list of labels, can be used to lookup actual seuqence
        #                                                             term from <sequence_term_lookup>
    
        #-----------------------
        # --- 0. Begin logging
        logstr = "[...] Start readSequenceTermsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)

        # --- 1. Reset current data structures
        self.sequence_term['lookup'] = {}
        self.sequence_term['category_grouping_lookup'] = {}
        self.sequence_term['sequence_grouping_lookup'] = {}
        
        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #print(split_input_line)
                #input()
                
                if (not (split_input_line[2] == "")):
                    # --- 2.1 Definitions: 
                    
                    #split_input_line[0]   # //
                    category_label = split_input_line[1].lower()   # Category Label
                    #main_label = split_input_line[2]   # Main label
                    #split_input_line[3]   # Main label string
                    #split_input_line[4]   # Sub label
                    #split_input_line[5]   # Sub label string
                    #split_input_line[6]   # Name Label string
                    #split_input_line[7]   # Term Sequence
                    sequence_grouping_label = split_input_line[8].lower()   # Term Sequence Grouping Label
                    #split_input_line[9]   # Series
                    sequence_term_full_label_string = split_input_line[10].lower()  # Term Full Label
                    #split_input_line[11]  # Is flavor
                    #split_input_line[12]  # Is variant
                    #split_input_line[13]  # <blank>
                    #split_input_line[14]  # Main object
                    #split_input_line[15]  # Supporting objects
                    #split_input_line[16]  # Intention actor
                    #split_input_line[17]  # Intention target state predicate
                    #split_input_line[18]  # Intention full string
                    #split_input_line[19]  # Intention type
                    #split_input_line[20]  # Predecessor Terms
                    #split_input_line[21]  # Direct Chained With (Grouping Label)* multiple terms is treated as an OR
                    #split_input_line[22]  # Successors (Grouping Label)* multiple terms is treated as an OR
                    #split_input_line[23]  # Prerequisite present predicates (aside from negative of Intention target state predicate)
                    #split_input_line[24]  # Prerequisite target state predicates
                    #split_input_line[25]  # Required Objects Present
                    #split_input_line[26]  # Chapter Pattern
                    #split_input_line[27]  # <blank>
                    #split_input_line[28]  # <blank>
                    #split_input_line[29]  # <blank>
                    #split_input_line[30]  # Notes
                    
                    try:
                        sequence_term_lookup_tuple = (
                            split_input_line[0]     ,
                            split_input_line[1]     ,           
                            split_input_line[2]     ,           
                            split_input_line[3]     ,           
                            split_input_line[4]     ,           
                            split_input_line[5]     ,           
                            split_input_line[6]     ,           
                            split_input_line[7]     ,
                            split_input_line[8]     ,
                            split_input_line[9]     ,
                            split_input_line[10]    ,
                            split_input_line[11]    ,
                            split_input_line[12]    ,
                            split_input_line[13]    ,
                            split_input_line[14]    ,
                            split_input_line[15]    ,
                            split_input_line[16]    ,
                            split_input_line[17]    ,
                            split_input_line[18]    ,
                            split_input_line[19]    ,
                            split_input_line[20]    ,
                            split_input_line[21]    ,
                            split_input_line[22]    ,
                            split_input_line[23]    ,
                            split_input_line[24]    ,
                            split_input_line[25]    ,
                            split_input_line[26]    ,
                            split_input_line[27]    ,
                            split_input_line[28]    ,
                            split_input_line[29]    ,
                            split_input_line[30]    
                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                    # --- DEBUGGING
                    #print(sequence_term_full_label_string)
                        
                    # --- 2.2 Add to sequence_term['lookup']:
                    if sequence_term_full_label_string in self.sequence_term['lookup']:
                        logstr = "[..!] Warning : [sequence_term['lookup']] duplicate sequence term label : <" + sequence_term_full_label_string + ">; Overwriting."
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)

                    self.sequence_term['lookup'][sequence_term_full_label_string] = copy.deepcopy(sequence_term_lookup_tuple)
                    
                    # --- 2.3 Add to sequence_term['category_grouping_lookup']
                    if category_label in self.sequence_term['category_grouping_lookup']:
                        if sequence_term_full_label_string in self.sequence_term['category_grouping_lookup'][category_label][1]:
                            logstr = "[..!] Warning : [sequence_term['category_grouping_lookup']] duplicate sequence term label : <" + sequence_term_full_label_string + ">; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.sequence_term['category_grouping_lookup'][category_label][1].append(copy.deepcopy(sequence_term_full_label_string))
                    else:
                        self.sequence_term['category_grouping_lookup'][category_label] = [category_label,[copy.deepcopy(sequence_term_full_label_string)]]
                    
                    # --- 2.4 Add to sequence_term['sequence_grouping_lookup']
                    if sequence_grouping_label in self.sequence_term['sequence_grouping_lookup']:
                        if sequence_term_full_label_string in self.sequence_term['sequence_grouping_lookup'][sequence_grouping_label][1]:
                            logstr = "[..!] Warning : [sequence_term['sequence_grouping_lookup']] duplicate sequence term label : <" + sequence_term_full_label_string + ">; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.sequence_term['sequence_grouping_lookup'][sequence_grouping_label][1].append(copy.deepcopy(sequence_term_full_label_string))
                    else:
                        self.sequence_term['sequence_grouping_lookup'][sequence_grouping_label] = [sequence_grouping_label, [copy.deepcopy(sequence_term_full_label_string)]]

                    
            # >> end: if not comment
        # --- 3. End file read loop
        input_file.close()
        
        # --- Last. End logging
        logstr = "[...] End readSequenceTermsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
    def readChapterPatternsFromFile(self, input_filename:str, mode=""):
        #       Cheat sheet:
        #           chapter_pattern_lookup
        #               tuple   : 0-24
        #               split_input_line[0]       # //
        #               split_input_line[1]       # [PK] Category Label
        #               split_input_line[2]       # Main label
        #               split_input_line[3]       # Main label string
        #               split_input_line[4]       # Sub label
        #               split_input_line[5]       # Sub label string
        #               split_input_line[6]       # Name Label string
        #               split_input_line[7]       # <blank>
        #               split_input_line[8]       # <blank>
        #               split_input_line[9]       # Pattern Sequence
        #               split_input_line[10]      # Sequence Grouping Label
        #               split_input_line[11]      # Series
        #               split_input_line[12]      # Pattern Full Label
        #               split_input_line[13]      # [FK] Sequence Term: Category Label
        #               split_input_line[14]      # Sequence Terms
        #               split_input_line[15]      # Sequence Term Minimum Density (0-1)
        #               split_input_line[16]      # Sequence Term Maximum Density (0-1)
        #               split_input_line[17]      # Sequence Term Minimum Terms
        #               split_input_line[18]      # Sequence Term Maximum Terms
        #               split_input_line[19]      # Duplicates Allowed
        #               split_input_line[20]      # <blank>
        #               split_input_line[21]      # <blank>
        #               split_input_line[22]      # <blank>
        #               split_input_line[23]      # <blank>
        #               split_input_line[24]      # <blank>
        
        #-----------------------0
        # --- 0. Begin logging
        logstr = "[...] Start readChapterPatternsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # --- 1. Reset current data structures
        self.chapter_pattern['lookup'] = {}
        self.chapter_pattern['category_grouping_lookup'] = {}
        self.chapter_pattern['sequence_grouping_lookup'] = {}
        
        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #input()
                
                if (not (split_input_line[2] == "")):
                    # --- 2.1 Definitions:
                    # split_input_line[0]       # //
                    chapter_pattern_category_label = split_input_line[1].lower()       # Category Label
                    # split_input_line[2]       # Main label
                    # split_input_line[3]       # Main label string
                    # split_input_line[4]       # Sub label
                    # split_input_line[5]       # Sub label string
                    # split_input_line[6]       # Name Label string
                    # split_input_line[7]       # <blank>
                    # split_input_line[8]       # <blank>
                    # split_input_line[9]       # Pattern Sequence
                    chapter_pattern_sequence_grouping_label = copy.copy(split_input_line[10].lower())      # Sequence Grouping Label
                    # split_input_line[11]      # Series
                    chapter_pattern_full_label_string = copy.copy(split_input_line[12].lower())      # Pattern Full Label
                    # split_input_line[13]      # Category Label
                    # split_input_line[14]      # Required Sequence Terms
                    # split_input_line[15]      # Sequence Term Minimum Density (0-1)
                    # split_input_line[16]      # Sequence Term Maximum Density (0-1)
                    # split_input_line[17]      # Sequence Term Minimum Terms
                    # split_input_line[18]      # Sequence Term Maximum Terms
                    # split_input_line[19]      # Duplicates Allowed
                    # split_input_line[20]      # <blank>
                    # split_input_line[21]      # <blank>
                    # split_input_line[22]      # <blank>
                    # split_input_line[23]      # <blank>
                    # split_input_line[24]      # <blank>
                    
                    
                    #print(chapter_pattern_sequence_grouping_label)
                    #print(chapter_pattern_full_label_string)
                    #print("===")
                    #print(split_input_line)
                    #input()
                    
                    try:
                        chapter_pattern_lookup_tuple = (
                            split_input_line[0]       , # //
                            split_input_line[1]       , # Category Label
                            split_input_line[2]       , # Main label
                            split_input_line[3]       , # Main label string
                            split_input_line[4]       , # Sub label
                            split_input_line[5]       , # Sub label string
                            split_input_line[6]       , # Name Label string
                            split_input_line[7]       , # <blank>
                            split_input_line[8]       , # <blank>
                            split_input_line[9]       , # Pattern Sequence
                            split_input_line[10]      , # Sequence Grouping Label
                            split_input_line[11]      , # Series
                            split_input_line[12]      , # Pattern Full Label
                            split_input_line[13]      , # Category Label
                            split_input_line[14]      , # Required Sequence Terms
                            split_input_line[15]      , # Sequence Term Minimum Density (0-1)
                            split_input_line[16]      , # Sequence Term Maximum Density (0-1)
                            split_input_line[17]      , # Sequence Term Minimum Terms
                            split_input_line[18]      , # Sequence Term Maximum Terms
                            split_input_line[19]      , # Duplicates Allowed
                            split_input_line[20]      , # <blank>
                            split_input_line[21]      , # <blank>
                            split_input_line[22]      , # <blank>
                            split_input_line[23]      , # <blank>
                            split_input_line[24]        # <blank>

                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                    # --- DEBUGGING
                    print(chapter_pattern_full_label_string)
                    self.chapter_pattern['chapter_pattern_category_label'] = chapter_pattern_category_label
                        
                    # --- 2.2 Add to chapter_pattern['lookup']:
                    if chapter_pattern_full_label_string in self.chapter_pattern['lookup']:
                        logstr = "[..!] Warning : [chapter_pattern_lookup] duplicate chapter pattern label : " + chapter_pattern_full_label_string + "; Overwriting."
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                    self.chapter_pattern['lookup'][chapter_pattern_full_label_string] = copy.deepcopy(chapter_pattern_lookup_tuple)
                    
                    # --- 2.3 Add to chapter_pattern['category_grouping_lookup']
                    if chapter_pattern_category_label in self.chapter_pattern['category_grouping_lookup']:
                        if chapter_pattern_full_label_string in self.chapter_pattern['category_grouping_lookup'][chapter_pattern_category_label][1]:
                            logstr = "[..!] Warning : [chapter_pattern_category_grouping_lookup] duplicate chapter pattern label : " + chapter_pattern_full_label_string + "; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.chapter_pattern['category_grouping_lookup'][chapter_pattern_category_label][1].append(copy.deepcopy(chapter_pattern_full_label_string))
                    else:
                        self.chapter_pattern['category_grouping_lookup'][chapter_pattern_category_label] = [chapter_pattern_category_label,[copy.deepcopy(chapter_pattern_full_label_string)]]
                    
                    # --- 2.4 Add to chapter_pattern['sequence_grouping_lookup']
                    
                    if chapter_pattern_sequence_grouping_label in self.chapter_pattern['sequence_grouping_lookup']:
                        if chapter_pattern_full_label_string in self.chapter_pattern['sequence_grouping_lookup'][chapter_pattern_sequence_grouping_label][1]:
                            logstr = "[..!] Warning : [chapter_pattern_category_grouping_lookup] duplicate chapter pattern label : " + chapter_pattern_full_label_string + "; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.chapter_pattern['sequence_grouping_lookup'][chapter_pattern_sequence_grouping_label][1].append(copy.deepcopy(chapter_pattern_full_label_string))
                    else:
                        self.chapter_pattern['sequence_grouping_lookup'][chapter_pattern_sequence_grouping_label] = [chapter_pattern_sequence_grouping_label, [copy.deepcopy(chapter_pattern_full_label_string)]]
                    
            # >> end: if not comment
        # --- 3. End file read loop
        input_file.close()

        
        # --- Last. End logging
        logstr = "[...] End readChapterPatternsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
                
    def readPredicateDescriptorsFromFile(self, input_filename:str, mode=""):
        #       Cheat sheet:
        #           chapter_pattern_lookup
        #               tuple   : 0-15
        #                   split_input_line[0]      //
        #                   split_input_line[1]      Grouping Label
        #                   split_input_line[2]      Main label
        #                   split_input_line[3]      Main label string
        #                   split_input_line[4]      Sub label
        #                   split_input_line[5]      Sub label string
        #                   split_input_line[6]      Name Label string
        #                   split_input_line[7]      Term Sequence
        #                   split_input_line[8]      Term Sequence Grouping Label
        #                   split_input_line[9]      Parameter 1 label
        #                   split_input_line[10]     Parameter 1 type
        #                   split_input_line[11]     Likelihood of (+)
        #                   split_input_line[12]     Minimum Unique Instances
        #                   split_input_line[13]     Maximum Unique Instances
        #                   split_input_line[14]     Duplicates Allowed
        #                   split_input_line[15]     Notes
        #-----------------------0
        # --- 0. Begin logging
        logstr = "[...] Start readPredicateDescriptorsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # --- 1. Reset current data structures
        self.predicate_def['lookup'] = {}
        self.predicate_def['category_grouping_lookup'] = {}
        self.predicate_def['name_grouping_lookup'] = {}

        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #input()
                
                if (not (split_input_line[2] == "")):
                    #print("---------------------//")
                    #print(split_input_line[2])
                    #input()
                    # --- 2.1 Definitions:
                    # split_input_line[0]       # //
                    predicate_def_category_label = split_input_line[1].lower()       # Grouping Label
                    # split_input_line[2]       # Main label
                    # split_input_line[3]       # Main label string
                    # split_input_line[4]       # Sub label
                    # split_input_line[5]       # Sub label string
                    predicate_def_sequence_grouping_label = split_input_line[6].lower()       # Name Label string
                    # split_input_line[7]       # Term Sequence
                    predicate_def_full_label_string = split_input_line[8].lower()       # Term Sequence Grouping Label
                    # split_input_line[9]       # Parameter 1 label
                    # split_input_line[10]      # Parameter 1 type
                    # split_input_line[11]      # Likelihood of (+)
                    # split_input_line[12]      # Minimum Unique Instances
                    # split_input_line[13]      # Maximum Unique Instances
                    # split_input_line[14]      # Duplicates Allowed
                    # split_input_line[15]      # Notes
                    
                    try:
                        predicate_def_lookup_tuple = (
                            split_input_line[0]   ,     # //
                            split_input_line[1]   ,     # Grouping Label
                            split_input_line[2]   ,     # Main label
                            split_input_line[3]   ,     # Main label string
                            split_input_line[4]   ,     # Sub label
                            split_input_line[5]   ,     # Sub label string
                            split_input_line[6]   ,     # Name Label string
                            split_input_line[7]   ,     # Term Sequence
                            split_input_line[8]   ,     # Term Sequence Grouping Label
                            split_input_line[9]   ,     # Parameter 1 label
                            split_input_line[10]  ,     # Parameter 1 type
                            split_input_line[11]  ,     # Likelihood of (+)
                            split_input_line[12]  ,     # Minimum Unique Instances
                            split_input_line[13]  ,     # Maximum Unique Instances
                            split_input_line[14]  ,     # Duplicates Allowed
                            split_input_line[15]       # Notes

                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                    
                    # --- 2.2 Add to predicate_def['lookup']:
                    if predicate_def_full_label_string in self.predicate_def['lookup']:
                        logstr = "[..!] Warning : [predicate_def_lookup] duplicate predicate definition label : " + predicate_def_full_label_string + "; Overwriting."
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                    self.predicate_def['lookup'][predicate_def_full_label_string] = copy.deepcopy(predicate_def_lookup_tuple)
                    
                    # --- 2.3 Add to predicate_def['category_grouping_lookup']
                    if predicate_def_category_label in self.predicate_def['category_grouping_lookup']:
                        if predicate_def_full_label_string in self.predicate_def['category_grouping_lookup'][predicate_def_category_label][1]:
                            logstr = "[..!] Warning : [predicate_def_category_grouping_lookup] duplicate predicate definition label : " + predicate_def_full_label_string + "; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.predicate_def['category_grouping_lookup'][predicate_def_category_label][1].append(copy.deepcopy(predicate_def_full_label_string))
                    else:
                        self.predicate_def['category_grouping_lookup'][predicate_def_category_label] = [predicate_def_category_label,[copy.deepcopy(predicate_def_full_label_string)]]
                    
                    # --- 2.4 Add to predicate_def['name_grouping_lookup']
                    
                    
                    print(predicate_def_sequence_grouping_label)
                    if predicate_def_sequence_grouping_label in self.predicate_def['name_grouping_lookup']:
                        if predicate_def_full_label_string in self.predicate_def['name_grouping_lookup'][predicate_def_sequence_grouping_label][1]:
                            logstr = "[..!] Warning : [predicate_def_category_grouping_lookup] duplicate predicate definition label : " + predicate_def_full_label_string + "; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.predicate_def['name_grouping_lookup'][predicate_def_sequence_grouping_label][1].append(copy.deepcopy(predicate_def_full_label_string))
                    else:
                        #print([predicate_def_sequence_grouping_label, [copy.deepcopy(predicate_def_full_label_string)]])
                        #print("ELSE: self.predicate_def['name_grouping_lookup'][predicate_def_sequence_grouping_label] : " + predicate_def_sequence_grouping_label)
                        self.predicate_def['name_grouping_lookup'][predicate_def_sequence_grouping_label] = [predicate_def_sequence_grouping_label, [copy.deepcopy(predicate_def_full_label_string)]]
                                        
                    
        # --- 3. End file read loop
        input_file.close()

        # --- Last. End logging
        logstr = "[...] End readPredicateDescriptorsFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
    
    # > Name lookups are loosely coupled with a domain object hierarchy: creature-item-place
    def readCreatureNameLookupFromFile(self, input_filename:str, mode=""):
        #       Cheat sheet:
        #           person_name_lookup
        #               tuple   : 0-3
        #                   split_input_line[0]      //
        #                   split_input_line[1]      Creature Name
        #                   split_input_line[2]      Subtype
        #                   split_input_line[3]      Gender
        #                   split_input_line[4]      Role bias
        #                   split_input_line[5]      Other information

        #-----------------------0
        # --- 0. Begin logging
        logstr = "[...] Start readCreatureNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # --- 1. Reset current data structures
        #No need for now

        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #input()
                
                if (not (split_input_line[1] == "")):
                    # --- 2.1 Definitions:
                    # split_input_line[0]       # //
                    creature_name_str = split_input_line[1]       # Creature Name
                    subtype = split_input_line[2]                 # Subtype
                    # split_input_line[3]       # 
                    # split_input_line[4]       # 
                    # split_input_line[5]       # 
                    
                    try:
                        creature_name_lookup_tuple = (
                           split_input_line[0]      , #//
                           split_input_line[1]      , #Person Name
                           split_input_line[2]      , #Subtype
                           split_input_line[3]      , #Gender
                           split_input_line[4]      , #Role bias
                           split_input_line[5]        #Other information
                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                    
                    # --- 2.2 Add to name_lookup[type]:
                    
                    try:
                        if creature_name_str in self.name_lookup[subtype]:
                            logstr = "[..!] Warning : [name_lookup["+subtype+"]] duplicate creature name : " + creature_name_str + "; Overwriting."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                    except KeyError:
                        self.name_lookup[subtype] = {}
                        
                    self.name_lookup[subtype][creature_name_str] = copy.deepcopy(creature_name_lookup_tuple)
                    
        # --- 3. End file read loop
        input_file.close()

        # --- Last. End logging
        logstr = "[...] End readCreatureNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
    
    def readItemNameLookupFromFile(self, input_filename:str, mode=""):
        #       Cheat sheet:
        #           person_name_lookup
        #               tuple   : 0-3
        #                   split_input_line[0]      //
        #                   split_input_line[1]      Item Name
        #                   split_input_line[2]      Subtype


        #-----------------------
        # --- 0. Begin logging
        logstr = "[...] Start readItemNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # --- 1. Reset current data structures
        # No need for now
        
        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #input()
                
                if (not (split_input_line[1] == "")):
                    # --- 2.1 Definitions:
                    # split_input_line[0]       # //
                    item_name_str = split_input_line[1]       # Item Name
                    subtype = split_input_line[2]             # Subtype
                    # split_input_line[3]       # 
                    # split_input_line[4]       # 
                    # split_input_line[5]       # 
                    
                    try:
                        item_name_lookup_tuple = (
                           split_input_line[0]      , #//
                           split_input_line[1]      , #Item Name
                           split_input_line[2]        #Subtype
                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                    
                    # --- 2.2 Add to name_lookup[type]:
                    
                    try:
                        if item_name_str in self.name_lookup[subtype]:
                            logstr = "[..!] Warning : [name_lookup["+subtype+"]] duplicate item name : " + item_name_str + "; Overwriting."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                    except KeyError:
                        self.name_lookup[subtype] = {}
                        
                    self.name_lookup[subtype][item_name_str] = copy.deepcopy(item_name_lookup_tuple)
                    
        # --- 3. End file read loop
        input_file.close()

        # --- Last. End logging
        logstr = "[...] End readItemNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
    
    def readObjectNamesLookupFromFile(self, input_filename:str, mode=""):
        #       Cheat sheet:
        #           person_name_lookup
        #               tuple   : 0-3
        #                   split_input_line[0]      //
        #                   split_input_line[1]      Object Name
        #                   split_input_line[2]      Subtype
        #                   split_input_line[3]      Attribute1
        #                   split_input_line[4]      Attribute2
        #                   split_input_line[5]      Attribute3
        #                   split_input_line[6]      Vacant1
        #                   split_input_line[7]      Vacant2

        #-----------------------0
        # --- 0. Begin logging
        logstr = "[...] Start readObjectNamesLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # --- 1. Reset current data structures
        #No need for now

        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                if (not (split_input_line[1] == "")):
                    # --- 2.1 Definitions:
                    # split_input_line[0]       # //
                    object_name_str = split_input_line[1]       # Object Name
                    subtype         = split_input_line[2]       # Subtype
                    attribute1      = split_input_line[3]       # 
                    attribute2      = split_input_line[4]       # 
                    attribute3      = split_input_line[5]       # 
                    
                    try:
                        object_name_lookup_tuple = (
                           split_input_line[0]      , #//
                           split_input_line[1]      , #Object Name
                           split_input_line[2]      , #Subtype
                           split_input_line[3]      , #Attribute 1
                           split_input_line[4]      , #Attribute 2
                           split_input_line[5]        #Attribute 3
                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                    
                    # --- 2.2 Add to name_lookup[type]:
                    
                    try:
                        if object_name_str in self.name_lookup[subtype]:
                            logstr = "[..!] Warning : [name_lookup["+subtype+"]] duplicate creature name : " + object_name_str + "; Overwriting."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                    except KeyError:
                        self.name_lookup[subtype] = {}
                        
                    self.name_lookup[subtype][object_name_str] = copy.deepcopy(object_name_lookup_tuple)
                    
        # --- 3. End file read loop
        input_file.close()

        # --- Last. End logging
        logstr = "[...] End readObjectNamesLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
    
    def readIntentionTemplatesFromFile(self, input_filename:str, mode=""):
    
        #   split_input_line[0]     # //
        #   split_input_line[1]     # Domain
        #   split_input_line[2]     # Main Label
        #   split_input_line[3]     # Secondary Label
        #   split_input_line[4]     # Chapter Pattern
        #   split_input_line[5]     # Grouping
        #   split_input_line[6]     # Grouping_label
        #   split_input_line[7]     # Series
        #   split_input_line[8]     # Series_label
        #   split_input_line[9]     # Intention Predicate Object Predicates
        #   split_input_line[10]    # Intention Actor
        #   split_input_line[11]    # Intention Predicate
        #   split_input_line[12]    # Intention Full String
        #   split_input_line[13]    # Likelihood

        #-----------------------
        # --- 0. Begin logging
        logstr = "[...] Start readItemNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        
        # --- 2. Begin file read loop
        input_file = open(input_filename, "r")
        line_ctr = 0
        for input_line in input_file:
            line_ctr += 1
            # >> start: if not comment
            if(not self.__isComment(input_line)):
            
                split_input_line = input_line.strip().split(',')
                
                #print("'" + str(split_input_line[1]) + "'")
                #print(str(split_input_line[0] == ""))
                #input()
                
                if (not (split_input_line[1] == "")):
                    # --- 2.1 Definitions:
                    #split_input_line[0]     # //
                    #split_input_line[1]     # Domain
                    #split_input_line[2]     # Main Label
                    #split_input_line[3]     # Secondary Label
                    #split_input_line[4]     # Chapter Pattern
                    #split_input_line[5]     # Grouping
                    grouping_label = split_input_line[6]     # Grouping_label
                    #split_input_line[7]     # Series
                    series_label   = split_input_line[8]     # Series_label
                    #split_input_line[9]     # Intention Predicate Object Predicates
                    #split_input_line[10]     # Intention Actor
                    #split_input_line[11]     # Intention Predicate
                    #split_input_line[12]     # Intention Full String
                    #split_input_line[13]     # Likelihood
                    
                    try:
                        intention_template_lookup_tuple = (
                            split_input_line[0]     , # //
                            split_input_line[1]     , # Domain                        
                            split_input_line[2]     , # Main Label                        
                            split_input_line[3]     , # Secondary Label                        
                            split_input_line[4]     , # Chapter Pattern                        
                            split_input_line[5]     , # Grouping                        
                            split_input_line[6]     , # Grouping_label                        
                            split_input_line[7]     , # Series                        
                            split_input_line[8]     , # Series_label                        
                            split_input_line[9]     , # Intention Predicate Object Predicates                        
                            split_input_line[10]    , # Intention Actor                        
                            split_input_line[11]    , # Intention Predicate                        
                            split_input_line[12]    , # Intention Full String                        
                            split_input_line[13]      # Likelihood                        
                        )
                    except IndexError:
                        logstr = "[!!!] ERROR : Malformed input (line "+str(line_ctr)+"): "
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                        logstr = "\t" + str(split_input_line)
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)
                        
                    # --- 2.2 Add to intention_templates['lookup']:
                    if series_label in self.intention_templates['lookup']:
                        logstr = "[..!] Warning : self.intention_templates['lookup'] duplicate sequence term label : " + series_label + "; Overwriting."
                        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                        print(logstr)

                    self.intention_templates['lookup'][series_label] = copy.deepcopy(intention_template_lookup_tuple)
                    
                    # --- 2.3 Add to intention_templates['sequence_grouping_lookup']
                    if grouping_label in self.intention_templates['sequence_grouping_lookup']:
                        if series_label in self.intention_templates['sequence_grouping_lookup'][grouping_label][1]:
                            logstr = "[..!] Warning : intention_templates['sequence_grouping_lookup'] duplicate sequence term label : " + series_label + "; Ignoring."
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                        else:
                            self.intention_templates['sequence_grouping_lookup'][grouping_label][1].append(copy.deepcopy(series_label))
                    else:
                        self.intention_templates['sequence_grouping_lookup'][grouping_label] = [grouping_label, [copy.deepcopy(series_label)]]
                    
                    
                    
                    
        # --- 3. End file read loop
        input_file.close()

        # --- Last. End logging
        logstr = "[...] End readItemNameLookupFromFile('"+input_filename+"','"+mode+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # [DEBUGGING]
        #print("self.intention_templates['sequence_grouping_lookup']")
        #for key,value in self.intention_templates['sequence_grouping_lookup'].items():
        #    print("----:" + str(key))
        #    for someitem in value[1]:
        #        print("\t" + str(someitem))
        #
        #print("self.intention_templates['lookup']")
        #for key,value in self.intention_templates['lookup'].items():
        #    print("["+str(key)+"]")
        #    
        #input()
        #
        #
        pass
    
    def fillNames(self, objtype:str,namelist:list):
    
        for sometype in namelist:
            try:
                self.name_lookup[objtype].update(self.name_lookup[sometype])
            except KeyError:
                self.name_lookup[objtype] = {}
                self.name_lookup[objtype].update(self.name_lookup[sometype])
    
    def getSequenceTerm(self, sequence_term_label:str):
        result_term = None
        try:
            result_term = self.sequence_term['lookup'][sequence_term_label]
        except LookupError:
            logstr = "[!!!] ERROR: [getSequenceTerm("+str(sequence_term_label)+")] Key not found"
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            print(logstr)
            #raise Exception(logstr)
        return copy.deepcopy(result_term)

    def getSequenceTermList(self, grouping_label:str, mode1="sequence", mode2="terms"):
        
        # Cheat sheet
        #   mode1:str
        #       "sequence"
        #       "category"
        #   mode2:str
        #       "terms"
        #       "labels"
        
        if mode1 == "sequence":
            try:
                sequence_term_label_list = self.sequence_term['sequence_grouping_lookup'][grouping_label]
                
            except LookupError:
                logstr = "[..!] Warning: [getSequenceTermList(sequence)] Key not found : " + str(grouping_label)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr)
            
            if mode2 == "labels":
                return copy.deepcopy(sequence_term_label_list[1])
            elif mode2 == "terms":
                
                # list of tuples
                result_list = []
                for somelabel in sequence_term_label_list[1]:
                    result_list.append(self.getSequenceTerm(somelabel))

                return copy.deepcopy(result_list)
            else:
                logstr = "[!!!] ERROR: [getSequenceTermList(sequence)] Invalid mode2 : " + str(mode2)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                return None
            
        elif mode1 == "category":
            try:
                sequence_term_label_list = self.sequence_term['category_grouping_lookup'][grouping_label]
                
            except LookupError:
                logstr = "[..!] Warning: [getSequenceTermList(category)] Key not found : " + str(grouping_label)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr)
                
            if mode2 == "labels":
                return copy.deepcopy(sequence_term_label_list[1])
            elif mode2 == "terms":
                
                # list of tuples
                result_list = []
                for somelabel in sequence_term_label_list[1]:
                    result_list.append(self.getSequenceTerm(somelabel))

                return copy.deepcopy(result_list)
            else:
                logstr = "[!!!] ERROR: [getSequenceTermList(category)] Invalid mode2 : " + str(mode2)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                return None

        else:
            logstr = "[!!!] ERROR: [getSequenceTermList] Invalid mode1 : " + str(mode1)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(logstr)
        
    def getChapterPattern(self, chapter_pattern_label:str):
        result_term = None
        try:
            result_term = self.chapter_pattern['lookup'][chapter_pattern_label]
        except LookupError:
            logstr = "[!!!] ERROR: [getChapterPattern("+str(chapter_pattern_label)+")] Key not found"
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            print(logstr)
            #raise Exception(logstr)
        return copy.deepcopy(result_term)

    def getChapterPatternList(self, grouping_label:str, mode1="sequence", mode2="terms"):
        
        # Cheat sheet
        #   mode1:str
        #       "sequence"
        #       "category"
        #   mode2:str
        #       "terms"
        #       "labels"
        
        if mode1 == "sequence":
            try:
                chapter_pattern_label_list = self.chapter_pattern['sequence_grouping_lookup'][grouping_label]
                
            except LookupError:
                logstr = "[..!] Warning: [getChapterPatternList(sequence)] Key not found : " + str(grouping_label)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr)
            
            if mode2 == "labels":
                return copy.deepcopy(chapter_pattern_label_list[1])
            elif mode2 == "terms":
                
                # list of tuples
                result_list = []
                for somelabel in chapter_pattern_label_list[1]:
                    result_list.append(self.getChapterPattern(somelabel))

                return copy.deepcopy(result_list)
            else:
                logstr = "[!!!] ERROR: [getChapterPatternList(sequence)] Invalid mode2 : " + str(mode2)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                return None
            
        elif mode1 == "category":
            try:
                chapter_pattern_label_list = self.chapter_pattern['category_grouping_lookup'][grouping_label]
                
            except LookupError:
                logstr = "[..!] Warning: [getChapterPatternList(category)] Key not found : " + str(grouping_label)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr)
                
            if mode2 == "labels":
                return copy.deepcopy(chapter_pattern_label_list[1])
            elif mode2 == "terms":
                
                # list of tuples
                result_list = []
                for somelabel in chapter_pattern_label_list[1]:
                    result_list.append(self.getChapterPattern(somelabel))

                return copy.deepcopy(result_list)
            else:
                logstr = "[!!!] ERROR: [getChapterPatternList(category)] Invalid mode2 : " + str(mode2)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                return None

        else:
            logstr = "[!!!] ERROR: [getChapterPatternList] Invalid mode1 : " + str(mode1)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(logstr)
    
    # ---
    
    def filterSequenceTerms(self, mode="category", filter_str=""):
        
        result_dict = {}
        
        
        if mode == "category":
            index = 1
        elif mode == "sequence_grouping_label":
            index = 8
        else:
            logstr = "[!!!] ERROR: Unknown mode:" + str(mode)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(logstr)
        
        for key,value_tuple in self.sequence_term['lookup'].items():
            if value_tuple[index].lower() == filter_str.lower():
                result_dict[key] = copy.deepcopy(value_tuple)
        
        
            
        return result_dict

    def filterSequenceGroupingLookup(self, mode="category", filter_str=""):
        
        result_dict = {}
        filter_str += "_"
        #print(filter_str)
        #print("----")
        if mode == "category":
            
            for key,value_tuple in self.sequence_term['sequence_grouping_lookup'].items():
                
                #print(value_tuple[0].lower()[:len(filter_str)])
                #input()
                
                candidate_category = copy.deepcopy(value_tuple[0].lower()[:len(filter_str)])
                
                
                if candidate_category == filter_str.lower():
                    #print(candidate_category + " == " + filter_str.lower())
                    result_dict[key] = copy.deepcopy(value_tuple)
                else:
                    #print(candidate_category + " != " + filter_str.lower())
                    pass
            
        else:
            logstr = "[!!!] ERROR: Unknow filter_str:" + str(filter_str)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(logstr)
            
        #print(result_dict)
        #input()
        return result_dict
    
    def filterProblemObjects(self, domain:DomainProblem, mode="type", filter_str=""):
        
        result_list = []

        if mode == "type":
            for obj_def in self.all_problem_objects_list:
                if domain.typeIsOfType(obj_def[1].lower(),filter_str.lower()):
                    result_list.append(copy.deepcopy(obj_def))
                #else:
                #    print(obj_def[1].lower() + " is not " + filter_str.lower())
        else:
            logstr = "[!!!] ERROR: filterProblemObjects : Invalid mode : " + str(mode)
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            raise Exception(logstr)
        return result_list
                

    # ----
    
    def generate_type_count(self):
        for someobjvar in self.all_problem_objvar_list:
            try:
                self.obj_type_count[someobjvar[1]] += 1
            except KeyError:
                self.obj_type_count[someobjvar[1]] = 1
        return
    
    def instantiate_objvars(self, domain:DomainProblem, objtype:str):
        
        # 0. Some objtype-related checks
        duplicate_allowed_list = ['place']
        
        # 1. Assign objvar to real objects [places]
        for something in self.all_problem_objvar_list:
            if something[1] == objtype:
                result_list = self.filterProblemObjects(domain, "type", objtype)
                
                random.shuffle(result_list)
                
                found_flag = False
                for r_result in result_list:
                    if (    (r_result not in self.problem_objvar_dict.values()) or
                            (objtype in duplicate_allowed_list)
                    ):
                        found_flag = True
                        self.problem_objvar_dict[something[0]] = r_result
                    
                    
                    #for some_objvar_key,some_objvar_value in self.problem_objvar_dict.items():
                    #    print(str(some_objvar_key) + ":"+str(some_objvar_value))
                    #    input()
                if found_flag == False:
                    logstr = "[!!!] ERROR: Unable to assign: " + str(something)
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    raise Exception(logstr)
                    
                
                
                r_result = random.choice(result_list)
                #if objtype == "place":
                #    print("INSTANTIATE_OBJVARS: " + str(something) + ":" + str(r_result))
        return
        
    def replace_objvars(self, input_str:str):
        output_str = copy.copy(input_str)
        
        #if output_str == "?author":
            
        
        for somevar in self.all_problem_objvar_list:
            old = somevar[0]
            new = self.problem_objvar_dict[somevar[0]][0]
            output_str = output_str.replace(old, new)

        if "?" in output_str:
            print("SOME [?] ERROR: " + output_str)
            
        return output_str

    # ---- 
    
    def setChapterPattern(self, chapter_pattern_str ="", mode1="random"):
        # chapter_pattern_sequence_grouping_label = chapter_pattern_str
        
        if mode1 == "set":
            self.chapter_pattern['sequence_grouping_label'] = chapter_pattern_str
            
        elif mode1 == "like":
            found_flag = False
            
            random_list = copy.copy(list(self.chapter_pattern['sequence_grouping_lookup'].keys()))
            random.shuffle(random_list)
            
            #print("Searching keys..")
            for some_pattern in random_list:
                #print("\t" + str(some_pattern))
                if chapter_pattern_str.lower() in some_pattern:
                    found_flag = True
                    self.chapter_pattern['sequence_grouping_label'] = copy.copy(some_pattern)
                
            if not found_flag:
                raise Exception("setChapterPattern(mode1='like') failure: chapter_pattern_str = '"+chapter_pattern_str+"'")

        
        elif mode1 == "random":
            some_pattern = random.sample(list(self.chapter_pattern['sequence_grouping_lookup']),1)
            self.chapter_pattern['sequence_grouping_label'] = copy.copy(some_pattern[0])
        
        
        
        logstr = "[...] setChapterPattern('"+self.chapter_pattern['sequence_grouping_label']+"','"+mode1+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
            
    def buildChapterSequenceInstance(self, mode1="random"):

        # ERASE LATER
        # self.sequence_term = {}
        # self.sequence_term['lookup'] = {}
        # self.sequence_term['category_grouping_lookup'] = {}
        # self.sequence_term['sequence_grouping_lookup'] = {}
        # 
        # self.chapter_pattern = {}
        # self.chapter_pattern['lookup'] = {}
        # self.chapter_pattern['category_grouping_lookup'] = {}
        # self.chapter_pattern['sequence_grouping_lookup'] = {}
        # 
        # self.chapter_pattern['sequence_grouping_label'] = None
        
        logstr = "[...] Start buildChapterSequenceInstance('"+mode1+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
        
        # 0. Data initialization stuff
        if self.chapter_pattern['sequence_grouping_label'] is None:
            logstr = "[...] chapter_pattern['sequence_grouping_label'] is blank; Selecting randomly"
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            print(logstr)
            
            self.setChapterPattern()
        
        self.chapter_sequence = []
        directly_chained_terms = []
        required_successor_terms = []
        
        # ---
        
        # 1. Get chapter pattern sequences
        chapter_pattern_label = self.chapter_pattern['sequence_grouping_label']
        chapter_pattern_sequence = self.chapter_pattern['sequence_grouping_lookup'][chapter_pattern_label]
        # chapter_pattern_sequence[0] : label
        # chapter_pattern_sequence[1] : list
        
        # Chapter pattern sequence loop
        # e.g. Villainy -> Monsters -> Struggle -> Recovery -> Victory
        #print("chapter_pattern_label : " + str(chapter_pattern_label))
        #print("chapter_pattern_sequence : " + str(chapter_pattern_sequence))
        for somesequencelabel in chapter_pattern_sequence[1]:
            #print("??>>" + somesequencelabel)
            
            # somesequencelabel : Chapter Pattern Sequence
            
            category_label = self.chapter_pattern['lookup'][somesequencelabel][13].lower()
            #print("\t\t" + category_label)
            # ref: self.sequence_term['lookup'][<sequence_term_label>][13]      # [FK] Sequence Term: Category Label
            
            sequence_term_ctr = 0
            sequence_term_min = int(self.chapter_pattern['lookup'][somesequencelabel][17])
            sequence_term_max = int(self.chapter_pattern['lookup'][somesequencelabel][18])
            sequence_term_qty = random.randint(sequence_term_min, sequence_term_max)
            sequence_term_try_ctr = 0
            sequence_term_try_max = 16
            
            # ref: self.sequence_term['lookup'][<sequence_term_label>][13]      # [FK] Sequence Term: Category Label
            # ref: self.sequence_term['lookup'][<sequence_term_label>][17]      # Sequence Term Minimum Terms
            # ref: self.sequence_term['lookup'][<sequence_term_label>][18]      # Sequence Term Maximum Terms            
            
            if (self.chapter_pattern['lookup'][somesequencelabel][19].lower() == "false"):
                allow_duplicates = False
            elif (self.chapter_pattern['lookup'][somesequencelabel][19].lower() == "true"):
                allow_duplicates = True
            else:
                logstr = "[...] Unknown allow_duplicates value : ('"+str(self.chapter_pattern['lookup'][somesequencelabel][19])+"'; Defaulting to False)"
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                print(logstr)
                allow_duplicates = False
            # ref: self.sequence_term['lookup'][<sequence_term_label>][19]      # Duplicates Allowed
            
            #print(self.sequence_term['category_grouping_lookup'])
            sequence_term_sequence = self.sequence_term['category_grouping_lookup'][category_label]
            
            

            
            # sequence_term_sequence[0] : label
            # sequence_term_sequence[1] : list
            
            
            sequence_term_sequence_dict = self.filterSequenceGroupingLookup("category", category_label)
            sequence_term_sequence_list = list(sequence_term_sequence_dict)
            
            
            #print(" [...] >>>>>>>>>>>>>")
            #print(category_label)
            #print(somesequencelabel)
            #for something in sequence_term_sequence_list:
            #    print(something)
            
            
            #print(" [...] >>>>>>>>>>>>>")
            
            
            if mode1 == "random":
                
                # 2. Get required sequence term sequences
                #print(len(directly_chained_terms))
                random.shuffle(directly_chained_terms)
                remove_list = []
                
                #print("\t Directly chained terms choices:")
                #for some_successor in directly_chained_terms:
                #    print("\t\t" + str(some_successor))
                
                for some_successor in directly_chained_terms:
                    logstr = " [....] Adding directly-chained term: " + str(some_successor)
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    
                    self.chapter_sequence.append(copy.deepcopy(some_successor.lower()))
                    sequence_term_ctr += 1
                    
                    #remove_list.append(some_successor)
                        
                    directly_chained_terms = []
                    break
                
                #for something in remove_list:
                #    directly_chained_terms.remove(something)
                
                # [start 3.] Get remaining sequence term sequences
                #print(sequence_term_qty)
                #print(sequence_term_max)
                #print(sequence_term_try_max)
                while(( 
                        (sequence_term_ctr < sequence_term_qty) and 
                        (sequence_term_ctr < sequence_term_max) and 
                        (sequence_term_try_ctr < sequence_term_try_max)
                      ) or
                      (len(required_successor_terms) > 0 )
                ):
                    sequence_term_try_ctr += 1
                    
                    # [start 4.] Check if there are required successor terms in this chapter
                    found_flag = False
                    remove_list = []
                    
                    for some_required_successor in required_successor_terms:
                        if some_required_successor in sequence_term_sequence_list:
                            logstr = " [....] Adding required successor: " + str(some_required_successor)
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            print(logstr)
                            
                            sequence_term_sequence_label = copy.copy(some_required_successor)
                            found_flag = True
                            remove_list.append(some_required_successor)
                    #<------break
                            break
                            
                    if found_flag:
                        for something in remove_list:
                            required_successor_terms.remove(something)
                    
                        
                    else:
                    # [else 4.] ...else, pick randomly
                        if(  (sequence_term_ctr <= sequence_term_qty) and 
                             (sequence_term_ctr <= sequence_term_max) and 
                             (sequence_term_try_ctr < sequence_term_try_max)
                        ):
                            sequence_term_sequence_label = random.choice(sequence_term_sequence_list)
                        else:
                #<----------break
                            break
                    
                    # [end 4.]
                    # ---
                    
                    # ---
                    if not allow_duplicates:
                        if sequence_term_sequence_label in self.chapter_sequence:
                            continue
                    # ---
                    #self.sequence_term['lookup'][sequence_term_sequence_label]
                    # #... just in case we need the actual sequence term definition this early
                    #print("[Adding] : " + sequence_term_sequence_label)
                    self.chapter_sequence.append(copy.deepcopy(sequence_term_sequence_label))
                    sequence_term_ctr += 1
                    
                    
                    # [start 5.] Update directly_chained_terms list
                    
                    sequence_grouping_list = self.filterSequenceTerms("sequence_grouping_label",sequence_term_sequence_label)
                    
                    for some_sequence_term_label in sequence_grouping_list:
                        some_sequence_term = self.sequence_term['lookup'][some_sequence_term_label]
                        
                        split_supp_obj = some_sequence_term[21].strip().split(';')
                        
                        for some_label in split_supp_obj:
                            if  not (some_label == "")  and                     \
                                not (some_label in directly_chained_terms):
                                directly_chained_terms.append(some_label)
                    # [end 5.]
                    # ---
                    
                    # [start 6.] Update required_successor_terms list
                    
                    sequence_grouping_list = self.filterSequenceTerms("sequence_grouping_label",sequence_term_sequence_label)
                    
                    for some_sequence_term_label in sequence_grouping_list:
                        some_sequence_term = self.sequence_term['lookup'][some_sequence_term_label]
                        
                        split_supp_obj = some_sequence_term[22].strip().split(';')
                        
                        for some_label in split_supp_obj:
                            if  not (some_label == "")  and                     \
                                not (some_label in required_successor_terms):
                                required_successor_terms.append(some_label.lower())
                                #print("Required: " + str(some_label))
                    # [end 6.]
                    # ---

                    
                    if sequence_term_try_ctr >= sequence_term_try_max:
                        #print("BREAK")
                        break
                    
                # [end 3.]
                if len(self.chapter_sequence) < sequence_term_min:
                    logstr = "[!!!] ERROR: self.chapter_sequence length is below minimum"
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    print(logstr)
                    raise Exception(logstr)
                
            else:
                # sequence_term_sequence[some_explicit_label]
                pass
        
        
        if len(self.chapter_sequence) < sequence_term_min:
            logstr = "[!!!] ERROR: self.chapter_sequence length is below minimum"
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
            print(logstr)
            raise Exception(logstr)

        #print("[....] >>>>>>>>>>>")
        #for something in self.chapter_sequence:
        #    print(something)
        #    #print(self.sequence_term['lookup'][something])
        #input()
        
        logstr = "[...] End buildChapterSequenceInstance('"+mode1+"')"
        util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
        print(logstr)
            
    def buildProblemObjects(self, domain:DomainProblem, neutral_obj_count=0, location_file=""):
        'Pre-build problem objects from chapter pattern information'
        '   > Primary data structure: self.all_problem_objvar_list'
        # ----
        def generate_objects(domain:DomainProblem, objtype:str, neutral_obj_count,explicit_count=0):
        
            #print(self.obj_type_count)
            #neutral_obj_count = 1
            
            if objtype == pddlglobals._OBJECT_TYPE:
                return
                
            if explicit_count == 0:
                try:
                    total_obj = self.obj_type_count[objtype] + neutral_obj_count
                except:
                    self.obj_type_count[objtype] = 0
                    total_obj = neutral_obj_count
            else:
                total_obj = explicit_count
            
            obj_ctr = 0
            #print("NEED: " + str(total_obj))
            while obj_ctr < total_obj:
                
                name_found = False
                tried_types = []
                try_objtype = objtype
                while(not name_found):
                    shuffled_names = list(self.name_lookup[try_objtype].keys())
                    random.shuffle(shuffled_names)
                    
                    r_result = None
                    for some_name in shuffled_names:
                        if not(some_name in self.chosen_names):
                            self.chosen_names.append(some_name)
                            r_result = some_name
                            break
                    #<-----[break]
                        
                    if r_result is None:
                        
                        children_list = domain.getChildren(objtype)
                        print(children_list)
                        
                        try_again = False
                        for some_child in children_list:
                            if some_child not in tried_types:
                                tried_types.append(some_child)
                                try_objtype = some_child
                                try_again = True
                                break
                        if try_again:
                            continue
                        else:
                            break
                        
                    else:
                        name_found = True
                
                if not name_found:
                    logstr = " [!!!] ERROR: Ran out of names for " + str(objtype)
                    util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                    raise Exception(logstr)                        
                    
                    
                    
                #r_result = random.choice(list(self.name_lookup[objtype].keys()))
                
                obj_str = "(" + str(r_result) + " - "+objtype+")"
                obj_term = [str(r_result), copy.deepcopy(objtype)]
                #print(obj_str)
                if not(obj_str in self.all_problem_objects_str):

                    self.all_problem_objects_str.append(copy.deepcopy(obj_str))
                    self.all_problem_objects_list.append([copy.deepcopy(str(r_result)),objtype])
                    domain.objects.append(obj_term)
                
                obj_ctr += 1
                
            self.instantiate_objvars(domain, objtype)
            pass
        
        def generate_intention(domain:DomainProblem, actor_pred:list):
            intentions = []
            
            intention_group_label = random.choice(list(self.intention_templates['sequence_grouping_lookup']))
            intention_group = self.intention_templates['sequence_grouping_lookup'][intention_group_label]
            
            for intention_template_label in intention_group[1]:

                intention_template = self.intention_templates['lookup'][intention_template_label]
                
                #   intention_template[0]     # //
                #   intention_template[1]     # Domain
                #   intention_template[2]     # Main Label
                #   intention_template[3]     # Secondary Label
                #   intention_template[4]     # Chapter Pattern
                #   intention_template[5]     # Grouping
                #   intention_template[6]     # Grouping_label
                #   intention_template[7]     # Series
                #   intention_template[8]     # Series_label
                #   intention_template[9]     # Intention Predicate Object Predicates
                #   intention_template[10]    # Intention Actor
                #   intention_template[11]    # Intention Predicate
                #   intention_template[12]    # Intention Full String
                #   intention_template[13]    # Likelihood
                
                intention_template_raw = intention_template[12]
                
                #print(intention_template_label + "[1]")
                
                # [1] Replace ?actor variable with actor instance
                #print(intention_template_raw)
                intention_str = intention_template_raw.replace('?actor',actor_pred[0])
                #print(intention_str)
                #input()
                
                for objtype_str in intention_template[9].strip().split(';'):
                    
                    objtype_str = objtype_str.strip()
                    
                    objtype_list_temp = objtype_str.replace('(', '').replace(')', '').split(' ')
                    #print(objtype_list_temp)
                    objtype_list = []
                    objtype_list.append(objtype_list_temp[0])
                    objtype_list.append(objtype_list_temp[2])
                    
                    objtype_varname = objtype_list[0]
                    objtype_type = objtype_list[1]
                    
                    if objtype_varname == '?actor':
                        pass
                    else:
                        result_list = self.filterProblemObjects(domain, "type", objtype_type)
                        try:
                            obj_instance = random.choice(result_list)
                        except IndexError:
                            generate_objects(domain, objtype_type, neutral_obj_count,explicit_count=1)
                            result_list = self.filterProblemObjects(domain, "type", objtype_type)
                            try:
                                obj_instance = random.choice(result_list)
                            except IndexError:
                                raise Exception("Creation of intention-specific object has failed: " + str(objtype_list))
                        
                        intention_str = intention_str.replace(objtype_varname,obj_instance[0])
                        #print(intention_str)
                        #input()
                
                intentions.append(intention_str)
            
            return copy.deepcopy(intentions)
        #------------
        
        # 0. Initialization
        problem_objects_str = []
        problem_objects_list = []
        self.problem_objects_str_per_chapter = []
        self.problem_objects_list_per_chapter = []
        self.all_problem_objvar_str = ['(?author - admin)']
        self.all_problem_objvar_list = [['?author','admin']]
        self.chosen_names = []
        actor_list = []
        
        #if mode == "overwrite":
        #    domain.objects = []
        #elif mode == ""
        
        # 1. Loop through self.chapter_sequence
        for sequence_grouping_label in self.chapter_sequence:
            #print(sequence_grouping_label)
            # 2. Get sequence terms from sequence grouping
            sequence_grouping_list = self.filterSequenceTerms("sequence_grouping_label",sequence_grouping_label)
            for some_sequence_term_label in sequence_grouping_list:
                some_sequence_term = self.sequence_term['lookup'][some_sequence_term_label]
                # Main object           some_sequence_term[14]
                # Supporting objects    some_sequence_term[15]
                #print(some_sequence_term[14] + " | " + some_sequence_term[15])
                
                #self.problem_objects_str_string
                
                # ----
                # Main object
                split_main_obj = some_sequence_term[14].strip().split(';')
                
                for some_supp_obj in split_main_obj:
                    some_supp_obj = some_supp_obj.strip()
                    
                    if  (not (some_supp_obj in problem_objects_str)) and (not (some_supp_obj == "")):
                        split_some_supp_obj = some_supp_obj.replace('(', '').replace(')', '').split(' ')
                        if len(split_some_supp_obj) == 3:
                            if (
                                (type(split_some_supp_obj[0]) is str) and
                                (type(split_some_supp_obj[2]) is str) and
                                (split_some_supp_obj[1] == "-")
                               ):
                                
                                problem_objects_str.append(copy.deepcopy(some_supp_obj))
                                problem_objects_list.append([copy.deepcopy(split_some_supp_obj[0]),copy.deepcopy(split_some_supp_obj[2])])
                        else:
                            
                            logstr = "[!!!] ERROR: buildProblemObjects : Invalid object definition: " + some_supp_obj
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            raise Exception(logstr)
                    else:
                        # Already in there!!!
                        pass
                        
                # Supporting objects
                split_supp_obj = some_sequence_term[15].strip().split(';')
                
                for some_supp_obj in split_supp_obj:
                    some_supp_obj = some_supp_obj.strip()
                    
                    if  (not (some_supp_obj in problem_objects_str)) and (not (some_supp_obj == "")):
                        split_some_supp_obj = some_supp_obj.replace('(', '').replace(')', '').split(' ')
                        if len(split_some_supp_obj) == 3:
                            if (
                                (type(split_some_supp_obj[0]) is str) and
                                (type(split_some_supp_obj[2]) is str) and
                                (split_some_supp_obj[1] == "-")
                               ):
                                
                                problem_objects_str.append(copy.deepcopy(some_supp_obj))
                                problem_objects_list.append([copy.deepcopy(split_some_supp_obj[0]),copy.deepcopy(split_some_supp_obj[2])])
                        else:
                            
                            logstr = "[!!!] ERROR: buildProblemObjects : Invalid object definition: " + some_supp_obj
                            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                            raise Exception(logstr)
                    else:
                        # Already in there!!!
                        pass
                # ----
            
            self.problem_objects_str_per_chapter.append(problem_objects_str)
            self.problem_objects_list_per_chapter.append(problem_objects_list)
            
        # Assign to internal lists
        # TODO: todo_ncs_001
        #print(problem_objects_str)
        #print(problem_objects_list)
        #input()
        
        self.all_problem_objvar_str.extend(problem_objects_str)
        self.all_problem_objvar_list.extend(problem_objects_list)
        for somevar in problem_objects_list:
            self.problem_objvar_dict[somevar[0]] = None

        
        # ----
        # Debugging
        #for something in self.all_problem_objvar_str:
        #    print(something)
        #print("+++++")
        #for something in self.all_problem_objvar_list:
        #    print(something)
        #print("+++++")
        #input()
        
        self.generate_type_count()
        
        # ------------------------------------------------------
        # 0. Initialization
        self.problem_state_str = []
        
        # ------------------------------------------------------
        # MANUALLY DEFINED
        
        # 1. Places
        # -- How to match/replace place objects from patterns to 
        #    actual places from in input file?
        
        #location_list = tu.readFromFile(self._INPUT_DIR + self._INPUT_DOMAIN_FULL_LABEL + "-terrain-" + self._INPUT_SERIES + ".txt","predicate-list")
        location_list = tu.readFromFile(location_file,"predicate-list")
        
        for somelocation in location_list:
            # somelocation[0]   "adjacent"
            # somelocation[1]   from_loc
            # somelocation[2]   to_loc
            
            adjacent_keyword = "adjacent"
            from_loc_name = somelocation[0][0]
            from_loc_type = somelocation[0][1]
            to_loc_name = somelocation[1][0]
            to_loc_type = somelocation[1][1]
            
            # 1.1 Location prechecks
            # -- From
            location_pred_str = "(" + from_loc_name + " - "+from_loc_type+")"
            if not(location_pred_str in self.all_problem_objects_str):
                self.all_problem_objects_str.append(copy.deepcopy(location_pred_str))
                self.all_problem_objects_list.append([copy.deepcopy(from_loc_name),copy.deepcopy(from_loc_type)])
                domain.objects.append([copy.deepcopy(from_loc_name),copy.deepcopy(from_loc_type)])
                
            # -- To
            location_pred_str = "(" + to_loc_name + " - "+to_loc_type+")"
            if not(location_pred_str in self.all_problem_objects_str):
                self.all_problem_objects_str.append(copy.deepcopy(location_pred_str))
                self.all_problem_objects_list.append([copy.deepcopy(to_loc_name),copy.deepcopy(to_loc_type)])
                domain.objects.append([copy.deepcopy(to_loc_name),copy.deepcopy(to_loc_type)])
                
            # -- Adjacency
            adjacency_pred_str = "(" + adjacent_keyword + " " + from_loc_name + " " + to_loc_name + ")"
            adjacency_pred_term = [copy.deepcopy(adjacent_keyword),[copy.deepcopy(from_loc_name),copy.deepcopy(from_loc_type)],[copy.deepcopy(to_loc_name),copy.deepcopy(to_loc_type)]]
            if not(adjacency_pred_str in self.problem_state_str):
                self.problem_state_str.append(copy.deepcopy(adjacency_pred_str))
                domain.state_list.append(copy.deepcopy(adjacency_pred_term))
                domain.state.add(str(adjacency_pred_term))
            else:
                print(" [..!] WARNING: Duplicate adjacency predicate :" + adjacency_pred_str)
                
        self.instantiate_objvars(domain, "location")
        
        # [IMPROVEMENT JUNCTION]
        #   Streamline  "extra" object quantities
        # ----
        # 2. Actors / Creatures
        # --
        # 2.0 Admin
        self.problem_objvar_dict['?author'] = ['author','admin']
        domain.objects.append(['author','admin'])
        
        #self.instantiate_objvars(domain, "admin")
        #generate_objects(domain, 'admin', 0)
        
        exclude_list = ['location','actor','admin', 'object','predicate','state']
        
        for some_type in domain.type_list:
            if some_type[0] not in exclude_list:
                logstr = "Generating required objects: " + str(some_type)
                util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=False)
                #print(logstr)
                generate_objects(domain, some_type[0],neutral_obj_count)
        
        #---------------------
        # Default actor intentions
        
        actor_types = copy.deepcopy(domain.actors)
        actor_types.remove('admin')
        
        print(self.problem_objvar_dict)
        print("----")
        for key,value in self.problem_objvar_dict.items():
            print(str(key) + ":" + str(value))
            
            self.hr_problem_objvar_dict[key] = "The '" + key.replace("?","") + "' is " + value[0]
            
            objname = value[0]
            objtype = value[1]
            if objtype in actor_types:
                actor_list.append(copy.copy(value))
        #--------
        
        for someactor in actor_list:
            try:
                intention_strings = generate_intention(domain, someactor)
                self.default_intention_strings.extend(intention_strings)
            except IndexError:
                pass
        pass
    
    def buildProblemState(self, domain:DomainProblem, settings:dict):
        
        def boop(domain:DomainProblem, mode="fullrandom"):
            output_pred_list_list = []
            # -- Ignore:
            #   adjacent
            
            ignore_list = []
            ignore_list.extend(domain._INTENTIONALITY_OPERATORS)
            ignore_list.extend(domain._ADJACENCY_OPERATORS)
            ignore_list.append(domain._EQUAL_OPERATOR)
            ignore_list.append(domain._FORALL_OPERATOR)
            ignore_list.append(domain._IF_OPERATOR)
            ignore_list.append(domain._IFELSE_OPERATOR)
            
            #ignore_list.append("intends")
            #ignore_list.append("adjacent")
            #ignore_list.append("equals")
            #ignore_list.append("forall")
            #ignore_list.append("if")
            #ignore_list.append("ifelse")
            
            
            #print(domain.predicates)
            #print("----")
            for some_predicate_obj in domain.predicates:
                #print(some_predicate_obj)
                #print("fasdfasdfas___")
                #input()
                
                if not(some_predicate_obj.name in ignore_list):
                    
                    temp = copy.deepcopy(some_predicate_obj.name)
                    #print(temp)
                    name_grouping_lookup_label = self._INPUT_DOMAIN_FULL_LABEL + "_" + util.smallify(temp)
                    #name_grouping_lookup_label = self._INPUT_DOMAIN_FULL_LABEL + "_" + temp
                    name_grouping_lookup_label = name_grouping_lookup_label.lower()
                    
                    
        #                   split_input_line[0]      //
        #                   split_input_line[1]      Grouping Label
        #                   split_input_line[2]      Main label
        #                   split_input_line[3]      Main label string
        #                   split_input_line[4]      Sub label
        #                   split_input_line[5]      Sub label string
        #                   split_input_line[6]      Name Label string
        #                   split_input_line[7]      Term Sequence
        #                   split_input_line[8]      Term Sequence Grouping Label
        #                   split_input_line[9]      Parameter 1 label
        #                   split_input_line[10]     Parameter 1 type
        #                   split_input_line[11]     Likelihood of (+)
        #                   split_input_line[12]     Minimum Unique Instances
        #                   split_input_line[13]     Maximum Unique Instances
        #                   split_input_line[14]     Duplicates Allowed
        #                   split_input_line[15]     Notes
        
                    #print("-----?")
                    
                    try:
                        #print(name_grouping_lookup_label)
                        current_predicate_name_grouping = self.predicate_def['name_grouping_lookup'][name_grouping_lookup_label]
                        likelihood     = float(self.predicate_def['lookup'][current_predicate_name_grouping[1][0]][11])
                        predicate_name = self.predicate_def['lookup'][current_predicate_name_grouping[1][0]][3]
                        #if predicate_name != some_predicate_obj.name:
                        #    print(predicate_name + "   " + some_predicate_obj.name)
                        #    raise Exception("MISMAAAAAAAAAAAAAAAAAAAATCH")
                            
                    except KeyError:
                        
                        #if name_grouping_lookup_label ==  "fantasy_fable_05_is_alive":
                        #    print(name_grouping_lookup_label)
                        #    print(likelihood)
                        #    print("KEY ERROR")
                        #    input()
                        print("predicate_def['name_grouping_lookup']["+name_grouping_lookup_label+"] : KEY ERROR !!!")
                        likelihood = -1
                        
                    #print(name_grouping_lookup_label)
                    #print(likelihood)
                    
                    predicate_name = some_predicate_obj.name
                    
                    #for some_object_def in self.all_problem_objvar_list:
                    for some_object_def in self.all_problem_objects_list:
                        #print(">>>>")
                        #print(some_object_def)
                        #----
                        if likelihood >= 1:
                            go_flag = True
                        else:
                            result = random.uniform(0, 1)
                            go_flag = (result <= likelihood)
                        #----
                        if go_flag:
                        
                            first_predparam_def_label = current_predicate_name_grouping[1][0]
                            first_predparam_def = self.predicate_def['lookup'][first_predparam_def_label]
                            
                            if domain.typeIsOfType(some_object_def[1],first_predparam_def[10]):
                                
                                new_predicate_str = ""
                                
                                new_predicate_str += "(" 
                                new_predicate_str += predicate_name
                                
                                # - the first_predparam is the driving element of the predicate
                                # - remaining parameters as examined -- likely random
                                new_predicate_str += " " + some_object_def[0]
                                
                                new_predicate_term = []
                                new_predicate_term.append(copy.deepcopy(predicate_name))
                                new_predicate_term.append(copy.deepcopy(some_object_def))
                                
                                
                                ctr = 0
                                abort_new_predicate = False
                                for some_predparam_def_label in current_predicate_name_grouping[1]:
                                    if ctr == 0:
                                        ctr += 1
                                        continue
                                    ctr += 1
                                    some_predparam_def = self.predicate_def['lookup'][some_predparam_def_label]
                                    
                                    # some_predparam_def[10]    # Parameter Type
                                    #try:
                                    #    result_list = self.filterProblemObjects(domain, "type", some_predparam_def[10])
                                    #except IndexError:
                                    #    print(some_predparam_def_label)
                                    #    print(some_predparam_def)
                                    #    raise IndexError("Cannot choose from an empty sequence")
                                    #print("SECOND PARAMETER")
                                    #print(result_list)
                                    
                                    #print(str(random.choice(result_list)))
                                    #input()
                                    
                                    result_list = self.filterProblemObjects(domain, "type", some_predparam_def[10])
                                    #print(" INDEX ERROR HUNT! : " + str())
                                    
                                    try:
                                        r_result = random.choice(result_list)
                                        new_predicate_str += " " + str(r_result[0])
                                        new_predicate_term.append(copy.deepcopy(r_result))
                                    except IndexError:
                                        abort_new_predicate = True
                                        break
                                        
                                if abort_new_predicate:
                                    #print("abort_new_predicate!")
                                    continue
                    #<--------------continue
                                new_predicate_str += ")" 
                                
                                #print("[y] " + some_object_def[1] + ":" + new_predicate_str)
                                #input()
                                #output_pred_list_list.append(copy.deepcopy(new_predicate_str))
                                output_pred_list_list.append(copy.deepcopy(new_predicate_term))
                                
                            else:
                                #if name_grouping_lookup_label ==  "fantasy_fable_05_is_alive":
                                #    print("[n] " + some_object_def[1])
                                continue
                        #else:
                        #    print("No go: " + str(some_object_def)) 

                            
                    #<----------#
            return output_pred_list_list
        
        # 99. Reference current objects
        # -- bash objects with predicates
        partial_pred_list_list = boop(domain, "fullrandom") 
        
        for state_pred_list in partial_pred_list_list:
        
            domain.state.add(str(state_pred_list))
            domain.state_list.append(state_pred_list)
            
            
        for intention_string in self.default_intention_strings:
            
            intention_pred_list = domain.scanTokens(None,intention_string)
            domain.defineInstances(intention_pred_list)
            
            domain.state.add(str(intention_pred_list))
            domain.state_list.append(intention_pred_list)
            
            
        print(domain.state)
        #input()
            
        # ------------------------------------------------------
        # AUTOMATED INITIAL STATE GENERATION ASSISTANCE
        '''
        # 0. Initialization
        problem_initstate_predicates = []
        predicate_dict = {}
        
        # 1. Loop through self.chapter_sequence
        group_ctr = 0
        for sequence_grouping_label in self.chapter_sequence:
            #print(sequence_grouping_label)
            group_ctr += 1
            # 2. Get sequence terms from sequence grouping
            sequence_grouping_list = self.filterSequenceTerms("sequence_grouping_label",sequence_grouping_label)
            for some_sequence_term_label in sequence_grouping_list:
                some_sequence_term = self.sequence_term['lookup'][some_sequence_term_label]
                
                # parse str (some_sequence_term[17]) into a predicate list
                # ref: self.sequence_term['lookup'][<sequence_term_label>][17] # Intention target state
                
                # For now, does not deal with  complex intentions (especially OR)
                
                # store (predicate_term, group_ctr) || predicate_dict[group_ctr].append(predicate_term)
                
                #if hasConflict(predicate_term, group_ctr, predicate_dict)
                
        '''
        pass

    #def buildProblemGoal(self, domain:DomainProblem, sequence_grouping_label:str, settings:dict):
    def buildProblemGoal(self, domain:DomainProblem, chapter_sequence, current_layer, settings:dict, retro_update_target_statepreds=False):
        # Settings dict:
        #   
        #   "mode"          :   str     "overwrite", "append", "director"
        
        # USEFUL HERE:
        # if hasConflict(predicate_term, group_ctr, predicate_dict)
        
        if settings['mode'] == "overwrite":
            domain.all_intentions = []
            domain.goals = []
            domain.positive_goals = []
            domain.negative_goals = []
         
        # [...] OLD APPROACH: All goals are rolled-up by an AND statement
        #total_goal = [domain._AND_OPERATOR]
        
        # [...] NEW APPROACH: Each goal predicate is separate
        total_goal = []
        
        sequence_grouping_label = chapter_sequence[current_layer]
        rev_chapter_sequence = copy.copy(chapter_sequence)
        rev_chapter_sequence.reverse()
        
        # 1. Append later-part required predicates
        
        if retro_update_target_statepreds:
        
            top_ctr = len(rev_chapter_sequence)
            for top_rev_sequence_grouping_label in rev_chapter_sequence:
                
                # top will update the bottom sequence terms
                top_ctr -= 1
                #print(">>" + str(top_ctr))
                
                for top_sequence_term_label in self.sequence_term['sequence_grouping_lookup'][top_rev_sequence_grouping_label][1]:
                    
                    top_sequence_term = self.sequence_term['lookup'][top_sequence_term_label]
                    
                    term_list = top_sequence_term[24].strip().split(';')
                    #print(">> term_list: " + str(term_list))
                    
                    for some_term in term_list:
                        if some_term == "":
                            continue
                        else:
                            goal_pred_str = self.replace_objvars(some_term)
                            goal_pred_list = domain.scanTokens(None,goal_pred_str)
                            
                            #if goal_pred_list not in total_goal:
                            
                            for bot_ctr in reversed(range(top_ctr-1)):
                                bot_rev_sequence_grouping_label = rev_chapter_sequence[bot_ctr]
                                for bot_sequence_term_label in self.sequence_term['sequence_grouping_lookup'][bot_rev_sequence_grouping_label][1]:
                                    bot_sequence_term = self.sequence_term['lookup'][bot_sequence_term_label]
                                    
                                    bot_sequence_term_list = list(bot_sequence_term)
                                    
                                    if some_term not in bot_sequence_term[24]:
                                        if bot_sequence_term[24] != "":
                                            bot_sequence_term_list[24] = bot_sequence_term[24] + ";" + some_term
                                        else:
                                            bot_sequence_term_list[24] = some_term
                                    bot_sequence_term = tuple(bot_sequence_term_list)
                                    
                                    #print(">>>>" + str(bot_ctr) + " | " + str(bot_sequence_term[24]))
                                    
            #input()
        
        else:
            top_ctr = len(rev_chapter_sequence)
            for top_rev_sequence_grouping_label in rev_chapter_sequence:
                
                # top will update the bottom sequence terms
                top_ctr -= 1
                #print(">>" + str(top_ctr))
                
                for top_sequence_term_label in self.sequence_term['sequence_grouping_lookup'][top_rev_sequence_grouping_label][1]:
                    top_sequence_term = self.sequence_term['lookup'][top_sequence_term_label]
                    term_list = top_sequence_term[24].strip().split(';')
                    #print(">> term_list: " + str(term_list))
            #input()
            
        # 2. Base Problem-Goal creation
        
        for sequence_term_label in self.sequence_term['sequence_grouping_lookup'][sequence_grouping_label][1]:
            # Sequence Term Definition
            sequence_term = self.sequence_term['lookup'][sequence_term_label]
            
            # -- Intention Predicates
            #print("Mysterious error: " + str(sequence_term))
            intention_pred_str = self.replace_objvars(sequence_term[18])
            #print(intention_pred_str)
            #print("----")
            intention_pred_list = domain.scanTokens(filename=None,input_str=intention_pred_str)
            domain.defineInstances(intention_pred_list)
            intention_pred_str = str(intention_pred_list)
            
            new_pred = intention_pred_list
            
            if len(new_pred) == 1:
                new_pred = new_pred[0]
                #print("----AHA!----")
                
                
            #print("buildProblemGoal: ADDING: " + str(new_pred))
            domain.state.add(str(new_pred))
            domain.state_list.append(new_pred)
            
            
            #print(intention_pred_str)
            #print(intention_pred_list)
            #input()
            
            # -- Goal Predicates from Intentions
            goal_pred_str = self.replace_objvars(sequence_term[17])
            goal_pred_list = domain.scanTokens(None,goal_pred_str)
            
            total_goal.append(copy.deepcopy(goal_pred_list))
            #print("first:")
            #print(goal_pred_list)
            #print(total_goal)
            #print("---")
            # -- Goal Predicates from Prerequisite target state predicates 
            
            term_list = sequence_term[24].strip().split(';')
            #print("term_list" + str(term_list))
            
            for some_term in term_list:
                if some_term == "":
                    continue
                else:
                    goal_pred_str = self.replace_objvars(some_term)
                    goal_pred_list = domain.scanTokens(None,goal_pred_str)
                    
                    if goal_pred_list not in total_goal:
                        #print(" [TEST Prerequisite target state] " + str(goal_pred_list))
                        total_goal.append(copy.deepcopy(goal_pred_list))
                        #print("second:")
                        #print(goal_pred_list)
                        #print(total_goal)
                        #print("---")
        #print("???")
        #print(total_goal)
        #print("....")
        #input()
        
        #print("[1]")
        domain.setGoals(total_goal)
        
        domain.generateAllIntentions()
        
        pass
    
    def buildProblemGoal2(self, domain:DomainProblem, sequence_term_label:str, settings:dict):
        # Settings dict:
        #   
        #   "mode"          :   str     "overwrite", "append", "director"
        
        # USEFUL HERE:
        # if hasConflict(predicate_term, group_ctr, predicate_dict)
        
        if settings['mode'] == "overwrite":
            domain.all_intentions = []
            domain.goals = []
            domain.positive_goals = []
            domain.negative_goals = []
            
        total_goal = [domain._AND_OPERATOR]

        # Sequence Term Definition
        sequence_term = self.sequence_term['lookup'][sequence_term_label]
        
        # -- Intention Predicates
        intention_pred_str = self.replace_objvars(sequence_term[18])
        intention_pred_list = domain.scanTokens(None,intention_pred_str)
        
        domain.defineInstances(intention_pred_list)
        #split_intention_pred_list = []
        #domain.splitPropositions(intention_pred_list,split_intention_pred_list,[],[],[])
        
        intention_pred_str = str(intention_pred_list)
        
        new_pred = intention_pred_list
        
        if len(new_pred) == 1:
            new_pred = new_pred[0]
            print("----AHA!----")
        domain.state.add(str(new_pred))
        domain.state_list.append(new_pred)
        
        
        #print(intention_pred_str)
        #print(intention_pred_list)
        #input()
        
        # -- Goal Predicates
        goal_pred_str = self.replace_objvars(sequence_term[17])
        goal_pred_list = domain.scanTokens(None,goal_pred_str)
        
        total_goal.append(copy.deepcopy(goal_pred_list))
        
        #print("dfasdf")
        #print(goal_pred_list)
        #input()
            
        # goal_pred_list
        
        print("[2]")
        domain.setGoals(total_goal)
        #print("???")
        domain.generateAllIntentions()
        
        pass
    
    
        
    
'''
def main(argv, p_arg):
    
    # 0. Initial setup
    #now = datetime.datetime.now()
    #now_str = now.strftime("%Y%m%d_%H%M%S")
    #
    #_LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "LOG_ncsparser_" + now_str + ".txt"
    
    someNCS = NarrativeChapterStructure()
    someNCS.readSequenceTermsFromFile(_INPUT_DIR + "ncs_terms_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _INPUT_SERIES + ".csv")
    someNCS.readChapterPatternsFromFile(_INPUT_DIR + "ncs_patterns_" + _INPUT_DOMAIN_FULL_LABEL + "-" + _INPUT_SERIES + ".csv")
    
    #someNCS.consoleDisplay()
    
    someNCS.setChapterPattern(mode1="random")
    
    someNCS.buildChapterSequenceInstance()
    
    someNCS.consoleDisplay("chaptersequenceinstance")
        
if __name__ == '__main__':
    p_arg = []
    main(sys.argv, p_arg)
'''