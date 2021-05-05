

_ALIGNMENT_MID_VALUE = 0
_ALIGNMENT_MAX_VALUE = _ALIGNMENT_MID_VALUE + 100
_ALIGNMENT_MIN_VALUE = _ALIGNMENT_MID_VALUE - 100

_ALIGNMENT_LAWFUL_STR = "Lawful"
_ALIGNMENT_CHAOTIC_STR = "Chaotic"

_ALIGNMENT_GOOD_STR = "Good"
_ALIGNMENT_EVIL_STR = "Evil"

_ALIGNMENT_NEUTRAL_STR = "Neutral"

_NEUTRALITY_THRESHOLD = _ALIGNMENT_MAX_VALUE * 0.3


class Personality:

    #---->>>> [ INITIALIZATION ]
    def __init__(self, 
        alignment="", 
        goal_graph_depth=6, 
        plan_graph_depth=6, 
        nextstepsize=10, 
        nextsteprange=2, 
        solutions_per_goal=1,
        unexplained_threshold=50, 
        author_goal_branching_alloc=50
    ):
    
        #------------>>>> Constants
        
        
        #------------>>>> Attributes (DEFAULTS)
        self.alignment = alignment
        self.goal_graph_depth = goal_graph_depth
        self.plan_graph_depth = plan_graph_depth
        self.nextstepsize = nextstepsize
        self.nextsteprange = nextsteprange
        self.solutions_per_goal = solutions_per_goal
        self.unexplained_threshold = unexplained_threshold
        self.author_goal_branching_alloc = author_goal_branching_alloc
        
        
        #---->>>> Inertia and momentum: dictates change velocity of alignment values
        self.inertia = _ALIGNMENT_MAX_VALUE * 0.01
        #self.momentum = _ALIGNMENT_MAX_VALUE * 0.02
        
        #---->>>> Bias values: dictates if this personality is bias for or against
        #           certain alignments. Affects likelihood of being similar to said
        #           biases
        self.bias_factor = 2
        self.bias_lawfulness_pro = _ALIGNMENT_NEUTRAL_STR
        self.bias_lawfulness_anti = _ALIGNMENT_NEUTRAL_STR

        self.bias_goodness_pro = _ALIGNMENT_NEUTRAL_STR
        self.bias_goodness_anti = _ALIGNMENT_NEUTRAL_STR
    
    #---->>>> [ PRIVATE METHODS ]    
    
    def __isNeutral(self,alignment_val:int):
        if (not self.__isPositive(alignment_val)) and (not self.__isNegative(alignment_val)):
            return True
            
    def __isPositive(self,alignment_val:int):
        if (alignment_val > (_ALIGNMENT_MID_VALUE + _NEUTRALITY_THRESHOLD)):
            return True
        else:
            return False

    def __isNegative(self,alignment_val:int):
        if (alignment_val < (_ALIGNMENT_MID_VALUE - _NEUTRALITY_THRESHOLD)):
            return True
        else:
            return False
            
    #---->>>> [ PUBLIC METHODS ]
    
    def setAlignmentValues(self, lawfulness_val:int, goodness_val:int):
        #---->>>> Error mitigation
        if lawfulness_val > _ALIGNMENT_MAX_VALUE:
            lawfulness_val = _ALIGNMENT_MAX_VALUE
        if lawfulness_val < _ALIGNMENT_MIN_VALUE:
            lawfulness_val = _ALIGNMENT_MIN_VALUE
        if goodness_val > _ALIGNMENT_MAX_VALUE:
            goodness_val = _ALIGNMENT_MAX_VALUE
        if goodness_val < _ALIGNMENT_MIN_VALUE:
            goodness_val = _ALIGNMENT_MIN_VALUE
            
        self.lawfulness_val = lawfulness_val
        self.goodness_val = goodness_val
        self.setAlignmentString()
        
    def setAlignmentString(self):
        if self.__isNeutral(self.lawfulness_val):
            self.lawfulness_str = _ALIGNMENT_NEUTRAL_STR
        elif self.__isPositive(self.lawfulness_val):
            self.lawfulness_str = _ALIGNMENT_LAWFUL_STR
        else:
            self.lawfulness_str = _ALIGNMENT_CHAOTIC_STR

            
        if self.__isNeutral(self.goodness_val):
            self.goodness_str = _ALIGNMENT_NEUTRAL_STR
        elif self.__isPositive(self.goodness_val):
            self.goodness_str = _ALIGNMENT_GOOD_STR
        else:
            self.goodness_str = _ALIGNMENT_EVIL_STR
        
        self.alignment = self.lawfulness_str + " " + self.goodness_str
        