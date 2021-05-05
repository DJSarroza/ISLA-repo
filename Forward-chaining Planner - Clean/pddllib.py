import re
import copy
import ast
import random
import pddlglobals

class Action:

    def __init__(self, name, parameters, preconditions, positive_preconditions, negative_preconditions, effects, possible_positive_effects, possible_negative_effects, agents, humanreadables, cost = 0):
        self.name = name
        self.parameters = parameters
        self.preconditions = preconditions
        self.positive_preconditions = positive_preconditions
        self.negative_preconditions = negative_preconditions
        
        # Note: 
        #   - effects is a predicate tree
        #   - negative_effects INCLUDES the 'not' operator
        self.effects = effects
        self.possible_positive_effects = possible_positive_effects
        self.possible_negative_effects = possible_negative_effects
        
        self.agents = agents
        self.humanreadables = humanreadables
        self.cost = cost
        
        self.function_string = None

    def __str__(self):
        return 'action: ' + self.name + \
        '\n  parameters: ' + str(self.parameters) + \
        '\n  preconditions: ' + str(self.preconditions) + \
        '\n     pos:' + str(self.positive_preconditions) + \
        '\n     neg:' + str(self.negative_preconditions) + \
        '\n  effects: ' + str(self.effects) + \
        '\n     pos:' + str(self.possible_positive_effects) + \
        '\n     neg:' + str(self.possible_negative_effects) + \
        '\n  agents: ' + str(self.agents) + \
        '\n  cost: ' + str(self.cost) + '\n'

    def __eq__(self, other): 
        return self.__dict__ == other.__dict__
        
    def getFunctionString(self):
        if self.function_string is None:
            self.function_string = ""
            self.function_string += self.name + "("
            
            comma_flag = False
            for parameter in self.parameters:
                if comma_flag:
                    self.function_string += ", "
                else:
                    comma_flag = True
                #if parameter[0][0] != "
                self.function_string += str(parameter[0])
            self.function_string += ")"
        return self.function_string
        
        
    def isMatch(self, parameter_list:list):
        param_cnt = len(self.parameters)
        if (len(parameter_list) != (param_cnt)):
            return False
        
        for index in range(0,param_cnt):
            if (self.parameters[index][0] != parameter_list[index]):
                return False
        
        return True
    
    def getActionGoalScore(self, total_goals:list):
        'Returns the percentage of total_goals that will be true after applying this action'
        
        max_score = 0
        raw_score = 0
        
        for predicate_term in total_goals:
            max_score += 1
            #print("[DEBUG] " + str(predicate_term))
            if (
                    (str(predicate_term) in str(self.possible_positive_effects)) or 
                    (str(predicate_term) in str(self.possible_negative_effects))
                ):
                #print("[DEBUG] " + str(predicate_term[1]))
                raw_score += 1
                
            #elif (
            #        (str(['not', predicate_term]) in str(self.possible_positive_effects)) or 
            #        (str(['not', predicate_term]) in str(self.possible_negative_effects))
            #    ):
                
        return (raw_score/max_score)
    
class Predicate:

    def __init__(self, 
                    name, 
                    parameters, 
                    definition, 
                    primary_obj,
                    secondary_obj,
                    humanreadables):
                    
        self.name = name
        self.parameters = parameters
        self.definition = definition
        self.primary_obj = primary_obj
        self.secondary_obj = secondary_obj
        self.humanreadables = humanreadables
        
        self.function_string = None
        
    def __str__(self):
        return 'predicate: ' + self.name + \
        '\n  parameters: ' + str(self.parameters) + \
        '\n  definition: ' + str(self.definition) + \
        '\n  primary_obj: ' + str(self.primary_obj) + \
        '\n  secondary_obj: ' + str(self.secondary_obj) + \
        '\n  humanreadables: ' + str(self.humanreadables) + '\n'
        

        
        
    def getFunctionString(self):
        def toFunctionString(name, parameters):
        
            function_string = ""
            function_string += name + "("
            
            comma_flag = False
            for parameter in parameters:
                if comma_flag:
                    function_string += ", "
                else:
                    comma_flag = True
                #if parameter[0][0] != "
                if type(parameter[0]) is list:
                    temp_parameters = copy.deepcopy(parameter[0])
                    temp_name = temp_parameters.pop(0)
                    
                    function_string += toFunctionString(temp_name, temp_parameters)
                else:
                    function_string += str(parameter[0])
            function_string += ")"
            
            return function_string
            
        #============================
        
        if self.function_string is None:
            self.function_string = toFunctionString(self.name, self.parameters)

        return self.function_string
        
    def instantiateTo(self, input_parameter_list, domainproblem=None):
    
        def replaceVariables(input_list:list, parameter_label_list:list, parameter_instance_list:list, domainproblem=None, uppercase=False):

            temp_list = copy.deepcopy(input_list)
            output_list = []
            for temp_element in temp_list:
                if type(temp_element) is list:
                    temp_element = replaceVariables(temp_element, parameter_label_list, parameter_instance_list, domainproblem=domainproblem)
                elif type(temp_element) is str:
                
                    p_flag = False
                    if (temp_element[0] == '"') and \
                       (temp_element[-1] == '"'):
                        p_flag = True
                        temp_element = temp_element.replace('"','')
                    ctr=0
                    #print("[===============]")
                    for some_label in parameter_label_list:
                    
                        if some_label[0] in temp_element:
                        
                            #print("[===========]")
                            #print(some_label)
                            #print(parameter_instance_list[ctr])
                            #print("---")
                            #print(parameter_instance_list)
                            
                            if some_label[1] == pddlglobals._PREDICATE_TYPE:
                                
                                not_flag = False
                                if parameter_instance_list[ctr][0][0] == pddlglobals._NOT_OPERATOR:
                                    tpl = copy.deepcopy(parameter_instance_list[ctr][0][1])
                                    not_flag = True
                                else:
                                    tpl = copy.deepcopy(parameter_instance_list[ctr][0])
                                
                                
                                #print(" [DEBUG] >>]" + str(tpl))
                                temp_pred_def_obj = domainproblem.getPredicateObj(tpl.pop(0))
                                temp_pred_def_obj.instantiateTo(tpl, domainproblem=domainproblem)
                                
                                #print(temp_pred_def_obj)
                                #input()
                                if not_flag:
                                    temp_element = temp_element.replace(some_label[0], "not " + temp_pred_def_obj.getRandomHRString())
                                else:
                                    temp_element = temp_element.replace(some_label[0], temp_pred_def_obj.getRandomHRString())
                                
                            else:
                                temp_element = temp_element.replace(some_label[0], parameter_instance_list[ctr][0])
                                
                        ctr+=1
                        
                    #if p_flag:
                    #    temp_element = '"' + str(temp_element) + '"'
                else:
                    raise Exception("Type error, list or str expected; " + str(type(temp_elem)) + " found.")
                output_list.append(temp_element)
            
            return output_list
        
        
        
        #print("definition")
        self.definition = copy.deepcopy(replaceVariables(self.definition, self.parameters, input_parameter_list,domainproblem))
        #print("primary_obj")
        self.primary_obj = copy.deepcopy(replaceVariables(self.primary_obj, self.parameters, input_parameter_list,domainproblem))
        #print("secondary_obj")
        self.secondary_obj = copy.deepcopy(replaceVariables(self.secondary_obj, self.parameters, input_parameter_list,domainproblem))
        #print("humanreadables")
        self.humanreadables = copy.deepcopy(replaceVariables(self.humanreadables, self.parameters, input_parameter_list,domainproblem,uppercase=True))
        #print("parameters")
        self.parameters = copy.deepcopy(replaceVariables(self.parameters, self.parameters, input_parameter_list,domainproblem))

        
    def getRandomHRString(self, uppercase=False):
        if len(self.humanreadables) > 0:
            return random.choice(self.humanreadables)
        else:
            return self.getFunctionString() + " (no hrstring available)"
        
