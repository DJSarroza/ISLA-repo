from datetime import datetime
from flask_app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
    

class User(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username    = db.Column(db.String(16), unique=True, nullable=False)
    email       = db.Column(db.String(64), unique=True, nullable=False)
    image_file  = db.Column(db.String(128), nullable=False, default='default.jpg')
    password    = db.Column(db.String(64), nullable=False)
    role        = db.Column(db.String(16), nullable=False, default='BASIC')
    
    def __repr__(self):
        return f"User('{self.username}', {self.email}, {self.image_file})"
        
class UserRoles(db.Model, UserMixin):
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role        = db.Column(db.String(16), nullable=False)
    attribute1  = db.Column(db.String(16), nullable=False)
    attribute2  = db.Column(db.String(16), nullable=False)
    attribute3  = db.Column(db.String(16), nullable=False)
        
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(64), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f"Post('{self.title}', {self.date_posted})"

#==============================================================

class UserActivePlanners(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer)
    narrative_id = db.Column(db.String(32))
    status = db.Column(db.String(16), nullable=False, default="DRAFT")
    date_start = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    date_end = db.Column(db.DateTime)
    
#==============================================================        
class NarrativeInstance(db.Model):
    #id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    narrative_id = db.Column(db.String(32), primary_key=True, nullable=False)
    narrative_label = db.Column(db.String(32))
    
    story_pattern = db.Column(db.String(32))
    user_id = db.Column(db.Integer)
    algorithm = db.Column(db.String(32))
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    map_label   = db.Column(db.String(16), nullable=False)
    
    def __repr__(self):
        return f"NarrativeInstance('{self.narrative_id}', '{self.user_id}' , {self.date_created})"
        
class PlanChapterInstance(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    narrative_instance_id = db.Column(db.String(32))
    
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_address = db.Column(db.String(64), nullable=False)
    chapter_label = db.Column(db.String(64), nullable=False)
    initial_state = db.Column(db.Text)
    final_state = db.Column(db.Text)
    diff1 = db.Column(db.Text)
    diff2 = db.Column(db.Text)
    extra1 = db.Column(db.Text)
    extra2 = db.Column(db.Text)
    extra3 = db.Column(db.Text)
    parent_chapter = db.Column(db.Integer)

    def __repr__(self):
        return f"PlanChapterInstance([{self.id}], '{self.narrative_instance_id}', {self.chapter_address}, {self.chapter_label}, {self.parent_chapter})"
        
class PlanChapterInstanceAction(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    chapter_id = db.Column(db.String(64))
    narrative_instance_id = db.Column(db.String(32))
    
    action_string = db.Column(db.String(64))
    action_string_hr = db.Column(db.Text)
    
    def __repr__(self):
        return f"PlanChapterInstanceAction('{self.chapter_id}', {self.action_string})"
        
class SolutionChapterInstance(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    narrative_instance_id = db.Column(db.String(32))
    
    chapter_number = db.Column(db.Integer, nullable=False)
    chapter_address = db.Column(db.String(64), nullable=False)
    chapter_label = db.Column(db.String(64), nullable=False)
    initial_state = db.Column(db.Text)
    final_state = db.Column(db.Text)
    diff1 = db.Column(db.Text)
    diff2 = db.Column(db.Text)
    extra1 = db.Column(db.Text)
    extra2 = db.Column(db.Text)
    extra3 = db.Column(db.Text)
    parent_chapter = db.Column(db.Integer)
    
    #actions = db.relationship('SolutionChapterInstanceAction', backref='solution_chapter_instance', lazy=True)

    #def __repr__(self):
    #    return f"SolutionChapterInstance([{self.id}], '{self.narrative_instance_id}', {self.chapter_address}, {self.chapter_label}, {self.parent_chapter})"
        
class SolutionChapterInstanceAction(db.Model):
    id = db.Column(db.String(64), primary_key=True)
    chapter_id = db.Column(db.String(64))
    narrative_instance_id = db.Column(db.String(32))
    
    action_string    = db.Column(db.String(64))
    action_string_hr = db.Column(db.Text)
    
    initial_state_hrparagraph = db.Column(db.Text)
    negative_change_hrparagraph = db.Column(db.Text)
    positive_change_hrparagraph = db.Column(db.Text)
    final_state_hrparagraph_all                 = db.Column(db.Text)
    final_state_hrparagraph_norm_only           = db.Column(db.Text)
    final_state_hrparagraph_adjacency_only      = db.Column(db.Text)
    final_state_hrparagraph_intentions_only     = db.Column(db.Text)
    
    final_state_hrparagraph_special1  = db.Column(db.Text)
    final_state_hrparagraph_special2  = db.Column(db.Text)
    final_state_hrparagraph_special3  = db.Column(db.Text)
    final_state_hrparagraph_special4  = db.Column(db.Text)
    
    
    explained_by    = db.Column(db.Text)  # These are LISTS, delimited by semicolon
    explained_by_hr = db.Column(db.Text)  # These are LISTS, delimited by semicolon
    plan_graph_node_label  = db.Column(db.Text) 
    plan_graph_node_parent = db.Column(db.Text)
    roles = db.Column(db.Text)
    goal_graph_soft_plan = db.Column(db.Text)
    reserved1 = db.Column(db.Text)
    reserved2 = db.Column(db.Text)
    reserved3 = db.Column(db.Text)
    
    def __repr__(self):
        return f"SolutionChapterInstanceAction('{self.chapter_id}', {self.action_string})"

class SolutionHRSequence(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_id = db.Column(db.String(64))
    narrative_instance_id = db.Column(db.String(32))
    hrparagraph = db.Column(db.Text)
    explained_by_hr = db.Column(db.Text)
    contributary_hr = db.Column(db.Text)

class NarrativeUserReview(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer)
    narrative_id = db.Column(db.String(32))
    
    # Survey questions
    #   [Narrative Output]
    #   1. Scale of 1-10, how much sense does the narrative have?
    #   2. In your opinion, how much time does an average human need to produce the same narrative?
    #      2.a [Optional] Can you please provide a short explaination?
    #   3. Adjectives to describe the narrative output
    #      3.a [Optional] Can you please provide a short explaination?
    
    #   [Interface / Website]
    #   1. Scale of 1-10, how user-friendly is the site? (forms and displays)
    #   
    
    #   [Suggestions]
    #   1. Which features needs improvement?
    #   2. Which features are lacking?
    #   3. Which features are satisfactory?
    
    part_01_question_01 = db.Column(db.Integer)
    part_01_question_02 = db.Column(db.String(24))
    part_01_question_02a = db.Column(db.Text)
    part_01_question_03 = db.Column(db.Text)
    part_01_question_03a = db.Column(db.Text)
    
    part_02_question_01 = db.Column(db.Integer)
    
    part_03_question_01 = db.Column(db.Text)
    part_03_question_02 = db.Column(db.Text)
    part_03_question_03 = db.Column(db.Text)
    
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class Feedback1(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    user_id = db.Column(db.Integer)
    narrative_id = db.Column(db.String(32))
    question_1 = db.Column(db.Text)
    question_2 = db.Column(db.Text)
    question_3 = db.Column(db.Text)
    question_4 = db.Column(db.Text)
    question_5 = db.Column(db.Text)
    question_6 = db.Column(db.Text)
    question_7 = db.Column(db.Text)
    question_8 = db.Column(db.Text)
    question_9 = db.Column(db.Text)
    question_10 = db.Column(db.Text)
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class TeachingToolSurvey(db.Model):
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    first_name = db.Column(db.Text)
    last_name = db.Column(db.Text)
    email = db.Column(db.Text)
    affiliate_school = db.Column(db.Text)
    subject = db.Column(db.Text)
    number_of_sections = db.Column(db.Text)
    total_number_of_students = db.Column(db.Text)
    
    assessment_question_01 = db.Column(db.Text)
    assessment_question_02 = db.Column(db.Text)
    assessment_question_03 = db.Column(db.Text)
    assessment_question_04 = db.Column(db.Text)
    assessment_question_05 = db.Column(db.Text)
    assessment_question_06 = db.Column(db.Text)
    assessment_question_07 = db.Column(db.Text)
    assessment_question_08 = db.Column(db.Text)
    assessment_question_09 = db.Column(db.Text)
    assessment_question_10 = db.Column(db.Text)
    
    date_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    
class PlanGraphNode(db.Model):
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_id                  = db.Column(db.Text)
    node_label              = db.Column(db.Text, unique=True)
    layer                   = db.Column(db.Integer)
    last_action             = db.Column(db.String(32))
    author_goal_score       = db.Column(db.Text)
    state                   = db.Column(db.Text)
    achieved_author_goals   = db.Column(db.Text)
    reserved_01             = db.Column(db.Text)
    reserved_02             = db.Column(db.Text)
    reserved_03             = db.Column(db.Text)
    reserved_04             = db.Column(db.Text)
    reserved_05             = db.Column(db.Text)
    
class PlanGraphEdge(db.Model):
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    run_id                  = db.Column(db.Text)
    from_node_label         = db.Column(db.Text)
    to_node_label           = db.Column(db.Text)
    
#==============================================================


#==============================================================
class Domains(db.Model):
    id                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category            = db.Column(db.String(16), nullable=False)
    category_str        = db.Column(db.String(16), nullable=False)
    sub_label           = db.Column(db.String(16), nullable=False)
    sub_label_str       = db.Column(db.String(16), nullable=False)
    series              = db.Column(db.String(8), nullable=False)
    domain_full_label   = db.Column(db.String(32), nullable=False, unique=True)
    readable_label      = db.Column(db.String(32), nullable=False)
    author_notes        = db.Column(db.Text)
    visibility          = db.Column(db.String(16), nullable=False)
    created_by          = db.Column(db.String(16), nullable=True)
    last_edited_by      = db.Column(db.String(16), nullable=True)
    status              = db.Column(db.String(16), nullable=False, default="DRAFT")
    date_created        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited         = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class ObjectTypes(db.Model):
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain_id       = db.Column(db.String(16), nullable=False)
    
    object_type     = db.Column(db.String(16), nullable=False)
    parent_type     = db.Column(db.String(16), default="")
    default_flag    = db.Column(db.String(16))
    status          = db.Column(db.String(16), nullable=False, default="DRAFT")
    
class ActorTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain_id = db.Column(db.String(16), nullable=False)
    
    object_type = db.Column(db.String(16), nullable=False)
    default_flag = db.Column(db.String(16))
    status = db.Column(db.String(16), nullable=False, default="DRAFT")

class StatePredicateDef(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain_id = db.Column(db.String(16), nullable=False)
    
    predicate_label = db.Column(db.String(16), nullable=False)
    definition_str = db.Column(db.String(64))
    function_string = db.Column(db.Text, nullable=False)
    
    parameter1_label            = db.Column(db.String(16), nullable=False)
    parameter1_type             = db.Column(db.String(16), nullable=False)
    parameter1_min_instances    = db.Column(db.String(16))
    parameter1_max_instances    = db.Column(db.String(16))
    
    parameter2_label            = db.Column(db.String(16), default = "")
    parameter2_type             = db.Column(db.String(16), default = "")
    parameter2_min_instances    = db.Column(db.String(16), default = "")
    parameter2_max_instances    = db.Column(db.String(16), default = "")
    
    parameter3_label            = db.Column(db.String(16), default = "")
    parameter3_type             = db.Column(db.String(16), default = "")
    parameter3_min_instances    = db.Column(db.String(16), default = "")
    parameter3_max_instances    = db.Column(db.String(16), default = "")
    
    parameter4_label            = db.Column(db.String(16), default = "")
    parameter4_type             = db.Column(db.String(16), default = "")
    parameter4_min_instances    = db.Column(db.String(16), default = "")
    parameter4_max_instances    = db.Column(db.String(16), default = "")
    
    parameter5_label            = db.Column(db.String(16), default = "")
    parameter5_type             = db.Column(db.String(16), default = "")
    parameter5_min_instances    = db.Column(db.String(16), default = "")
    parameter5_max_instances    = db.Column(db.String(16), default = "")
    
    parameter6_label            = db.Column(db.String(16), default = "")
    parameter6_type             = db.Column(db.String(16), default = "")
    parameter6_min_instances    = db.Column(db.String(16), default = "")
    parameter6_max_instances    = db.Column(db.String(16), default = "")
    
    primary_object = db.Column(db.String(16), nullable=True)
    secondary_object = db.Column(db.String(16), nullable=True)
    
    humanreadable_string1 = db.Column(db.Text, default = "")
    humanreadable_string2 = db.Column(db.Text, default = "")
    humanreadable_string3 = db.Column(db.Text, default = "")
    humanreadable_string4 = db.Column(db.Text, default = "")
    
    eval_predicate_pos_criticality = db.Column(db.Integer)
    eval_predicate_neg_criticality = db.Column(db.Integer)
    eval_predicate_abs_criticality = db.Column(db.Integer)
    
    eval_predicate_pos_mutability = db.Column(db.Integer)
    eval_predicate_neg_mutability = db.Column(db.Integer)
    eval_predicate_full_mutability = db.Column(db.Integer)
    
    initial_state_affinity = db.Column(db.Float)
    initial_intention_affinity = db.Column(db.Float)
    
    mutability = db.Column(db.String(16), nullable=True)
    visibility = db.Column(db.String(16), nullable=True)
    
    attribute1 = db.Column(db.String(16), nullable=True)
    attribute2 = db.Column(db.String(16), nullable=True)
    attribute3 = db.Column(db.String(16), nullable=True)
    
    status = db.Column(db.String(16), nullable=False, default="DRAFT")

class ActionDef(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain_id = db.Column(db.String(16), nullable=False)
    
    # Essentially the compound key
    domain_full_label = db.Column(db.String(32), nullable=False)
    action_label = db.Column(db.String(16), nullable=False)
    action_full_label = db.Column(db.String(48), nullable=False, unique=True)
    
    function_str = db.Column(db.Text, nullable=False)
    precondition_str = db.Column(db.Text, nullable=True)
    effect_str = db.Column(db.Text, nullable=True)
    
    agents1_label  = db.Column(db.String(16), default = "")
    agents1_type   = db.Column(db.String(16), default = "")
    agents2_label  = db.Column(db.String(16), default = "")
    agents2_type   = db.Column(db.String(16), default = "")
    agents3_label  = db.Column(db.String(16), default = "")
    agents3_type   = db.Column(db.String(16), default = "")
    agents4_label  = db.Column(db.String(16), default = "")
    agents4_type   = db.Column(db.String(16), default = "")
    
    humanreadable_string1 = db.Column(db.Text, default = "")
    humanreadable_string2 = db.Column(db.Text, default = "")
    humanreadable_string3 = db.Column(db.Text, default = "")
    humanreadable_string4 = db.Column(db.Text, default = "")
    
    eval_action_enabler = db.Column(db.Integer)
    eval_action_disabler = db.Column(db.Integer)
    
    status = db.Column(db.String(16), nullable=False, default="DRAFT")

class Action_Parameters(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_full_label = db.Column(db.String(48), nullable=False)
    parameter_label = db.Column(db.String(16), nullable=False)
    parameter_type  = db.Column(db.String(16), nullable=False)
    parameter_order = db.Column(db.Integer, nullable=False, default=0)
    
class Action_Predicates(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    action_full_label = db.Column(db.String(48), nullable=False)
    type = db.Column(db.String(16),nullable=False)
    predicate_def_id = db.Column(db.Integer)
    predicate_instance_id = db.Column(db.Integer)
    predicate_raw = db.Column(db.Text)
    predicate_function_str = db.Column(db.Text)
    predicate_order = db.Column(db.Integer, nullable=False, default=0)
    
#==============================================================    
class Problems(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain_id = db.Column(db.String(16), nullable=False)
    
class Actions(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
#==============================================================  

class LocationMap(db.Model):
    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    map_label       = db.Column(db.String(16), nullable=False, unique=True)
    readable_label  = db.Column(db.Text, nullable=False)
    domain          = db.Column(db.String(32), nullable=False)
    attribute1      = db.Column(db.String(16))
    attribute2      = db.Column(db.String(16))
    attribute3      = db.Column(db.String(16))
    visibility      = db.Column(db.String(16), nullable=False)
    status          = db.Column(db.String(8), nullable=False)
    notes           = db.Column(db.Text)
    created_by      = db.Column(db.String(16), nullable=False)
    last_edited_by  = db.Column(db.String(16), nullable=False)
    date_created    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class LocationNode(db.Model):
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    map_label   = db.Column(db.String(16), nullable=False)
    node_label  = db.Column(db.String(16), nullable=False)
    readable_label  = db.Column(db.Text, nullable=False)
    node_type   = db.Column(db.String(16), nullable=False)
    description = db.Column(db.Text)
    
class LocationEdges(db.Model):
    id          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    map_label   = db.Column(db.String(16), nullable=False)
    from_node   = db.Column(db.String(16), nullable=False)
    to_node     = db.Column(db.String(16), nullable=False)

#==============================================================  

class StoryPattern(db.Model):
    id             = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grouping_label = db.Column(db.String(32), nullable=False, unique=True)
    readable_label = db.Column(db.String(32), nullable=False, unique=True)

class ChapterPattern(db.Model):
    id                          = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chapter_pattern_cat_label   = db.Column(db.String(16), nullable=True)
    main_label                  = db.Column(db.String(32), nullable=False)
    main_label_str              = db.Column(db.String(32), nullable=False)
    sub_label                   = db.Column(db.String(16), nullable=True)
    sub_label_str               = db.Column(db.String(16), nullable=True)
    name_label_str              = db.Column(db.Text, nullable=False)
    vacant1                     = db.Column(db.String(8), nullable=True)
    vacant2                     = db.Column(db.String(8), nullable=True)
    pattern_sequence            = db.Column(db.String(8), nullable=False)
    sequence_grouping_label     = db.Column(db.String(32), nullable=False)
    series                      = db.Column(db.String(8), nullable=False)
    pattern_full_label          = db.Column(db.Text, nullable=False, unique=True)
    sequence_term_cat_label     = db.Column(db.String(16), nullable=False)
    sequence_term_count         = db.Column(db.Integer, nullable=False)
    sequence_term_min_density   = db.Column(db.Float, nullable=True)
    sequence_term_max_density   = db.Column(db.Float, nullable=True)
    sequence_term_min_count     = db.Column(db.Integer, nullable=True)
    sequence_term_max_count     = db.Column(db.Integer, nullable=True)
    duplicates_allowed          = db.Column(db.String(8), nullable=False)
    vacant3                     = db.Column(db.String(8), nullable=True)
    vacant4                     = db.Column(db.String(8), nullable=True)
    domain                      = db.Column(db.String(32), nullable=True)
    visibility                  = db.Column(db.String(16), nullable=False)
    status                      = db.Column(db.String(8), nullable=False)
    notes                       = db.Column(db.Text, nullable=True)
    created_by                  = db.Column(db.String(16), nullable=False)
    last_edited_by              = db.Column(db.String(16), nullable=False)
    date_created                = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited                 = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class SequenceTerms(db.Model):
    id                                  = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sequence_term_cat_label             = db.Column(db.String(16), nullable=False)
    main_label                          = db.Column(db.String(32), nullable=False)
    main_label_str                      = db.Column(db.String(32), nullable=False)
    sub_label                           = db.Column(db.String(16), nullable=True)
    sub_label_str                       = db.Column(db.String(16), nullable=True)
    name_label_str                      = db.Column(db.String(64), nullable=False)
    term_sequence                       = db.Column(db.String(8), nullable=False)
    term_sequence_grouping_label        = db.Column(db.String(16), nullable=False)
    series                              = db.Column(db.String(16), nullable=False)
    sequence_term_full_label            = db.Column(db.Text, nullable=False, unique=True)
    is_flavor                           = db.Column(db.String(8), nullable=True)
    is_variant                          = db.Column(db.String(8), nullable=True)
    vacant1                             = db.Column(db.String(8), nullable=True)
    main_object                         = db.Column(db.String(16), nullable=False)
    supporting_objects                  = db.Column(db.String(32), nullable=True)
    intention_actor                     = db.Column(db.String(16), nullable=False)
    intention_target_state_predicate    = db.Column(db.String(16), nullable=False)
    intention_full_str                  = db.Column(db.String(64), nullable=False)
    intention_type                      = db.Column(db.String(8), nullable=True)
    predecessor_terms                   = db.Column(db.String(16), nullable=True)
    direct_chained_with                 = db.Column(db.Text, nullable=True)
    successors                          = db.Column(db.Text, nullable=True)
    prerequisite_present_predicates     = db.Column(db.Text, nullable=True)
    prerequisite_target_predicates      = db.Column(db.Text, nullable=True)
    required_objects                    = db.Column(db.Text, nullable=True)
    in_chapter_pattern                  = db.Column(db.Text, nullable=True)
    vacant2                             = db.Column(db.String(8), nullable=True)
    vacant3                             = db.Column(db.String(8), nullable=True)
    status                              = db.Column(db.String(8), nullable=True)
    notes                               = db.Column(db.Text, nullable=True)
    date_created                        = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited                         = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class SequenceTermCategories(db.Model):
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sequence_term_cat_label = db.Column(db.String(16), nullable=False)
    description             = db.Column(db.Text)
    domain                  = db.Column(db.String(32))
    vacant2                 = db.Column(db.String(16))
    vacant3                 = db.Column(db.String(16))
    visibility              = db.Column(db.String(16))
    status                  = db.Column(db.String(16))
    created_by              = db.Column(db.String(16))
    last_edited_by          = db.Column(db.String(16))
    date_created            = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited             = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
class SequenceTermActors(db.Model):
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_name           = db.Column(db.String(16))
    object_type             = db.Column(db.String(16))
    domain                  = db.Column(db.String(32))
    
class SequenceTermObjects(db.Model):
    id                      = db.Column(db.Integer, primary_key=True, autoincrement=True)
    variable_name           = db.Column(db.String(16))
    object_type             = db.Column(db.String(16))
    domain                  = db.Column(db.String(32))
    
class PredicateDescriptors(db.Model):
    id                              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain                          = db.Column(db.String(32), nullable=False)
    main_label                      = db.Column(db.String(32), nullable=False)
    main_label_str                  = db.Column(db.String(32), nullable=False)
    sub_label                       = db.Column(db.String(16), nullable=True)
    sub_label_str                   = db.Column(db.String(16), nullable=True)
    name_label_str                  = db.Column(db.String(64), nullable=False)
    term_sequence                   = db.Column(db.String(8), nullable=False)
    term_sequence_grouping_label    = db.Column(db.String(16), nullable=False)
    parameter_label                 = db.Column(db.String(16), nullable=False)
    parameter_type                  = db.Column(db.String(16), nullable=False)        
    likelihood                      = db.Column(db.Float, nullable=False) 
    min_unique                      = db.Column(db.String(16), nullable=False) 
    max_unique                      = db.Column(db.String(16), nullable=False) 
    duplicates_allowed              = db.Column(db.String(8), nullable=False) 
    notes                           = db.Column(db.Text, nullable=True)
    status                          = db.Column(db.String(16))
    created_by                      = db.Column(db.String(16))
    last_edited_by                  = db.Column(db.String(16))
    date_created                    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited                     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class ObjectNames(db.Model):
    id                              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    domain                          = db.Column(db.String(32), nullable=False)
    main_label                      = db.Column(db.String(32), nullable=False)
    readable_label                  = db.Column(db.String(32), nullable=False)
    object_type                     = db.Column(db.String(16))
    attribute1                      = db.Column(db.String(16))
    attribute2                      = db.Column(db.String(16))
    attribute3                      = db.Column(db.String(16))
    vacant1                         = db.Column(db.String(8), nullable=True)
    vacant2                         = db.Column(db.String(8), nullable=True)
    status                          = db.Column(db.String(16))
    created_by                      = db.Column(db.String(16))
    last_edited_by                  = db.Column(db.String(16))
    date_created                    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_edited                     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    
    
    
#====
# end

    