class DomainProblem:

    # ==========================================
    # Init
    # ==========================================
    
    def __init__(self):
        self._TRUE                  = pddlglobals._TRUE
        self._FALSE                 = pddlglobals._FALSE
        self._PARENT_OPERATOR       = pddlglobals._PARENT_OPERATOR     
        self._TYPE_OPERATOR         = pddlglobals._TYPE_OPERATOR       
                                      
        self._VAR_OPERATOR          = pddlglobals._VAR_OPERATOR        
        self._FORALL_VAR_OPERATOR   = pddlglobals._FORALL_VAR_OPERATOR 
                                      
        self._AND_OPERATOR          = pddlglobals._AND_OPERATOR        
        self._OR_OPERATOR           = pddlglobals._OR_OPERATOR         
        self._NOT_OPERATOR          = pddlglobals._NOT_OPERATOR        
        self._IF_OPERATOR           = pddlglobals._IF_OPERATOR        
        self._IFELSE_OPERATOR       = pddlglobals._IFELSE_OPERATOR        
                                      
        self._FORALL_OPERATOR       = pddlglobals._FORALL_OPERATOR     
        self._WHEN_OPERATOR         = pddlglobals._WHEN_OPERATOR
        self._THEN_OPERATOR         = pddlglobals._THEN_OPERATOR
        
        self._EXEC_ACTION_OPERATOR  = pddlglobals._EXEC_ACTION_OPERATOR
                                      
        self._EQUAL_OPERATOR        = pddlglobals._EQUAL_OPERATOR      
                                      
        self._OBJECT_TYPE           = pddlglobals._OBJECT_TYPE         
        self._PREDICATE_TYPE        = pddlglobals._PREDICATE_TYPE
        self._STATE_TYPE            = pddlglobals._STATE_TYPE
        self._ADMIN_TYPE            = pddlglobals._ADMIN_TYPE          
        
        self._VALID_PROPOSITION_OPERATORS = []
        self._VALID_PROPOSITION_OPERATORS.append(self._AND_OPERATOR)
        self._VALID_PROPOSITION_OPERATORS.append(self._OR_OPERATOR)
        self._VALID_PROPOSITION_OPERATORS.append(self._NOT_OPERATOR)
        self._VALID_PROPOSITION_OPERATORS.append(self._FORALL_OPERATOR)
        self._VALID_PROPOSITION_OPERATORS.append(self._WHEN_OPERATOR)
        self._VALID_PROPOSITION_OPERATORS.append(self._EQUAL_OPERATOR)
        
        self._INTENTIONALITY_OPERATORS = pddlglobals._INTENTIONALITY_OPERATORS
        self._ADJACENCY_OPERATORS = pddlglobals._ADJACENCY_OPERATORS
        
        # -- Domain structures
        self.domain_name = None
        self.type_list = []
        self.actors = []
        self.predicates = []
        self.actions = []
        
        # -- Problem structures
        self.problem_name = None
        self.objects = []
        self.state = set()
        self.state_list = []
        self.all_intentions = []
        self.goals = []
        self.positive_goals = []
        self.negative_goals = []
        

    # ------------------------------------------
    # Tokens
    # ------------------------------------------

    def scanTokens(self, filename=None, input_str=None):
        #print(input_str)
        #print("...")
        if filename is None:
            str = re.sub(r';.*$', '', input_str, flags=re.MULTILINE)
        else:
            with open(filename,'r') as f:
                # Remove single line comments
                str = re.sub(r';.*$', '', f.read(), flags=re.MULTILINE)
            
        # Tokenize
        stack = []
        list = []
        for term in re.findall(r'[()]|[^\s()]+', str):
            if term == '(':
                stack.append(list)
                list = []
            elif term == ')':
                if stack:
                    l = list
                    list = stack.pop()
                    list.append(l)
                else:
                    somestr = "Missing open parentheses:" + str(input_str)
                    raise Exception(somestr)
            else:
                list.append(term)
        if stack:
            somestr = "Missing close parentheses:" + str(input_str)
            raise Exception(somestr)
        if len(list) != 1:
            #print(type(input_str))
            #print(input_str)
            somestr = "Malformed expression: " + str(input_str)
            raise Exception(somestr)
        return list[0]

    #-----------------------------------------------
    # Parse domain
    #-----------------------------------------------

    def parseDomain(self, domain_filename):
        tokens = self.scanTokens(domain_filename, None)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.domain_name = 'unknown'
            self.type_list = []
            self.actors = []
            self.predicates = []
            self.actions = []
            
            while tokens:
                group = tokens.pop(0)
                term = group.pop(0)
                if   term == 'domain':
                    self.domain_name = group[0]
                elif term == ':requirements':
                    pass # TODO
                elif term == ':types':
                    self.parseTypes(group)
                elif term == ':actors':
                    self.parseActors(group)
                elif term == ':predicates':
                    self.parsePredicates(group)
                elif term == ':action':
                    self.parseActions(group)
                else: print(str(term) + ' is not recognized in domain')
        else:
            raise 'File ' + domain_filename + ' does not match domain pattern'

    def saveDomain(self, domain_filename):
        
        # >>>
        def __toRawPredicateString(const_somepredicate:list):
            somepredicate = copy.deepcopy(const_somepredicate)
            output_str = ""
            
            predicate_name = somepredicate.pop(0)
            
            output_str += "(" + predicate_name
            for someterm in somepredicate:
                output_str += " (" + someterm[0] + " - " + someterm[1] + ")"
            output_str += ")"
            
            return output_str
        
        def __toRawActionString(someaction:Action):
            
            def __toRawPredicateTree(depth:int, const_predicate_tree):
                
                output_str = ""
                padding = ""
                for ctr in range(0,depth):
                    padding += "    "
                
                #print(type(const_predicate_tree))
                if type(const_predicate_tree) == list:
                    
                    
                    # >>> Conditional Operators (AND, OR, NOT)
                    if (const_predicate_tree[0] in pddlglobals._CONDITIONAL_OPERATORS):
                        operator = const_predicate_tree[0]
                        operands = const_predicate_tree[1]
                        
                        if operator == pddlglobals._NOT_OPERATOR:
                            term_raw = __toRawPredicateTree(depth+1, operands)
                            output_str += "                    " + padding + "(" + operator + "\n"
                            output_str += copy.copy(term_raw)
                            output_str += "                    " + padding + ")\n"
                        else:
                            output_str += "                    " + padding + "(" + operator + "\n"
                            for someterm in operands:
                                term_raw = __toRawPredicateTree(depth+1, someterm)
                                output_str += copy.copy(term_raw)
                            output_str += "                    " + padding + ")\n"
                    # >>> For-All operator
                    elif (const_predicate_tree[0] == pddlglobals._FORALL_OPERATOR):
                        
                        ctr = 0
                        
                        forall_operator = const_predicate_tree[0]
                        forall_variable = const_predicate_tree[1]
                        when_operator   = const_predicate_tree[2]
                        when_condition  = const_predicate_tree[3]
                        when_effect     = const_predicate_tree[4]
                        
                        output_str += "                    " + padding + "(" + forall_operator + "\n"
                        output_str += "                    " + padding + "    (" + forall_variable[0] + " - " + forall_variable[1] + ")\n"
                        output_str += "                    " + padding + "    (" + when_operator + "\n"
                        
                        when_condition_raw = __toRawPredicateTree(depth+2, when_condition)
                        output_str += when_condition_raw

                        when_effect_raw = __toRawPredicateTree(depth+2, when_effect)
                        output_str += when_effect_raw
                        
                        output_str += "                    " + padding + "    )\n"
                        output_str += "                    " + padding + ")\n"
                    # >>> When Operator
                    elif (const_predicate_tree[0] == pddlglobals._WHEN_OPERATOR):

                        when_operator   = const_predicate_tree[0]
                        when_condition  = const_predicate_tree[1]
                        when_effect     = const_predicate_tree[2]
                        
                        output_str += "                    " + padding + "(" + when_operator + "\n"
                        
                        when_condition_raw = __toRawPredicateTree(depth+1, when_condition)
                        output_str += when_condition_raw

                        when_effect_raw = __toRawPredicateTree(depth+1, when_effect)
                        output_str += when_effect_raw
                        
                        output_str += "                    " + padding + ")\n"
                    elif (const_predicate_tree[0] in self._INTENTIONALITY_OPERATORS):
                        
                        intention_operator = const_predicate_tree[0]
                        intention_actor =  const_predicate_tree[1]
                        intention_predicate =  const_predicate_tree[2]
                        
                        output_str += "                    " + padding + "(" + intention_operator + "\n"
                        output_str += "                        " + padding + intention_actor[0] + "\n"
                        
                        intention_predicate_raw = __toRawPredicateTree(depth+1, intention_predicate)
                        output_str += copy.copy(intention_predicate_raw)
                        
                        output_str += "                    " + padding + ")\n"
                        
                    # >>> Normal predicates    
                    else:
                        term_raw = ""
                        output_str += "                    " + padding + "("                        
                        ctr = 0
                        
                        if (len(const_predicate_tree) == 1):
                            for someterm in const_predicate_tree[0]:
                                if ctr == 0:
                                    output_str += someterm + " "
                                else:
                                    output_str += someterm[0] + " "
                                ctr += 1
                            output_str += ")\n"

                        else:
                            for someterm in const_predicate_tree:
                                if ctr == 0:
                                    output_str += someterm + " "
                                else:
                                    output_str += someterm[0] + " "
                                ctr += 1
                            output_str += ")\n"
                        
                        
                else:
                    raise Exception(" [!!!] ERROR: Expected type: list")
                return output_str
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
            
            output_str = ""
            #(:action personeatrawmeat
            #:parameters     ((?somecreature - person))
            #:precondition   (and
            #                    (hasrawmeat ?somecreature)
            #                )
            #:effect         (and
            #                    (not (hasrawmeat ?somecreature))
            #                    (not (hungry ?somecreature))
            #                    (issick ?somecreature)
            #                )
            #:agents ((?somecreature))
            #)
            
            output_str += "    (:action "+someaction.name+"\n"
            output_str += "    :parameters     ("
            #parameters loop
            ctr = 0
            for someparameter in someaction.parameters:
                if ctr == 0:
                    output_str += "(" + someparameter[0] + " - " + someparameter[1] + ")"
                else:
                    output_str += " (" + someparameter[0] + " - " + someparameter[1] + ")"
                
                ctr += 1
            output_str += ")\n"
            
            
            #preconditions loop
            #for someprecon in someaction.preconditions:
            #    print(someprecon)
            #    input()
                
            precon_str = __toRawPredicateTree(0, someaction.preconditions)
            output_str += "    :precondition\n"
            output_str += precon_str
            output_str += "    \n"
            
            #effect loop
            #print(someaction.effects)
            #input()
            precon_str = __toRawPredicateTree(0, someaction.effects)
            output_str += "    :effect\n"
            output_str += precon_str
            output_str += "    \n"
            #agents loop
            
            output_str += "    :agents       ("
            ctr = 0
            for someagent in someaction.agents:
                if ctr == 0:
                    output_str += "("+someagent[0]+")"
                else:
                    output_str += " ("+someagent[0]+")"
                ctr += 1
            output_str += ")\n"
            
            output_str += "    )\n"
            
            return output_str
        
        # >>>
        
        # WARNING: mode is set to writing a NEW file
        savefile = open(domain_filename, "w")
        
        # [define: start]
        savefile.write("(define (domain "+ self.domain_name +")\n")
        # ----------------------------------
        # [types: start]
        savefile.write("    (:types\n")
        #>>>types loop
        for sometype in self.type_list:
            savefile.write("        " + sometype[0] + "\n")
        # [types: end]
        savefile.write("    )\n")
        # ----------------------------------
        # [actors: start]
        savefile.write("    (:actors\n")
        #>>>actors loop
        for someactor in self.actors:
            savefile.write("        " + someactor + "\n")
        # [actors: end]
        savefile.write("    )\n")
        # ----------------------------------
        # [predicates: start]
        savefile.write("    (:predicates\n")
        #>>>predicates loop
        for somepredicate in self.predicates:
            predicate_raw = __toRawPredicateString(somepredicate)
            savefile.write("        " + predicate_raw + "\n")
        # [predicates: end]
        savefile.write("    )\n")
        # ----------------------------------
        # [actions: start]
        #>>>actions loop
        for someaction in self.actions:
            action_raw = __toRawActionString(someaction)
            savefile.write(action_raw + "\n")
        # [actions: end]
        
        # ----------------------------------
        
        # ----------------------------------
        
        # ----------------------------------
        # [define: end]
        savefile.write(")\n")
        savefile.close()
        
    #-----------------------------------------------
    # Parse types
    #-----------------------------------------------
    def parseTypes(self, group):
        
        # Add the main "object" type
        self.addType({'type_name':"object", 'parent':""})
        self.addType({'type_name':pddlglobals._PREDICATE_TYPE, 'parent':""})
        
        for type_element in group:
            if type(type_element) is str:
                
                self.addType({'type_name':type_element, 'parent':""})
                
            elif len(type_element) == 2:
                
                self.addType({'type_name':type_element[0], 'parent':type_element[1]})
                
                

    #-----------------------------------------------
    # Is valid type checking
    #-----------------------------------------------
        
    def isValidType(self, candidate):
        
        if type(candidate) is not str:
            return False
        for type_element in self.type_list:
            if candidate == type_element[0]:
                #print(" [.....>] Type match found")
                return True
        return False
    
    def getParent(self, object_type):
        
        for type_element in self.type_list:
            if object_type == type_element[0]:
                return type_element[1]
        raise Exception(' [!!!] ERROR: Undefined type "'+str(object_type)+'"')
        
    def getChildren(self, object_type):
        output = []
        for type_element in self.type_list:
            if object_type == type_element[1]:
                output.append(type_element[0])
        return output
        
    def typeIsOfType(self, candidate_type, type_name):
        
        if candidate_type == type_name:
            return True
        elif type_name == self._STATE_TYPE:
            # TODO
            #print(" !!!!!!!!!!!!!!!!!!!!!!! This is a state. need further checking !!!!!!!!!!!!!!!!!!!!!!!")
            #if self.isValidStateInstance
            return True
        elif type_name == self._PREDICATE_TYPE:
        
            return self.isValidPredicate(proposition)
            
        #elif type_name == self._OBJECT_TYPE:
        #    if self.typeIsOfType(candidate_type,"place"):
        #        return False
        #    else:
        #        return True
        else:
            object_inst_parent = self.getParent(candidate_type)
            if object_inst_parent == "":
                
                return False
            elif self.typeIsOfType(object_inst_parent,type_name):
                return True        
            
    #-----------------------------------------------
    # Parse actors
    #-----------------------------------------------
        
    def parseActors(self, group):
        #self.actors = []
        for actor in group:
            self.addActor({'actor':actor})
        #    if self.isValidType(actor_element):
        #        self.actors.append(actor_element)
        #    else:
        #        raise Exception(' [!!!] ERROR: Invalid actor, undefined type "'+str(actor_element)+'"')
    
    #-----------------------------------------------
    # Parse predicates
    #-----------------------------------------------
    def parsePredicates(self, group):
        
        #print(" [...] parsePredicates start >>>")
                
        for predicate in group:
            #print(" [.....?] predicate")
            #print(predicate)
            
            self.addPredicate({'raw_input_list':predicate})
            
    #-----------------------------------------------
    # Get predicate definition from predicate name
    #-----------------------------------------------
        
    def getPredicateDef(self, candidate):
        if type(candidate) is not str:
            #raise Exception('Invalid type, expected str')
            return False
        
        #print(" [...>>] getPredicateDef :: self.predicates") 
        #print(self.predicates)
        #print(" -----------------------------------------------------")
        #if candidate in [self._NOT_OPERATOR, self._AND_OPERATOR, self._OR_OPERATOR]:
        if candidate in self._VALID_PROPOSITION_OPERATORS:
            
            if candidate == self._EQUAL_OPERATOR:
                #print(" [...!!] equal detected")
                #raise Exception("Stop")
                pass
            elif candidate == self._FORALL_OPERATOR:
                #print(" [...!!] forall detected")
                #raise Exception("Stop")
                pass
            else:
                #print(" [...] Operator? " + str(candidate))
                return True
        #print(" [...] What? " + str(candidate))
        for predicate in self.predicates:
            #print(" [...>>>>>>] predicate")
            #print(predicate[0] + " ?= " + candidate)
            #print(" ----------------->>>>>>>")
            if predicate.name == candidate:
                return predicate.definition
        print(" [!!!] ERROR: Invalid predicate: " + candidate)
        return False    
        
        
    def getPredicateObj(self, predicate_name:str):
        if type(predicate_name) is not str:
            print(predicate_name)
            raise Exception('Invalid type, expected str')
            return None
        for predicate in self.predicates:
            if predicate.name == predicate_name:
                return copy.deepcopy(predicate)
            
        return None
        
    #-----------------------------------------------
    # Parse action
    #-----------------------------------------------

    def parseActions(self, group):
        
        #print("=====")
        #print(group)
        self.addAction({'raw_input_list':group})
    
    #-----------------------------------------------
    # Parse agents
    #-----------------------------------------------
        
    def parseAgents(self, group, agents:list, var_list):
        #if type(group) is not list:
        #    raise 
        
        for agent_elem in group:
            found_flag = False
            for var_elem in var_list:
                #print(" [...>>] " + str(agent_elem) + " == " + str(var_elem[0]))
                if agent_elem[0] == var_elem[0]:
                    agents.append(var_elem)
                    found_flag = True
            if not found_flag:
                raise Exception(' [!!!] ERROR: Undefined agent: ' + str(agent_elem))
        
        #raise Exception(" [!!!] ERROR: Stop for now")
    
    def parseHumanReadableStr(self, group, humanreadables:list, var_list):
        
        for some_raw in group:
            processed_str = ""
            
            for some_word in some_raw:
                processed_str += some_word + " "
                
            processed_str = processed_str.strip()
            
            for some_var in var_list:
                if some_var[0] not in processed_str:
                    raise Exception("Human readable string does not represent a variable: " + str(some_var) + " :: " + str(group))
                
                
            humanreadables.append(copy.copy(processed_str))
    
    #-----------------------------------------------
    # Get action definition from action name
    #-----------------------------------------------

    def getAction(self, candidate):
        if type(candidate) is not str:
            raise Exception(' [!!!] ERROR: Invalid type, expected str')
        
        for action in self.actions:
            if action.name == candidate:
                return action
        return False
        
    #-----------------------------------------------
    # Parse problem
    #-----------------------------------------------

    def parseProblem(self, problem_filename):
        tokens = self.scanTokens(problem_filename, None)
        if type(tokens) is list and tokens.pop(0) == 'define':
            self.problem_name = 'unknown'
            self.objects = []
            
            self.state = set()
            self.state_list = []
            self.all_intentions = []
            
            self.goals = []
            self.positive_goals = []
            self.negative_goals = []
            
            
            while tokens:
                group = tokens.pop(0)
                term = group[0]
                if   term == ':problem':
                    self.problem_name = group[-1]
                elif term == ':domain':
                    if self.domain_name != group[-1]:
                        raise Exception('Different domain specified in problem file')
                    #pass
                elif term == ':requirements':
                    pass # TODO
                elif term == ':objects':
                    group.pop(0)
                    self.parseProblemObjects(group)
                elif term == ':init':
                    group.pop(0)
                    self.parseInitialState(group)
                elif term == ':goal':
                    #print("\n\n [...] Goals")
                    #print(group[1])
                    #input()
                    #self.splitPropositions(group[1], self.goals, self.positive_goals, self.negative_goals, [])
                    
                    group.pop(0)
                    print(group)
                    print("----")
                    
                    self.setGoals(group)
                    #for sub_group in group:
                    #    print("sub_group: " + str(sub_group))
                    #    self.setGoals(sub_group)
                    
                else: 
                    print(str(term) + ' is not recognized in problem')
        
        self.generateAllIntentions()
        
    def saveProblem(self,problem_filename):
        # >>>
        def __sp_toRawPredicateTree(depth:int, const_predicate_tree):
            
            output_str = ""
            padding = ""
            for ctr in range(0,depth):
                padding += "    "
            
            #print(type(const_predicate_tree))
            if type(const_predicate_tree) == list:
                # >>> Conditional Operators (AND, OR, NOT)
                if (const_predicate_tree[0] in pddlglobals._CONDITIONAL_OPERATORS):
                    operator = const_predicate_tree[0]
                    operands = const_predicate_tree[1]
                    
                    if operator == pddlglobals._NOT_OPERATOR:
                        #print("SAVE_PROBLEM INNER OPERAND [ __sp_toRawPredicateTree NOT]: " + str(operands))
                        term_raw = __sp_toRawPredicateTree(depth+1, operands)
                        #print(term_raw)
                        output_str += "        " + padding + "(" + operator + "\n"
                        output_str += copy.copy(term_raw)
                        output_str += "        " + padding + ")\n"
                    else:
                        output_str += "        " + padding + "(" + operator + "\n"
                        for someterm in operands:
                            term_raw = __sp_toRawPredicateTree(depth+1, someterm)
                            output_str += copy.copy(term_raw)
                        output_str += "        " + padding + ")\n"
                # >>> For-All operator
                elif (const_predicate_tree[0] == pddlglobals._FORALL_OPERATOR):
                    
                    ctr = 0
                    
                    forall_operator = const_predicate_tree[0]
                    forall_variable = const_predicate_tree[1]
                    when_operator   = const_predicate_tree[2]
                    when_condition  = const_predicate_tree[3]
                    when_effect     = const_predicate_tree[4]
                    
                    output_str += "        " + padding + "(" + forall_operator + "\n"
                    output_str += "        " + padding + "    (" + forall_variable[0] + " - " + forall_variable[1] + ")\n"
                    output_str += "        " + padding + "    (" + when_operator + "\n"
                    
                    when_condition_raw = __sp_toRawPredicateTree(depth+2, when_condition)
                    output_str += when_condition_raw

                    when_effect_raw = __sp_toRawPredicateTree(depth+2, when_effect)
                    output_str += when_effect_raw
                    
                    output_str += "        " + padding + "    )\n"
                    output_str += "        " + padding + ")\n"
                # >>> When Operator
                elif (const_predicate_tree[0] == pddlglobals._WHEN_OPERATOR):

                    when_operator   = const_predicate_tree[0]
                    when_condition  = const_predicate_tree[1]
                    when_effect     = const_predicate_tree[2]
                    
                    output_str += "        " + padding + "(" + when_operator + "\n"
                    
                    when_condition_raw = __sp_toRawPredicateTree(depth+1, when_condition)
                    output_str += when_condition_raw

                    when_effect_raw = __sp_toRawPredicateTree(depth+1, when_effect)
                    output_str += when_effect_raw
                    
                    output_str += "        " + padding + ")\n"
                elif (const_predicate_tree[0] in self._INTENTIONALITY_OPERATORS):
                    
                    intention_operator = const_predicate_tree[0]
                    intention_actor =  const_predicate_tree[1]
                    intention_predicate =  const_predicate_tree[2]
                    
                    output_str += "        " + padding + "(" + intention_operator + "\n"
                    output_str += "            " + padding + intention_actor[0] + "\n"
                    
                    intention_predicate_raw = __sp_toRawPredicateTree(depth+1, intention_predicate)
                    output_str += copy.copy(intention_predicate_raw)
                    
                    output_str += "        " + padding + ")\n"
                    
                # >>> Normal predicates    
                else:
                    term_raw = ""
                    output_str += "        " + padding                       
                    ctr = 0

                    if  (   (len(const_predicate_tree) == 1) or
                            (   (len(const_predicate_tree) == 2) and 
                                (const_predicate_tree[1] == pddlglobals._PREDICATE_TYPE)
                            )
                        ):
                        term_raw = " " + __sp_toRawPredicateTree(depth, const_predicate_tree[0])
                        output_str += copy.copy(term_raw)
                        
                    else:
                        output_str += "("
                        for someterm in const_predicate_tree:
                            if ctr == 0:
                                output_str += someterm + " "
                            else:
                                output_str += someterm[0] + " "
                            ctr += 1
                        output_str += ")\n"
                    
                    
            else:
                raise Exception(" [!!!] ERROR: Expected type: list : " + str(const_predicate_tree))
            return output_str
        # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>                    
        def __sp_toRawPredicateInstanceString(const_somepredicate:list, mode=0):
            def __sp_toRawPredicateString(depth:int, const_predicate_tree):
                
                output_str = ""
                
                #print(type(const_predicate_tree))
                if type(const_predicate_tree) == list:
                    
                    
                    # >>> Conditional Operators (AND, OR, NOT)
                    if (const_predicate_tree[0] in pddlglobals._CONDITIONAL_OPERATORS):
                        operator = const_predicate_tree[0]
                        operands = const_predicate_tree[1]
                        
                        
                        
                        if operator == pddlglobals._NOT_OPERATOR:
                            #print("SAVE_PROBLEM INNER OPERAND [__sp_toRawPredicateString NOT]: " + str(operands))
                            term_raw = __sp_toRawPredicateString(depth+1, operands)
                            #print(term_raw + " POTAAATO")
                            output_str += "(" + operator + " "
                            output_str += copy.copy(term_raw)
                            output_str += ")"
                        else:
                            output_str += "(" + operator + " "
                            for someterm in operands:
                                term_raw = __sp_toRawPredicateString(depth+1, someterm)
                                output_str += copy.copy(term_raw)
                            output_str += ")"
                            
                    elif (const_predicate_tree[0] in self._INTENTIONALITY_OPERATORS):
                        intention_operator = const_predicate_tree[0]
                        intention_actor =  const_predicate_tree[1]
                        intention_predicate =  const_predicate_tree[2]
                        output_str += "(" + intention_operator + " "
                        output_str += intention_actor[0] + ""
                        
                        intention_predicate_raw = __sp_toRawPredicateString(depth+1, intention_predicate)
                        output_str += copy.copy(intention_predicate_raw)
                        
                        output_str += ")"
                        
                    # >>> Normal predicates    
                    else:
                        term_raw = ""
                        
                        ctr = 0
                        
                        if  (   (len(const_predicate_tree) == 1) or
                                (   (len(const_predicate_tree) == 2) and 
                                    (const_predicate_tree[1] == pddlglobals._PREDICATE_TYPE)
                                )
                            ):
                            #print("[DEBUG THING] " + str(const_predicate_tree))
                            
                            term_raw = " " + __sp_toRawPredicateString(depth, const_predicate_tree[0])
                            output_str += copy.copy(term_raw)
                            
                        else:
                            output_str += "("     
                            for someterm in const_predicate_tree:
                                if ctr == 0:
                                    output_str += someterm
                                else:
                                    if type(someterm) is list:
                                        output_str += " " + copy.copy(someterm[0])
                                    else:
                                        output_str += " " + copy.copy(someterm)
                                ctr += 1
                            output_str += ")"
                            
                        #print("[>]" +output_str)
                        
                        
                else:
                    raise Exception(" [!!!] ERROR: Expected type: list : " + str(const_predicate_tree))
                return output_str
            # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>        

            output_str = ""
            
            somepredicate = copy.deepcopy(const_somepredicate)
            
            predicate_name = somepredicate.pop(0)
            
            output_str += "        (" + predicate_name

            
            if predicate_name in self._INTENTIONALITY_OPERATORS:
                intention_actor = somepredicate.pop(0)
                
                output_str += " " + intention_actor[0] + " "
                #print(somepredicate)
                if len(somepredicate) == 1:
                    #print(somepredicate)
                    intention_predicate = __sp_toRawPredicateString(0,somepredicate[0])
                else:
                    raise Exception(" [!!!] ERROR: Unexpected intention predicate list length")
                output_str += intention_predicate
            else:
                for someterm in somepredicate:
                    output_str += " " + copy.copy(someterm[0])
            
            
            output_str += ")\n"
            return output_str
        
        # >>>
        # WARNING: mode is set to writing a NEW file
        savefile = open(problem_filename, "w")
        
        # [define: start]
        if self.problem_name is None:
            savefile.write("(define (:problem "+ problem_filename +")\n")
        else:
            savefile.write("(define (:problem "+ str(self.problem_name) +")\n")
            
        savefile.write("    (:domain " + self.domain_name +")\n")
        
        # [objects: start]
        savefile.write("    (:objects\n")
        for someobject in self.objects:
            #print(someobject)
            savefile.write("        ("+someobject[0]+" - "+someobject[1]+")\n")
        # [objects: end]
        savefile.write("    )\n")
        # ----------------------------------
        # [init: start]
        savefile.write("    (:init\n")
        for somepredicate in list(self.state_list):
            #print(" [DEBUG] " + str(somepredicate))
            predicate_raw = __sp_toRawPredicateInstanceString(somepredicate)
            savefile.write(predicate_raw)
        
        # [init: end]
        savefile.write("    )\n")        
        # ----------------------------------
        # [goal: start]
        savefile.write("    (:goal\n")
        #for somegoal in self.goals:
        #    print(somegoal)
            
            
        goal_raw = ""
        #print("ALL GOALS: " + str(self.goals))
        for some_goal in self.goals:
            #print("Adding: " + str(some_goal))
            goal_raw = goal_raw + __sp_toRawPredicateTree(0,some_goal)
        
        
        savefile.write(goal_raw)
        # [goal: end]
        savefile.write("    )\n")        
        # ----------------------------------
        # [define: end]
        savefile.write(")\n")
        savefile.close()
        
        #print(" [...] DEBUG: Saved file: " + problem_filename)
        #input()
    #-----------------------------------------------
    # Parse problem objects
    #-----------------------------------------------
    
    def parseProblemObjects(self, group):
        #print(" [...] parseProblemObjects : group")
        #print(group)
        
        for term in group:
            if len(term) != 3:
                raise Exception('Invalid term length '+str(len(term))+', expected 3')
            if term[1] != self._TYPE_OPERATOR:
                raise Exception('Invalid class operator '+str(term[1])+', expected '+_TYPE_OPERATOR+'')
            
            if self.isValidType(term[2]):
                self.objects.append([term[0],term[2]])
            else:
                raise Exception(str(term[2]) + ' is not a valid type')

    #-----------------------------------------------
    # Get object from object instance name
    #-----------------------------------------------
                
    def getObject(self, object_name):
        #print(object_name)
        
        if type(object_name) is not str:
            raise Exception(' [!!!] ERROR: [getObject(' + str(object_name)+')] Invalid type, expected str')
            
        for object in self.objects:
            if object[0] == object_name:
                return object
                
        raise Exception(' [!!!] ERROR: [getObject('+str(object_name)+')] Undefined object "'+str(object_name)+'"')
        return False
        
    #-----------------------------------------------
    # Check if is valid predicate. Ignores the variable names
    # and just compares the types
    #-----------------------------------------------
        
    def isValidPredicate(self, predicate_candidate):    
        
        #print(predicate_candidate)
        #print("-------------------------1")
        #predicate_def = predicate_candidate
        
        if (predicate_candidate[0][0] == self._TRUE) or (predicate_candidate[0][0] == self._FALSE):
            return True
        elif type(predicate_candidate[0]) is list:
            if len(predicate_candidate) == 1:
                return False
            if predicate_candidate[1] == pddlglobals._PREDICATE_TYPE:
                if not self.isValidPredicate(predicate_candidate[0]):
                    print(" [..!] A subpredicate is invalid: " + str(predicate_candidate_term))
                    return False
                else:
                    return True
            else:
                #print(" [..!] Subpredicate expected, found this instead : " + str(predicate_candidate[0]))
                return False
            print("THIS SHOULD NOOOT HAPPEN")
            return None
        elif predicate_candidate[0] == self._EXEC_ACTION_OPERATOR:
            return True
        
        elif predicate_candidate[0] == self._NOT_OPERATOR:
            return self.isValidPredicate(predicate_candidate[1])
        elif predicate_candidate[0][0] == self._FORALL_VAR_OPERATOR:
            return True
        else:
            predicate_def = self.getPredicateDef(predicate_candidate[0])
            
            ctr = 0
            if not (type(predicate_def) is list):
                return False
                
            for predicate_def_term in predicate_def:
                #print(predicate_def)
                if ctr == 0:
                    pass
                else:
                    if predicate_def_term[1] == self._OBJECT_TYPE:
                        break
                    if predicate_def_term[1] == self._PREDICATE_TYPE:
                        #print(predicate_candidate[ctr])
                        if self.isValidPredicate(predicate_candidate[ctr]):
                            pass
                        else:
                            raise Exception(' [!!!] ERROR: Invalid state instance: ' + str(predicate_candidate[ctr]))
                    elif self.typeIsOfType(predicate_candidate[ctr][1],predicate_def_term[1]):
                        pass
                    else:
                        print(" [..!] [isValidPredicate] Invalid predicate: type mismatch ("+str(predicate_candidate[ctr][1])+" - "+str(predicate_def_term[1])+")")
                        return False
                ctr += 1
            return True
        
        print("THIS SHOULD NOOOT HAPPEN")
        return None
    #-----------------------------------------------
    # Parse initial state
    #-----------------------------------------------
                
    def parseInitialState(self, group):
        #print("\n\n [...] parseInitialState")
        #print(group)
        #print(" -----------------------------------------------------")
        
        
        for predicate_inst in group:
            # get predicate definition
            
            #self.defineInstances(predicate_inst)
            #if self.isValidStateInstance(predicate_inst):
                
                # buildPropositionTree(self, input_group:list, var_list:list, proposition_tree:list, mode, depth):
                
            result_proposition_tree = []
            
            #splitPropositions(self, group, proposition_tree, var_list):
            self.splitPropositions(predicate_inst,result_proposition_tree,[],[],[])
            #self.buildPropositionTree(predicate_inst, [], result_proposition_tree, 0,0)
            
            #print(str(result_proposition_tree))
            #raise Exception("asdfsadf")
            self.state.add(str(result_proposition_tree[0]))
            self.state_list.append(result_proposition_tree[0])
            #print(self.state)
            #raise Exception("!!!")
            #print("[13] Result: " + str(result_proposition_tree))
            #print(" -------->>>")
        return True

    def setInitialState(self, new_state:set):
        self.state = copy.deepcopy(new_state)
        self.state_list = []
        for somestatestr in list(new_state):
            state_list = ast.literal_eval(somestatestr)
            
            while (type(state_list is list) and (len(state_list) == 1)):
                print(" [>>>] Malformed state predicate <"+str(state_list)+">; Rectifying:")
                state_list = state_list[0]
            
            self.state_list.append(copy.deepcopy(state_list))        
        self.all_intentions = []
        self.generateAllIntentions()
            
    def setGoals(self, new_goals:list):
        #print("pddllib: new_goals")
        #print(new_goals)
        #input()
        self.goals = []
        
        self.positive_goals = []
        self.negative_goals = []
        
        
        
        #print(new_goals)
        #print("---")
        
        # [...] OLD APPROACH
        #self.splitPropositions(new_goals, self.goals, self.positive_goals, self.negative_goals, [])
        
        # [...] NEW APPROACH
        #print("----------------.sdfs")
        for some_goal in new_goals:
            
            #temp_goal = ['and', some_goal]
            temp_goal = copy.deepcopy(some_goal)
            #self.goals.append(copy.deepcopy(some_goal))
            
            #print(">> " + str(some_goal) )
            
            temp_goals = []
            self.splitPropositions(temp_goal, temp_goals, self.positive_goals, self.negative_goals, [])
            #self.splitPropositions(temp_goal, self.goals, self.positive_goals, self.negative_goals, [])
            
        
        self.goals.extend(self.positive_goals)
        self.goals.extend(self.negative_goals)
        
        #for something in self.goals:
        #    print(something)
            
        #input()
            
        #print("Domain goal breakdown")
        #
        #print(self.goals)
        #print("...")
        #print(self.positive_goals)
        #print("...")
        #print(self.negative_goals)
        #print("...")
        
        self.organizeGoals()
        
    def addGoals(self, new_goals:list):
        self.splitPropositions(new_goals, self.goals, self.positive_goals, self.negative_goals, [])
    
    
    #-----------------------------------------------
    # Split parameters
    #-----------------------------------------------
    
    def splitParameters(self, parameter_group):
        if not type(parameter_group) is list:
            raise Exception(' [!!!] ERROR: [splitParameters()] Invalid type, expected list')
        
        #print(" [..?] splitParameters")
        #print(parameter_group)
        
        valid_types = []
        valid_parameters = []
        
        for parameter_term in parameter_group:
            if len(parameter_term) != 3:
                raise Exception(' [!!!] ERROR: Invalid parameter term : ' + str(parameter_term))
            
            if parameter_term[1] == self._TYPE_OPERATOR:
                
                # memoization of isValidType function call
                if parameter_term[2] in valid_types:
                    pass
                else:
                    if self.isValidType(parameter_term[2]):
                        valid_types.append(parameter_term[2])
                    else:
                        raise Exception(' [!!!] ERROR: Undefined type "'+parameter_term[2]+'"')
                
                #---
                
                valid_parameters.append([parameter_term[0], parameter_term[2]])
                
                
            else:
                raise Exception('Invalid class operator "' + str(parameter_term[1]) + '", expected "' + self._TYPE_OPERATOR + '"')
        
        #print(" [...] valid_types")
        #print(valid_types)
        
        return valid_parameters
    
    #-----------------------------------------------
    # Valid logic operator checker
    #-----------------------------------------------
    
    def isValidPropositionOperator(self, operator_candidate:str):
        if operator_candidate in self._VALID_PROPOSITION_OPERATORS:
            return True
        else:
            return False

    def replaceVariables(self,proposition:list, var_list:list , mode = 1):
        if len(var_list) == 0:
        #    # this means proposition list has instances, not variables
            return proposition
        
        ctr=0
        for term in proposition:
            # recursively call self.replaceVariables if a sublist is encountered
            if type(term) is list:
                self.replaceVariables(term, var_list)
            # else, we proceed, assuming structure of current term is:
            #   ?var | !var | value
            
            new_term = ""
            #   ?var || !var
            if (term[0] == self._VAR_OPERATOR) or (term[0] == self._FORALL_VAR_OPERATOR):
                # check the var_list
                for var in var_list:
                    if term == var[0]:
                        new_term = var[0]
                        proposition[ctr] = copy.deepcopy(var)
                        break
                if new_term == "":
                    #raise Exception(' [!!!] ERROR: [splitPropositions()] Undefined variable "'+term+'"')
                    print(' [..!] [replaceVariables()] Undefined variable "'+term+'" ?> ' + str(var_list))
                    return False
                    
            #if term[0] == self._FORALL_VAR_OPERATOR:
                # TODO .. possibly?
            #    pass
            #   value
            else:
                pass
            ctr+=1
        return True
    
    #--------<<<<<
    
    def defineInstances(self, proposition:list):
        
        proposition_term_def = self.getPredicateDef(proposition[0])
        #print("  ins: " + str(proposition[0]))
        #print("  all: " + str(proposition))
        #print("  def: " + str(proposition_term_def))
        
        ctr=0
        for proposition_term in proposition:
            if ctr==0:
                pass
            elif type(proposition_term) is list:
                self.defineInstances(proposition_term)
            else:
                object_inst = self.getObject(proposition_term)
                proposition[ctr] = copy.deepcopy(object_inst)
                
            ctr+=1


    def buildPropositionTree(self, input_group:list, var_list:list, proposition_tree:list, positive_terms:list, negative_terms:list, mode1=-1, mode2=1, depth=0):
        
        def appendLiteralPropositions(input_proposition, mode2):
                
            proposition = copy.deepcopy(input_proposition)
            #proposition = input_group
            if mode1 == 0:
                #print("Instantiate!!!!!!!!!!!")
                #print(proposition)

                self.defineInstances(proposition)
                
            elif mode1 == -1:
                #print("PASS!!!!")
                pass
            else:
                #print("Replace!!!!!!!!!!!")
                self.replaceVariables(proposition,var_list)
                
            if type(proposition) is not list:
                #if len(proposition) == 1:
                #    print("???? > " + str(proposition))
                #    raise Exception("??")
                #else:
                #    print("!!!! > " + str(proposition))
                #    raise Exception("!!")
                print(" [????] > " + str(proposition))
                raise Exception("??")
                
            if proposition[0] in self._INTENTIONALITY_OPERATORS:
                #print("[3] ")
                #print(proposition)
                
                rebuilt_operand = []
                self.buildPropositionTree(proposition[2], var_list, rebuilt_operand, positive_terms, negative_terms, -1, -1, depth+1)
                
            # OLD APPROACH [20190725]
            #    if len(rebuilt_operand) == 1:
            #        proposition[2] = rebuilt_operand[0]
            #    else:
            #        proposition[2] = rebuilt_operand
            
            # TRY THIS
                if len(rebuilt_operand) == 1:
                    proposition[2] = [rebuilt_operand[0], pddlglobals._PREDICATE_TYPE]
                else:
                    proposition[2] = [rebuilt_operand, pddlglobals._PREDICATE_TYPE]
            
            
            if mode2 == 1:
                if not (proposition in positive_terms):
                    positive_terms.append(proposition)
                    
            elif mode2 == 0:
                if not ([self._NOT_OPERATOR, proposition] in negative_terms):
                    negative_terms.append([self._NOT_OPERATOR, proposition])
            else:
                pass
            #print("[12] mode1 " + str(mode1) + " :: " + str(proposition))
            #print(proposition)
            #print("???")
            if self.isValidPredicate(proposition):
                proposition_tree.append(proposition)
                
            else:
                raise Exception(" [!!!] ERROR: Invalid proposition: " + str(proposition))
        
        def processForAllCondition(condition_list:list, var_list:list, delete_list:list):
            
            if len(condition_list) != 3:
                raise Exception(" [!!!] ERROR: Malformed 'forall' condition clause: " + str(condition))
            if condition_list[0][0] != self._FORALL_VAR_OPERATOR:
                raise Exception(" [!!!] ERROR: Invalid 'forall' variable syntax: " + str(condition))
            if condition_list[1] != self._TYPE_OPERATOR:
                raise Exception(" [!!!] ERROR: Invalid syntax; expected: " + str(self._TYPE_OPERATOR))
            
            if not self.isValidType(condition_list[2]):
                raise Exception(" [!!!] ERROR: Invalid type: " + str(condition_list[2]))
            
            new_term = [condition_list[0],condition_list[2]]
            var_list.append(new_term)
            delete_list.append(new_term)
            return new_term
            
        def processWhenStatement(operands:list):
            
            #print(operands)
            
            when_operator = operands[0]
            when_condition = operands[1]
            when_then = operands[2]
            when_action = operands[3]
            
            if when_operator != self._WHEN_OPERATOR:
                raise Exception(" [!!!] ERROR: Expected a 'when' : " + str(operands))
            if when_then != self._THEN_OPERATOR:
                raise Exception(" [!!!] ERROR: Expected a 'then' : " + str(operands))
            
            # when - Operator
            proposition_tree.append(when_operator)
            
            # when - Condition
            new_proposition_tree = []
            self.buildPropositionTree(when_condition,var_list, new_proposition_tree, positive_terms, negative_terms, mode1, new_mode2, depth+1)
            if len(new_proposition_tree) == 1:
                #print("TWO")
                #print(new_proposition_tree)
                #input()
                proposition_tree.append(new_proposition_tree[0])
            else:
                proposition_tree.append(new_proposition_tree)

            # when - Then
            proposition_tree.append(when_then)
            
            # when - Action
            new_proposition_tree = []
            self.buildPropositionTree(when_action,var_list, new_proposition_tree, positive_terms, negative_terms, mode1, new_mode2, depth+1)
            if len(new_proposition_tree) == 1:
                #print("THREE")
                #print(new_proposition_tree)
                #input()
                proposition_tree.append(new_proposition_tree[0])
            else:
                proposition_tree.append(new_proposition_tree)

            
        # ----<<<< Readability stuff [start]
        depth_string = ""
        depth_count = 0
        while depth_count < depth:
            depth_string+=".."
            depth_count+=1
        # ----<<<< Readability stuff [end]
        
        #print("[0]")
        #print(input_group)
        
        if type(input_group) is list:
            operand_count = 0
            
            if (input_group[0] != self._EQUAL_OPERATOR) and (self.isValidPropositionOperator(input_group[0])):
                # Is valid operator
                #print("[1]")
                operator = input_group.pop(0)
                operands = input_group
                
                # >>> Mode selection
                if operator == self._NOT_OPERATOR:
                    if mode2 == 1:
                        new_mode2 = 0
                    elif mode2 == 0:
                        new_mode2 = 1
                    else:
                        new_mode2 = mode2
                else:
                    new_mode2 = mode2
                    
                # >>> Operator selection
                #FORALL operator (MUST have a WHEN operator within)
                if operator == self._FORALL_OPERATOR:
                    if len(operands) != 2:
                        
                        print(operator)
                        for operand in operands:
                            print(operand)
                        raise Exception(" [!!!] ERROR: [buildPropositionTree()] Invalid number of operands ("+str(len(operands))+") for '"+operator+"' operator")
                    #--------------------------------------------
                    
                    #print("!!!")
                    delete_list = []
                    
                    new_condition = processForAllCondition(operands[0], var_list, delete_list)
                    proposition_tree.append(operator)
                    proposition_tree.append(new_condition)
                    
                    #WHEN operator
                    if operands[1][0] == self._WHEN_OPERATOR:
                    
                        processWhenStatement(operands[1])
                        

                        
                    # TODO: can have effects WITHOUT WHEN statements
                    else:
                        raise Exception(" [!!!] ERROR: '"+str(self._WHEN_OPERATOR)+"' expected, '"+str(operands[1][0])+"' found")
                    
                    if delete_list:
                        for delete_item in delete_list:
                            del var_list[var_list.index(delete_item)]
                
                # [>] WHEN Operator
                elif operator == self._WHEN_OPERATOR:
                
                    new_operands = []
                    new_operands.append(operator)
                    new_operands.extend(operands)
                    
                    processWhenStatement(new_operands)
                    pass
                    
                # [>] NOT operator
                elif operator == self._NOT_OPERATOR:
                    if len(operands) != 1:
                        raise Exception(" [!!!] ERROR: [buildPropositionTree()] Invalid number of operands ("+str(len(operands))+") for '"+operator+"' operator")   
                    #--------------------------------------------
                    
                    proposition_tree.append(operator)
                    new_proposition_tree = []
                    self.buildPropositionTree(operands[0],var_list, new_proposition_tree, positive_terms, negative_terms, mode1, new_mode2, depth+1)
                    
                    if len(new_proposition_tree) != 1:
                        raise Exception(" [!!!] [Not] Invalid output: '"+str(new_proposition_tree)+"'")
                    else:
                        proposition_tree.append(new_proposition_tree[0])
                # [>] IF operator
                elif operator == self._IF_OPERATOR:
                    if len(operands) != 2:
                        raise Exception(" [!!!] ERROR: [buildPropositionTree()] Invalid number of operands ("+str(len(operands))+") for '"+operator+"' operator")
                    #--------------------------------------------
                    proposition_tree.append(operator)
                    new_proposition_tree = []
                    #print("Break 01")
                    #print(operands)
                    #input()
                    self.buildPropositionTree(operands[0],var_list, new_proposition_tree, positive_terms, negative_terms, mode1, new_mode2, depth+1)
                    
                # [>] AND, OR operators
                else:
                    if len(operands) < 1:
                        raise Exception(" [!!!] ERROR: [buildPropositionTree()] Invalid number of operands ("+str(len(operands))+") for '"+operator+"' operator")      
                    #--------------------------------------------
                    
                    proposition_tree.append(operator)
                    final_operand = []
                    for operand_group in operands:
                        new_proposition_tree = []
                        self.buildPropositionTree(operand_group,var_list, new_proposition_tree, positive_terms, negative_terms, mode1, new_mode2, depth+1)
                        
                        if len(new_proposition_tree) != 1:
                            #raise Exception(" [!!!] [And/Or] Invalid output: '"+str(new_proposition_tree)+"'")
                            #print("     output  : " + str(new_proposition_tree))
                            final_operand.append(new_proposition_tree)
                        else:
                            #print("     output  : " + str(new_proposition_tree[0]))
                            final_operand.append(new_proposition_tree[0])
                    proposition_tree.append(final_operand)
                
            else:
                #print("[2] ")
                # COULD be literals
                #print(" [////] input_group + " + str(input_group))
                appendLiteralPropositions(input_group, mode2)
            pass
        else:
            #print("[2]")
            # Found an named instance?
            print(" [..."+depth_string+"?] Found an named instance?")
            raise Exception(" ["+depth_string+"!!!] Unexpected named instance : " + str(input_group))
            
    #-----------------------------------------------
    # Split propositions
    #-----------------------------------------------
    
    def splitPropositions(self, group, proposition_tree, positive_terms, negative_terms, var_list):
    
        #--------<<<<< [START] Internal functions
            
        #--------<<<<<
        

        #--------<<<<< [END] Internal functions
    
        if not type(group) is list:
            raise Exception(' [!!!] ERROR: Invalid type, expected list')
            
            
        if len(var_list) == 0:
            mode1 = 0
        else:
            mode1 = 1
            
        mode2 = 1
        #proposition_tree = []
        #delete_list = []
        self.buildPropositionTree(group, var_list, proposition_tree, positive_terms, negative_terms, mode1, mode2, 0)
        
    def isValidActor(self, actor_candidate:str):
        
        for actor_element in self.objects:
            if (actor_candidate == actor_element[0]):
            
                for someactortype in self.actors:
                    if self.typeIsOfType(actor_element[1], someactortype):
                        return True
                    
        #print(self.actors)
        #raise Exception(" [!!!] ERROR: Invalid actor " + actor_candidate)
        return False
                
    #-----------------------------------------------
    # Intention generation methods
    #-----------------------------------------------
    
    def generateAllIntentions(self):
        
        #all_intentions = []
        
        #print(" [...>] State predicates")
        #print(" [...>] State string     : " + self.state)
        #state_list = ast.literal_eval(self.state)
        
        
        #print(" [...>] State predicates : " + str(state_list))
        #raise Exception("!!!")
        for raw_predicate in self.state:
        
            #print(" [...>] State string     : " + raw_predicate)            
            predicate = ast.literal_eval(raw_predicate)
            
            #print(" [...>] State string     : " + raw_predicate)            
            #print(" [...>] State predicates : " + str(predicate))
            #raise Exception("!!!")
            #print(predicate)
            if predicate[0] in self._INTENTIONALITY_OPERATORS:
                #print(" [...>>>] Valid intention:")
                
                
                actor_term = predicate[1]
                state = predicate[2]
                
                self.all_intentions.append([copy.deepcopy(actor_term),copy.deepcopy(state)])
                
    
    #-----------------------------------------------
    # Get intention methods
    #-----------------------------------------------
    
    def getActorIntentions(self, actor:str):
        actor_intentions = []
        for intention in self.all_intentions:
            #print(" ????")
            #print(intention)
            if intention[0][0] == actor:
                actor_intentions.append(intention)
                
        return actor_intentions
    
    def getAllIntentions(self):
        return self.all_intentions

    #-----------------------------------------------
    # Organize all goals into nested dictionaries
    #-----------------------------------------------
        
    def organizeGoals(self):
        
        
        self.goal_count = len(self.goals)
        
        #if self.goals[0] == self._OR_OPERATOR:
        #    self.goal_count = len(self.goals[1])
        #else:
        #    self.goal_count = 1
        #self.goal_dict = {}
        
        #for goal in self.goals:
        #    print
        
        return
    
    def getObjectsWithType(self, object_type):
        object_list = []
        for someobject in self.objects:
            if self.typeIsOfType(someobject[1], object_type):
                object_list.append(copy.deepcopy(someobject))
        return object_list
            

    #-----------------------------------------------
    # Manual creation of Domain-Problem elements
    #-----------------------------------------------
    #   - Redirect parse functions to these subroutines for consistency
    #   - Add more checking mechanisms
    #   
    # ----------------
    #  Domain 
    
    # self.type_list = []
    # self.actors = []
    # self.predicates = []
    # self.actions = []    
    
    #def addRequirements(self):
    #    pass
    
    def addType(self, parameters:dict):
        
        type_name = parameters['type_name']
        parent    = parameters['parent']
        
        self.type_list.append([type_name, parent])
        
    def addActor(self, parameters:dict):
        actor = parameters['actor']
        
        if self.isValidType(actor):
            self.actors.append(actor)
        else:
            raise Exception(' [!!!] ERROR: Invalid actor, undefined type "'+str(actor)+'"')
        
    def addPredicate(self, parameters:dict):
    
        #================
        raw_input_list = parameters['raw_input_list']
        predicate_prefix = raw_input_list.pop(0)
        name = raw_input_list.pop(0)
        
        if predicate_prefix.lower() != ":predicate":
            raise Exception("Syntax error: " + str(predicate_prefix))
        
        if not type(name) is str:
            raise Exception('State Predicate without name definition')
        for pred in self.predicates:
            if pred.name == name:
                raise Exception('State Predicate ' + name + ' redefined')
                
        #print("------PROCESSING PREDICATE: " + name)
        
        new_predicate = []
        parameters = []
        definition = []
        primary_obj = []
        secondary_obj = []
        humanreadables = []
        
        while raw_input_list:
            term = raw_input_list.pop(0)
            if term == ':parameters':
                if not type(raw_input_list) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = self.splitParameters(raw_input_list.pop(0))
                #print("parameters: " + str(parameters))
            elif term == ':definition':
            
                predicate_def = raw_input_list.pop(0)
                #print("predicate_def : " + str(predicate_def))
                predicate_def_name = predicate_def.pop(0)
                
                if predicate_def_name.lower() != name.lower():
                    raise Exception("Predicate name mismatch: " + str(predicate_def_name) + " != " + str(name))
                else:
                    definition.append(name)
                    
                for term in predicate_def:
                    #print(term)
                    if len(term) == 3:
                        if term[1] == self._PARENT_OPERATOR:
                            if self.isValidType(term[2]):
                                definition.append([term[0],term[2]])
                            elif term[2] == self._OBJECT_TYPE:
                                definition.append([term[0],term[2]])
                            elif term[2] == self._PREDICATE_TYPE:
                                definition.append([term[0],term[2]])
                            else:
                                raise Exception('Undefined type: "'+str(term[2])+'"')
                    else:
                        raise Exception('Invalid parent class operator "' + str(term[1]) + '", expected "' + self._PARENT_OPERATOR + '"')
                        
                #print("definition : " + str(definition))
                
            elif term == ':primary_obj':
                #print(" [...>>] Primary")
                self.parseAgents(raw_input_list.pop(0), primary_obj, parameters)
            elif term == ':secondary_obj':
                #print(" [...>>] Secondary")
                self.parseAgents(raw_input_list.pop(0), secondary_obj, parameters)
                
            elif term == ':humanreadable':
                #print(" [...>>] Human-readable string")
                self.parseHumanReadableStr(raw_input_list.pop(0), humanreadables, parameters)
            
        self.predicates.append(Predicate(   name,
                                            parameters, 
                                            definition, 
                                            primary_obj,
                                            secondary_obj,
                                            humanreadables))
        
        #print(self.predicates[-1])
        #input()
        
        
        #================
    #    predicate_def = parameters['predicate'][0]
    #    predicate_hrstring = parameters['predicate'][1]
    #    
    #    print(predicate_hrstring)
    #    input()
    #    
    #    predicate_name = predicate_def.pop(0)
    #    predicate_term_list = []
    #                    
    #    for term in predicate_def:
    #        
    #        if len(term) == 3:
    #            if term[1] == self._PARENT_OPERATOR:
    #                if self.isValidType(term[2]):
    #                    predicate_term_list.append([term[0],term[2]])
    #                elif term[2] == self._OBJECT_TYPE:
    #                    predicate_term_list.append([term[0],term[2]])
    #                elif term[2] == self._PREDICATE_TYPE:
    #                    predicate_term_list.append([term[0],term[2]])
    #                else:
    #                    raise Exception('Undefined type: "'+str(term[2])+'"')
    #        else:
    #            raise Exception('Invalid parent class operator "' + str(term[1]) + '", expected "' + self._PARENT_OPERATOR + '"')
    #    
    #    output_predicate = []
    #    output_predicate.append(predicate_name)
    #    output_predicate.extend(predicate_term_list)
    #    self.predicates.append(output_predicate)
        
    def addAction(self, parameters:dict):
        #----------------------------
        
        #----------------------------
        
        raw_input_list = parameters['raw_input_list']
        
        name = raw_input_list.pop(0)
        if not type(name) is str:
            raise Exception('Action without name definition')
        for act in self.actions:
            if act.name == name:
                raise Exception('Action ' + name + ' redefined')
                
        #print("------PROCESSING ACTION: " + name)
        
        parameters = []
        preconditions = []
        positive_preconditions = []
        negative_preconditions = []
        effects = []
        positive_effects = []
        negative_effects = []
        agents = []
        humanreadables = []
        
        while raw_input_list:
            term = raw_input_list.pop(0)
            if term == ':parameters':
                if not type(raw_input_list) is list:
                    raise Exception('Error with ' + name + ' parameters')
                parameters = self.splitParameters(raw_input_list.pop(0))
            elif term == ':precondition':
                #print(" [...>>] Precon")
                self.splitPropositions(raw_input_list.pop(0), preconditions, positive_preconditions, negative_preconditions, parameters)
                #print("[14] Result: " + str(preconditions))
            elif term == ':effect':
                #print(" [...>>] Effect")
                self.splitPropositions(raw_input_list.pop(0), effects, positive_effects, negative_effects, parameters)
                
                
            elif term == ':agents':
                #print(" [...>>] Agents")
                self.parseAgents(raw_input_list.pop(0), agents, parameters)
                #print(" <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                
            elif term == ':humanreadable':
                #print(" [...>>] Human-readable string")
                self.parseHumanReadableStr(raw_input_list.pop(0), humanreadables, parameters)
            else: 
                raise Exception(' [!!!] ERROR: [parseActions()] ' + str(term) + ' is not recognized in action')
                #print(str(term) + ' is not recognized in action')
        #if name == "marry":
        #    print(negative_effects)
            #input("..")
        #    print(" [...>>>>] parameters: " + str(parameters))
            
        #print("addAction: "+name+" Start")
        #extractNestedActions(effects, positive_effects, negative_effects)
        #print("addAction: "+name+" Done")
        
            
        self.actions.append(Action(name, parameters, preconditions, positive_preconditions, negative_preconditions, effects, positive_effects, negative_effects, agents, humanreadables))

    # ----------------
    #  Problem
    
    
class DomainProblemParser:

    def __init__(self, domainproblem:DomainProblem):
        
        # Mostly for the constants
        self.domainproblem = domainproblem
        self.effects_cache = dict()
        
    def getActorIntentions(self, actor:str, state:list):
        actor_intentions = []
        for intention in self.all_intentions:
            #print(" ????")
            #print(intention)
            if intention[0][0] == actor:
                actor_intentions.append(intention)
                
        return actor_intentions
    
    def getAllIntentions(self, state:set):
        all_intentions = []
        for raw_candidate_intention in state:
            candidate_intention = ast.literal_eval(raw_candidate_intention)
            #print(" [????] Parser: candidate_intention :: " + str(candidate_intention))
            if candidate_intention[0] in self.domainproblem._INTENTIONALITY_OPERATORS:
            
                
                new_intention = [candidate_intention[1][0],candidate_intention[2]]
                if new_intention not in all_intentions:
                    all_intentions.append(new_intention)
                
    
        return all_intentions
    
    def createActionInstance(self, action_def:Action, parameter_def_list):
        
        def replaceVariables(input_list:list, parameter_label_list:list, parameter_instance_list:list):
            output_list = []
            #print(" [...>>] replaceVariables")
            #output_list = self.domainproblem.replaceVariables(input_list, parameter_label_list)
            #print(parameter_instance_list)
            
            for input_element in input_list:
            
                replacement_element = []
                output_list_element = []
                
                #print(input_element)
                
                if type(input_element) is list:
                    pre_len = len(input_element)
                    #if len(input_element) == 2:
                        # maybe a variable 2-tuple
                    #print("[1] " + str(input_element[0][0]))
                    if input_element[0][0] == self.domainproblem._VAR_OPERATOR:
                        # yes it is
                        found_flag = False
                        param_ctr = 0
                        for param_label in parameter_label_list:
                            #print(" [...>>>>] Comparing : " + str(input_element) + " == " + str(param_label))
                            if input_element[0] == param_label[0]:
                                replacement_element = parameter_instance_list[param_ctr]
                                found_flag = True
                                #print(" [...>>>>]MATCH PUTA : " + str(input_element) + " << " + str(replacement_element))
                                break
                            param_ctr += 1
                        if found_flag:
                            output_list_element = copy.deepcopy(replacement_element)
                            #print(" [1] " + str(output_list_element))
                        else:
                            raise Exception(' [!!!] ERROR: No match found for: ' + str(input_element))
                    
                    else:
                        output_list_element = replaceVariables(input_element, parameter_label_list, parameter_instance_list)
                        #print(" [2] " + str(output_list_element))
                    #else:
                        #output_list_element = replaceVariables(input_element, parameter_label_list, parameter_instance_list)
                        #print(" [3] " + str(output_list_element))
                    post_len = len(input_element)
                else:
                    output_list_element = input_element
                output_list.append(output_list_element)
            return output_list
            
        def replaceVariables2(input_list:list, parameter_label_list:list, parameter_instance_list:list):
            output_list = []
            for input_elem in input_list:
                output_elem = copy.copy(input_elem)
                output_elem = output_elem.replace('"','')
                i = 0
                for some_label in parameter_label_list:
                    some_instance = parameter_instance_list[i]
                    output_elem = output_elem.replace(some_label[0], some_instance[0])
                    i += 1
                output_list.append(output_elem)
            return output_list
        
        parameters = parameter_def_list
        name = action_def.name
        
        #if "creature_injures_creature" in action_def.getFunctionString():
        #    print("dsafasdf")
        #    print(action_def.effects)
        #    print("--")
        #    print(action_def.possible_positive_effects)
        #    print("--")
        #    print(action_def.possible_negative_effects)
        #    input()
        
        try:
        
            # [4] Replace variables
            #   >> Preconditions
            preconditions = replaceVariables(action_def.preconditions, action_def.parameters, parameters)
            positive_preconditions = replaceVariables(action_def.positive_preconditions, action_def.parameters, parameters)
            negative_preconditions = replaceVariables(action_def.negative_preconditions, action_def.parameters, parameters)
            
            #   >> Effects
            effects = replaceVariables(action_def.effects, action_def.parameters, parameters)
            possible_positive_effects = replaceVariables(action_def.possible_positive_effects, action_def.parameters, parameters)
            
            possible_negative_effects = replaceVariables(action_def.possible_negative_effects, action_def.parameters, parameters)
            agents = replaceVariables(action_def.agents, action_def.parameters, parameters)
            
            #   >> Human Readables
            humanreadables = replaceVariables2(action_def.humanreadables, action_def.parameters, parameters)
            
            #   >> Action instance
            #new_action_instance = Action(name, parameters, preconditions, positive_preconditions, negative_preconditions, effects, positive_effects, negative_effects, agents)
            new_action_instance = Action(name, parameters, preconditions, positive_preconditions, negative_preconditions, effects, possible_positive_effects, possible_negative_effects, agents, humanreadables)
            
            new_positive_effects = []
            new_negative_effects = []
            
            #print("[__!] " + str(new_action_instance.getFunctionString()))
            self.extractNestedActionEffects(new_action_instance.effects, new_positive_effects, new_negative_effects)
            
            new_action_instance.possible_positive_effects.extend(new_positive_effects)
            new_action_instance.possible_negative_effects.extend(new_negative_effects)
            
            return new_action_instance
        except Exception:
            return None
    
    def updateState(self, current_state:set, positive_effects:list, negative_effects:list):
        output_state = copy.deepcopy(set(current_state))
        exec_list = []
        
        for some_effect in positive_effects:
            if self.domainproblem._EXEC_ACTION_OPERATOR in str(some_effect):
                #print("EXEC ACTION: " + str(some_effect))
                exec_list.append(copy.deepcopy(some_effect))
                
            else:
                #print("ADDING: " + str(some_effect))
                output_state.add(str(some_effect))
            
        for some_effect in negative_effects:
            #print("REMOVING: " + str(some_effect))
            try:
                output_state.remove(str(some_effect))
            except:
                pass
            
            
        for some_exec in exec_list:
            #print("APLYING: " + str(some_exec))
            exec_command = some_exec
            
            exec_operator = exec_command[0]
            exec_operand = exec_command[1]
            action_name = exec_operand[0]
            
            action_def = self.domainproblem.getAction(action_name)
            
            parameter_def_list = copy.copy(exec_operand)
            parameter_def_list.pop(0)
            
            action_instance = self.createActionInstance(action_def, parameter_def_list)
            if action_instance is None:
                logstr = " [!!!] ERROR: No action instances available for '"+str(action_name)+"'"
                raise Exception(logstr)
            else:
                output_state = self.applyAction(action_instance, output_state)
                
        return output_state
    
    def evalPropositionTree(self, operator:str, proposition_tree:list, current_state:set, mode = 1, name = ""):
        # Process [01] : Intial checks:
        if not type(proposition_tree) is list:
            print(proposition_tree)
            raise Exception(' [!!!] ERROR: [evalPropositionTree()] Invalid type, expected list: ' + str(type(proposition_tree)) + " : " + str(proposition_tree))
        
        # Process [02a] : TRUE comparison
        elif proposition_tree == [self.domainproblem._TRUE]:
            return True

        # Process [02b] : FALSE comparison
        elif proposition_tree == [self.domainproblem._FALSE]:
            return False
            
        # Process [03] : EQUALS comparison
        elif operator == self.domainproblem._EQUAL_OPERATOR:

            if len(proposition_tree) != 2:
                raise Exception(" [!!!] Can only compare 2 items using '"+str(self.domainproblem._EQUAL_OPERATOR)+"' operand: '" + str(proposition_tree) + "'")
            
            #raise Exception("EQUALS COMPARISON!!!!")
            if proposition_tree[0] == proposition_tree[1]:
                value = True
            else:
                value = False
            #if name == "goal_parsing": print("[01a] " + str(operator) + ":" + str(proposition_tree) + " = " + str(value))
            return value
        # Process [04] : If the first term is an operand, evalPropositionTree() call recursively
        #if (self.domainproblem.isValidPropositionOperator(proposition_tree[0])) and (proposition_tree[0] != self.domainproblem._EQUAL_OPERATOR):
        elif (self.domainproblem.isValidPropositionOperator(proposition_tree[0])):
            if (proposition_tree[0] == self.domainproblem._EQUAL_OPERATOR):

                if len(proposition_tree) != 3:
                    raise Exception(" [!!!] Invalid operator-operand count: '" + str(proposition_tree) + "'")
                
                new_operator = proposition_tree[0]
                new_operands = [proposition_tree[1],proposition_tree[2]]
                
                #if name == "goal_parsing": print("[03a] new operator: " + str(new_operator) + " / new operands: " + str(new_operands) + " >> delving...")
                value = self.evalPropositionTree(new_operator, new_operands, current_state, mode, name)                
                if operator == self.domainproblem._NOT_OPERATOR:
                    return not value
                else:
                    return value                
            else:
            
                if len(proposition_tree) != 2:
                    raise Exception(" [!!!] Invalid operator-operand count: '" + str(proposition_tree) + "'")
                
                new_operator = proposition_tree[0]
                new_operands = proposition_tree[1]
                
                #if name == "marry":
                #    print("[02] operator: " + str(new_operator) + " / operands: " + str(new_operands))
                #if operator == self.domainproblem._EQUAL_OPERATOR:
                #    print("[02] operator: " + str(new_operator) + " / operands: " + str(new_operands))
                #if name == "goal_parsing": print("[03b] new operator: " + str(new_operator) + " / new operands: " + str(new_operands) + " >> delving...")
                value = self.evalPropositionTree(new_operator, new_operands, current_state, mode, name)
                #if name == "goal_parsing": print("[03c] new operator: " + str(new_operator) + " / new operands: " + str(new_operands) + " : " + str(value))
                
                if operator == self.domainproblem._NOT_OPERATOR:
                    #if name == "goal_parsing": print("[03da] : " + str(not value))
                    value = not value
                else:
                    #if name == "goal_parsing": print("[03db] : " + str(value))
                    value = value
                    
                #if name == "goal_parsing": print("[03e] : " + str(value))
                return value
                
        # Process [05] : Attempt to evaluate the list of operands using the operator parameter
        else:
            value = False
            #potato_flag = False
            #if name == "goal_parsing": print("[04] operator" + str(proposition_tree))
            #if name == "goal_parsing": print("[04] operator: " + str(operator) + " / operands: " + str(proposition_tree))
            
            if self.domainproblem.getPredicateDef(proposition_tree[0]) is not False:
                if mode == 1:
                    #if str(proposition_tree) in current_state:
                    
                    #for some_state in current_state:
                    #    if (name == "goal_parsing") and (str(proposition_tree[0]) == "single"):
                    #        print("[04aa] > " + str(some_state) + " == " + str(proposition_tree) + " ???")
                    
                    found_flag = False
                    proposition_str = str(proposition_tree)
                    for somepred in current_state:
                        if proposition_str == somepred:
                            found_flag = True
                            break
                    #if str(proposition_tree) in current_state:
                    
                    if found_flag:
                        #print("[04a] value: " + str(proposition_tree) + " is True")
                        value = True
                    else:
                        #print("[04b] value: " + str(proposition_tree) + " is False")
                        value = False
                            
                else:
                    if name == "goal_parsing": print("[04c] forced True")
                    value = True
                    
                #if name == "goal_parsing": 
                    #print("[04d] value: " + str(value))
                    #for state_pred in current_state:
                    #    print("        "+str(state_pred))
                
                if operator == self.domainproblem._NOT_OPERATOR:
                    value = not value
                    
                return value
            else:
            
                if (len(proposition_tree) == 2):
                    #print("EEP")
                    # Substep 1. Determine if second element is a type name
                    if proposition_tree[1] == pddlglobals._PREDICATE_TYPE:
                        new_operator = self.domainproblem._AND_OPERATOR
                        new_operands = proposition_tree[0]
                        value = self.evalPropositionTree(new_operator, new_operands, current_state, mode, name)
                        return value
                
            
                # Process [05] : Loop through the proposition_tree list (list of lists)
                for proposition_term in proposition_tree:            
                    # Process [05] : Each operand is a potential subtree; check for an operator
                    # Process [06] : Loop through each term, as recursion is possible if a subterm is another tree
                    #   e.g.    
                    #        and    (marriedto ?groom ?bride)
                    #               (marriedto ?bride ?groom)
                    #               (not ( and  (single ?groom) <-- : 'and' with 'not' with 'and' 
                    #                           (single ?bride)
                    #               )
                    #        )                
                    

                    if self.domainproblem.isValidPropositionOperator(proposition_term[0]):
                        new_operator = proposition_term[0]
                        new_operands = proposition_term[1]
                        #if name == "steal":
                        #    print("[05] operator: " + str(new_operator) + " / operands: " + str(new_operands))
                        #if name == "goal_parsing": print("[05a] new operator: " + str(new_operator) + " / new operands: " + str(new_operands) + " >> delving...")
                        value = self.evalPropositionTree(new_operator, new_operands, current_state, mode, name)
                        #print("[05b] value: " + str(value))
                    else:
                        new_operator = self.domainproblem._AND_OPERATOR
                        new_operands = proposition_term                    
                        #if name == "goal_parsing": print("[05b] new operator: " + str(new_operator) + " / new operands: " + str(new_operands) + " >> delving...")
                        value = self.evalPropositionTree(new_operator, new_operands, current_state, mode, name)
                        
                    #print(" >> shortcuts")
                    if (operator == self.domainproblem._AND_OPERATOR) and (value == False):
                        return False
                    elif (operator == self.domainproblem._OR_OPERATOR) and (value == True):
                        return True
                    elif (operator == self.domainproblem._NOT_OPERATOR):
                        print(" >>>> SHORTCUT: not ["+str(not value)+"]")
                        return not value

                #print("[04] Done with for-loop: ")
                #print("     operator: " + str(operator))
                # no False encountered
                if operator == self.domainproblem._AND_OPERATOR:
                    return True
                # no True encountered
                elif operator == self.domainproblem._OR_OPERATOR:
                    return False
                else:
                    raise Exception(" [!!!] Unknown outcome:")
    
    def evalEffects(self, effect_tree:list, current_state:set, positive_effects:list, negative_effects:list, debug=False):
        
        #def __updateState(current_state:set, positive_effects:list, negative_effects:list):
        #    output_state = copy.deepcopy(current_state)
        #    
        #    for some_effect in positive_effects:
        #        output_state.add(str(some_effect))
        #        
        #    for some_effect in negative_effects:
        #        try:
        #            output_state.remove(str(some_effect))
        #        except:
        #            pass
        #        
        #    return output_state
                
        def __updateEffectLists(candidate:list, positive_effects:list, negative_effects:list):
            
            if candidate[0] != self.domainproblem._NOT_OPERATOR:
                if candidate not in positive_effects:
                    positive_effects.append(copy.deepcopy(candidate))
            else:
                if candidate[1] not in negative_effects:
                    negative_effects.append(copy.deepcopy(candidate[1]))
                
                
        def __replaceVariables(proposition:list, var_def:list, obj_def:list):
            'Replace all instances of var_def with obj_def'
            
            if proposition == var_def:
                #print(obj_def)
                #print(proposition)
                #print(var_def)
                #print("???")
                #input()
                #proposition = copy.deepcopy(obj_def)
                proposition[0] = obj_def[0]
                proposition[1] = obj_def[1]
                return
                
            for term in proposition:
                # recursively call self.replaceVariables if a sublist is encountered
                if type(term) is list:
                    __replaceVariables(term, var_def, obj_def)
            
            return
        
        #   For now, only has support for AND operator
        
        if not (type(effect_tree) is list):
            raise Exception("Invalid effect_tree type: " + str(type(effect_tree)))
            
        #----
        
        if effect_tree[0] == self.domainproblem._AND_OPERATOR:
            #print("Found 'AND'... diving")
            self.evalEffects(effect_tree[1], current_state, positive_effects, negative_effects,debug=debug)
        else:
            #print("____|" + str(effect_tree))
            if self.domainproblem.isValidPredicate(effect_tree):
                #print("PREDICATE [1]: " + str(effect_tree))
                __updateEffectLists(effect_tree, positive_effects, negative_effects)
            
            else:
            
                for some_effect in effect_tree:
                    operator = some_effect[0]
                    
                    #   >> AND
                    if operator == self.domainproblem._AND_OPERATOR:
                        #print("NESTED AND:")
                        self.evalEffects(some_effect, current_state, positive_effects, negative_effects, debug=debug)
                        
                    #   >> FORALL
                    elif operator == self.domainproblem._FORALL_OPERATOR:
                        
                        
                        
                        f_variable = some_effect[1]
                        f_variable_name = f_variable[0]
                        f_variable_type = f_variable[1]
                        
                        f_when_operator = some_effect[2]
                        f_when_condition = some_effect[3]
                        f_when_then = some_effect[4]
                        f_when_predicate = some_effect[5]
                        
                        if debug == True:
                            print("[...] FORALL")
                            print(f_variable)
                            print(f_variable_name)
                            print(f_variable_type)
                            
                            print(f_when_operator)
                            print(f_when_condition)
                            print(f_when_then)
                            print(f_when_predicate)
                        
                        obj_list = self.domainproblem.getObjectsWithType(f_variable_type)
                        
                        for obj_instance in obj_list:
                            #print(obj_instance)
                            
                            curr_when_condition = copy.deepcopy(f_when_condition)
                            curr_when_predicate = copy.deepcopy(f_when_predicate)
                            
                            __replaceVariables(curr_when_condition,f_variable,obj_instance)
                            __replaceVariables(curr_when_predicate,f_variable,obj_instance)
                            

                            temp_state = self.updateState(current_state, positive_effects, negative_effects)
                            
                            if debug == True:
                                print("\t" + str(curr_when_condition))
                                print("\t" + str(curr_when_predicate))
                            
                            
                            if self.evalPropositionTree(self.domainproblem._AND_OPERATOR, curr_when_condition, temp_state):
                                self.evalEffects(curr_when_predicate, temp_state, positive_effects, negative_effects, debug=debug)
                        
                        if debug:
                            print("[...] FORALL effects")
                            print(positive_effects)
                            print(negative_effects)
                        
                    #   >> WHEN
                    elif operator == self.domainproblem._WHEN_OPERATOR:
                        #print(" [DEBUG] Developing WHEN parsing")
                        when_operator = some_effect[0]
                        when_condition = some_effect[1]
                        when_then = some_effect[2]
                        when_action = some_effect[3]
                        
                        if (when_operator != self.domainproblem._WHEN_OPERATOR):
                            logstr = " [!!!] ERROR: Invalid 'WHEN' operator: " + str(when_operator)
                            raise Exception(logstr)
                        if (when_then != self.domainproblem._THEN_OPERATOR):
                            logstr = " [!!!] ERROR: Invalid 'THEN' operator: " + str(when_then)
                            raise Exception(logstr)
                        
                        if debug:
                            print("[...] WHEN-THEN")
                            print(when_operator)
                            print(when_condition)
                            print(when_then)
                            print(when_action)
                            print("---------------------------")
                        #input()
                        temp_state = self.updateState(current_state, positive_effects, negative_effects)
                        
                        if self.evalPropositionTree(self.domainproblem._AND_OPERATOR, when_condition, temp_state):
                            self.evalEffects(when_action, temp_state, positive_effects, negative_effects, debug=debug)
                        if debug:
                            print("[...] WHEN-THEN effects")
                            print(positive_effects)
                            print(negative_effects)
                    #   >> VALID PREDICATE
                    elif self.domainproblem.isValidPredicate(some_effect):
                        #print("PREDICATE [2]: " + str(some_effect))
                        __updateEffectLists(some_effect, positive_effects, negative_effects)                        
        pass
    
    def preconditionSatisfied(self, some_action:Action, current_state:set, debug=False):
        #print(" [...] preconditionSatisfied")
        #print(" [...>>] Preconditions:")
        #print(some_action.preconditions)
        #
        #print(" [...>>] Current State:")
        #print(current_state)
        
        result = self.evalPropositionTree(self.domainproblem._AND_OPERATOR, some_action.preconditions,current_state, name=some_action.name)
        #print(some_action.getFunctionString() + " : " + str(result))
        #raise Exception("Stooooop")
        
        return result
    
    def applyAction(self, current_step:Action, current_state:set):
        output_state = set()
        #dp_parser = self.planner_parameters['dp_parser']
        positive_effects = []
        negative_effects = []
        
        if (self.preconditionSatisfied(current_step,current_state)):
            
            debug = False
            #if "creature_loots_creature" in current_step.getFunctionString():
            #    print("APPLY ACTION-----------------")
            #    debug = True
            #    self.evalEffects(current_step.effects, current_state, positive_effects, negative_effects, debug=True)
                
            self.evalEffects(current_step.effects, current_state, positive_effects, negative_effects, debug=False)
            #print("P----")
            #print(positive_effects)
            #print("n----")
            #print(negative_effects)
            #print("AGAIN")
        else:
            #print(current_step.getFunctionString())
            #print(current_state)
            raise Exception("Preconditions for action '"+current_step.getFunctionString()+"' has not been met")
        
        output_state = copy.deepcopy(self.updateState(current_state, positive_effects, negative_effects))
        
        
        #print("Resulting State:")
        #for state_predicate in current_state:
        #    print(state_predicate)
            
        #raise Exception("Stop")
        return output_state
        
    def extractNestedActionEffects(self, effects:list, possible_positive_effects, possible_negative_effects):
        
        #--------------------------------------------------------
        
        for some_effect in effects:
            
            if type(some_effect) is str:
                continue
            elif type(some_effect) is list:
                
                if some_effect[0] == self.domainproblem._EXEC_ACTION_OPERATOR:
                    #print("extractNestedActionEffects: some_effect:" + str(some_effect))
                    
                    exec_operator = some_effect[0]
                    exec_operand = some_effect[1]
                    action_name = exec_operand[0]
                    
                    action_def = self.domainproblem.getAction(action_name)
                    
                    parameter_def_list = copy.copy(exec_operand)
                    parameter_def_list.pop(0)
                    
                    action_instance = self.createActionInstance(action_def, parameter_def_list)
                    try:
                        new_effects = self.effects_cache[action_instance.getFunctionString()]
                    except KeyError:
                        new_effects = {}
                        new_effects['possible_positive_effects'] = []
                        new_effects['possible_negative_effects'] = []
                        
                        new_effects['possible_positive_effects'].extend(action_instance.possible_positive_effects)
                        new_effects['possible_negative_effects'].extend(action_instance.possible_negative_effects)
                        
                        new_effects['possible_positive_effects'] = self.explodeAllVariablePredicates(new_effects['possible_positive_effects'])
                        new_effects['possible_negative_effects'] = self.explodeAllVariablePredicates(new_effects['possible_negative_effects'])                        
                        self.extractNestedActionEffects(action_instance.effects, new_effects['possible_positive_effects'], new_effects['possible_negative_effects'])
                        
                        self.effects_cache[action_instance.getFunctionString()] = copy.deepcopy(new_effects)
                        
                    for something in new_effects['possible_positive_effects']:
                        if not (something in possible_positive_effects):
                            possible_positive_effects.append(something)
                            
                    for something in new_effects['possible_negative_effects']:
                        if not (something in possible_negative_effects):
                            possible_negative_effects.append(something)

                    #possible_positive_effects.extend(new_effects['possible_positive_effects'])
                    #possible_negative_effects.extend(new_effects['possible_negative_effects'])                       
                    
                    #print(" [...] (extractNestedActionEffects) Debugging")
                    #print(action_instance.getFunctionString())
                    #for something in possible_positive_effects:
                    #    print(something)
                    #print("----")
                    #for something in possible_negative_effects:
                    #    print(something)
                    #input()
                else:
                    #print("extractNestedActionEffects: DIVING ["+str(some_effect)+"]")
                    self.extractNestedActionEffects(some_effect, possible_positive_effects, possible_negative_effects)
            
    def explodeAllVariablePredicates(self, input_list:list):
        
        copy_input_list = copy.deepcopy(input_list)
        output_list = []
        update_list = []
        remove_list = []
        
        for some_effect in input_list:
            some_effect_str = str(some_effect)
            if (self.domainproblem._VAR_OPERATOR in some_effect_str) or (self.domainproblem._FORALL_VAR_OPERATOR in some_effect_str):
            
                if some_effect[0] == self.domainproblem._NOT_OPERATOR:
                    update_list.extend(self.explodeVariablePredicate(some_effect[1], 1))
                    remove_list.append(some_effect)
                
                else:
                    update_list.extend(self.explodeVariablePredicate(some_effect))
                    remove_list.append(some_effect)
                
        if update_list != []:
            for some_remove in remove_list:
                copy_input_list.remove(some_remove)
                
            copy_input_list.extend(update_list)
            output_list = copy.deepcopy(copy_input_list)
        else:
            output_list = copy.deepcopy(input_list)
                
        return output_list
    
    def explodeVariablePredicate(self, input_predicate:list, not_flag=0):
        
        output_list = []
        bulk_def = []
        ctr = 0
        
        #self.domainproblem._VAR_OPERATOR = "?"
        #self.domainproblem._FORALL_VAR_OPERATOR = "!"
        var_operators = [self.domainproblem._VAR_OPERATOR, self.domainproblem._FORALL_VAR_OPERATOR]
        
        if not self.domainproblem.isValidPredicate(input_predicate):
            raise Exception(" [!!!] (explodeVariablePredicate) Invalid predicate : " + str(isValidPredicate))
        for some_term in input_predicate:
            if ctr == 0:
                ctr += 1
                predicate_name = some_term
                bulk_def.append([predicate_name])
            else:
                
                if len(some_term) != 2:
                    print("Error??? : " + str(some_term))
                    raise Exception(" [!!!] (explodeVariablePredicate) Invalid term length '"+str(len(some_term))+"', expected [literal, type] format")
                else:
                    if some_term[0][0] in var_operators:
                        intances_list = self.domainproblem.getObjectsWithType(some_term[1])
                        bulk_def.append(intances_list)
                    else:
                        
                        bulk_def.append([some_term])
                pass
                
                
        
        for brane_def in bulk_def:
            if output_list == []:
                output_list.append(brane_def)
            else:
                new_output_list = []
                
                for ol_elem in output_list:
                    for brane_elem in brane_def:
                    
                        instance_entry = []
                        instance_entry.extend(ol_elem)
                        
                        instance_entry.append(brane_elem)
                        new_output_list.append(copy.deepcopy(instance_entry))
                        
                output_list = new_output_list
        
        if not_flag == 1:
            new_output_list = []
            for some_output in output_list:
                new_output_list.append([self.domainproblem._NOT_OPERATOR,some_output])
            
            output_list = new_output_list
        
        #print(" [...] (explodeVariablePredicate) Debugging")
        #print(" Input: " + str(input_predicate))
        #print("----")
        #print(" Output:")
        #for something in output_list:
        #    print(something)
        return output_list
        pass

    def getGoalScore(self, current_state:set, total_goals:list):
        'Returns the percentage of total_goals that will be true after applying this action'
        
        max_score = 0
        raw_score = 0
        
        for predicate_term in total_goals:
            max_score += 1
            #print("[DEBUG] [0]" + str(predicate_term))

            # NEGATIVE
            if predicate_term[0] == self.domainproblem._NOT_OPERATOR:
                if (not (str(predicate_term[1]) in current_state)):
                    #print("[DEBUG] [1]" + str(predicate_term))
                    raw_score += 1
                    
            # POSITIVE
            else:
                if (str(predicate_term) in current_state):
                    #print("[DEBUG] [2]" + str(predicate_term))
                    raw_score += 1
                
        return (raw_score/max_score)
        
    def sanitizeIntentions(self, current_state:set):
        
        new_state = copy.copy(current_state)
        
        for some_predicate_str in current_state:
            some_predicate_list = ast.literal_eval(some_predicate_str)
            if some_predicate_list[0] in self.domainproblem._INTENTIONALITY_OPERATORS:
                if str(some_predicate_list[2]) in new_state:
                    new_state.remove(some_predicate_str)
        
        
        return new_state
    
    def convertToHRParagraph(self, current_state:set, filter={"adjacency":True, "intentions":True, "normal":True}, sort="default", debug=False):
        
        # modes (true/false) dict:
        #   intentions
        #   adjacency
        
        output_paragraph = ""
        output_list = []
        
        for some_predicate in current_state:
            
            some_predicate_list = ast.literal_eval(some_predicate)
            pred_name = some_predicate_list.pop(0)
            pred_parameters = some_predicate_list
            
            
            include_flag = False
            if  (filter['intentions']) and \
                (pred_name in self.domainproblem._INTENTIONALITY_OPERATORS):
                
                include_flag = True
            
            elif (filter['adjacency']) and \
                 (pred_name in self.domainproblem._ADJACENCY_OPERATORS):
                    
                include_flag = True
                
            elif (filter['normal']) and                                                  \
                 (not (pred_name in self.domainproblem._INTENTIONALITY_OPERATORS)) and  \
                 (not (pred_name in self.domainproblem._ADJACENCY_OPERATORS)):
                include_flag = True
            
            if not include_flag:
                continue
                
            new_pred_obj = copy.deepcopy(self.domainproblem.getPredicateObj(pred_name))
            if pred_name in self.domainproblem._INTENTIONALITY_OPERATORS:
                #print("[DEBUG_##>>] Testing")
                #print(pred_parameters)
                #print(new_pred_obj)
                #input()
                
                if pred_parameters[1][1] == pddlglobals._PREDICATE_TYPE:
                    new_pred_obj.instantiateTo(
                                                [   
                                                    pred_parameters[0],
                                                    #[pred_parameters[1],pddlglobals._PREDICATE_TYPE]
                                                    pred_parameters[1]
                                                ], 
                                                domainproblem=self.domainproblem
                                            )
                else:
                    new_pred_obj.instantiateTo(
                                                [   
                                                    pred_parameters[0],
                                                    [pred_parameters[1],pddlglobals._PREDICATE_TYPE]
                                                    #pred_parameters[1]
                                                ], 
                                                domainproblem=self.domainproblem
                                            )
                                          
                #output_paragraph = output_paragraph + new_pred_obj.getRandomHRString() + " "
                output_list.append(new_pred_obj.getRandomHRString())
                
            else:

                if debug:
                    print("========")
                    print("PREDICATE: " + str(some_predicate))
                    print("new_pred_obj (pre instantiation): ")
                    print(new_pred_obj)
                
                new_pred_obj.instantiateTo(copy.deepcopy(pred_parameters))
                #output_paragraph = output_paragraph + new_pred_obj.getRandomHRString() + " "
                output_list.append(new_pred_obj.getRandomHRString())
                
                if debug:
                    print("pred_parameters: " + str(pred_parameters))
                    print("new_pred_obj (post instantiation): ")
                    print(new_pred_obj)
                    print(new_pred_obj.getFunctionString())
                    print("========")
        
            
        for something in sorted(output_list):
            output_paragraph = output_paragraph + something + " "
        return str(output_paragraph)
        
# ==========================================
# Main
# ==========================================

if __name__ == '__main__':
    import sys
    import pprint
    
    #domain = sys.argv[1]
    #problem = sys.argv[2]

    _INPUT_DIR = "./problemdomain/"    
    _INPUT_CATEGORY = "fantasy"
    _INPUT_SERIES = "01"
    
    domain = _INPUT_DIR + _INPUT_CATEGORY + "-domain-" + str(_INPUT_SERIES) + ".pddl"
    problem = _INPUT_DIR + _INPUT_CATEGORY + "-problem-" + str(_INPUT_SERIES) + ".pddl"
    
    
    parser = DomainProblem()
    parser.parseDomain(domain)
    parser.parseProblem(problem)
    
    
    
    #print(' [ DOMAIN Definition ]')
    #print('Domain name:' + parser.domain_name)
    #print('Types:')
    #for type_element in parser.type_list:
        #print(type_element)
    #print('----------------------------')
    #
    #print('Predicates:')
    #for pred in parser.predicates:
        #print(pred)
    #print('----------------------------')

    
    #print('Actions:')
    #for act in parser.actions:
    #    if act.name == "marry":
    #        print(act)
    #print('----------------------------')
    
    #print(' [ PROBLEM Definition ]')
    #print('Problem name: ' + parser.problem_name)
    #print('Objects: ')
    #for obj in parser.objects:
    #    print(obj)
    #print('----------------------------')
    #
    #print('State: ')
    #for predicate in parser.state:
    #    print(predicate)
    #print('----------------------------')
    #
    print('Goals: ' + str(parser.goals))
    print('    All Goals:')
    for goal in parser.goals:
        print(goal)
    print('>>>>')
    print('    Positive:')
    for goal in parser.positive_goals:
        print(goal)
    print('>>>>')
    print('    Negative:')
    for goal in parser.negative_goals:
        print(goal)
    print('----------------------------')
    #
    #print('Evaluation Tests')
    #input = parser.goals
    #print(input)
    #print(parser.evalPropositionTree(input))
    #print('----------------------------')
    #
    #input = parser.state[14]
    #print(input)
    #print(parser.evalPropositionTree(input))
    #print('----------------------------')
    #
    #input = parser.state[13]  
    #print(input)
    #print(parser.evalPropositionTree(input))
    #print('----------------------------')
    #
    #input = ["and",parser.state[13],parser.goals]  
    #print(input)
    #print(parser.evalPropositionTree(input))
    #print('----------------------------')
    #
    #input = ["or",parser.state[4],parser.goals]  
    #print(input)
    #print(parser.evalPropositionTree(input))
    #print('----------------------------')
    