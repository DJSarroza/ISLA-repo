import secrets
import os
import re
import logging
import utility
import ast
import pddlglobals
import copy

from sqlalchemy import func

from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flask_app import app, db, bcrypt
from flask_app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, GenerateStoryForm
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
                                ObjectNames,                    \
                                PredicateDescriptors,           \
                                PlanGraphNode,                  \
                                PlanGraphEdge,                  \
                                Feedback1,                      \
                                TeachingToolSurvey
                                

                                 
from flask_login import login_user, current_user, logout_user, login_required
from sqlalchemy import or_
 
#==================================================================================
# CONSTANTS
_LOCATION_DIR = "./domainproblem/locations/"
 
#==================================================================================
# FUNCTIONS
def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path =os.path.join(app.root_path, 'static/profile_pics',picture_fn)
     
    output_size = (125,125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
     
    i.save(picture_path)
     
    return picture_fn

    
def parsePossibleEffects(predicate_type, input_effect_list, pos_effects:list, neg_effects:list):
    
    if predicate_type == "forall":
        raw_effect = input_effect_list[5]
    if predicate_type == "when":
        raw_effect = input_effect_list[3]
    
    if raw_effect[0] == pddlglobals._AND_OPERATOR:
        for some_effect in raw_effect[1]:
            if some_effect[0] == pddlglobals._NOT_OPERATOR:
                neg_effects.append(str(some_effect))
            else:
                pos_effects.append(str(some_effect))
    elif raw_effect[0] == pddlglobals._NOT_OPERATOR:
        neg_effects.append(str(raw_effect))
    else:
        pos_effects.append(str(raw_effect))
    
def evaluate_domain(domain_id):
    
    has_predicates = False
    has_actions = False
    
    # PREDICATES
    all_predicates = db.session.query(StatePredicateDef) \
                        .filter(StatePredicateDef.domain_id == domain_id) \
                        .all()
    
    all_actions = db.session.query(ActionDef) \
                        .filter(ActionDef.domain_id == domain_id) \
                        .all()
    
    for some_predicate in all_predicates:
    
        has_predicates = True
        
        predicate_label = some_predicate.predicate_label
        test_str = "['"+predicate_label+"'"
        
        predicate_pos_criticality = 0
        predicate_neg_criticality = 0
        predicate_abs_criticality = 0
        
        predicate_pos_mutability = 0
        predicate_neg_mutability = 0
        predicate_full_mutability = 0
        
        for some_action in all_actions:
            
            # > Criticality
            # ['not', ['issick'
            positive_preconditions = db.session.query(Action_Predicates) \
                                        .filter(Action_Predicates.action_full_label == some_action.action_full_label) \
                                        .filter(Action_Predicates.type == "POS_PRECON") \
                                        .all()
            
            negative_preconditions = db.session.query(Action_Predicates) \
                                        .filter(Action_Predicates.action_full_label == some_action.action_full_label) \
                                        .filter(Action_Predicates.type == "NEG_PRECON") \
                                        .all()
            
            # >> Positive criticality
            for some_precon in positive_preconditions:
                if test_str in some_precon.predicate_raw:
                    predicate_pos_criticality += 1
                    predicate_abs_criticality += 1
            
            # >> Negative criticality
            for some_precon in negative_preconditions:
                if test_str in some_precon.predicate_raw:
                    predicate_neg_criticality += 1
                    predicate_abs_criticality += 1
            
            # > Mutability
            all_effects = db.session.query(Action_Predicates) \
                            .filter(Action_Predicates.action_full_label == some_action.action_full_label) \
                            .filter(Action_Predicates.type == "SOME_EFFECT") \
                            .all()
                            
            for some_effect in all_effects:
                effect_list = ast.literal_eval(some_effect.predicate_raw)
                
                
                # >> Positive
                if effect_list[0] == predicate_label:
                    predicate_pos_mutability += 1
                    
                # >> Negative
                if effect_list[0] == pddlglobals._NOT_OPERATOR:
                    if effect_list[1][0] == predicate_label:
                        predicate_neg_mutability += 1
                        
                # >> For-All
                if effect_list[0] == pddlglobals._FORALL_OPERATOR:
                
                    forall_precon = effect_list[3]
                    forall_effect = effect_list[5]
                    
                    #print(forall_precon_raw)
                    #forall_precon = ast.literal_eval(forall_precon_raw)
                    #forall_effect = ast.literal_eval(forall_effect_raw)
                    
                    #===========
                    if forall_precon[0] == pddlglobals._NOT_OPERATOR:
                        if forall_precon[1][0] == predicate_label:
                            predicate_neg_criticality += 1
                    elif forall_precon[0] == predicate_label:
                        predicate_pos_criticality += 1
                    
                    #===========
                    if forall_effect[0] == pddlglobals._AND_OPERATOR:
                        for some_forall_effect in forall_effect[1]:
                            if some_forall_effect[0] == pddlglobals._NOT_OPERATOR:
                                if some_forall_effect[1][0] == predicate_label:
                                    predicate_neg_mutability += 1
                            elif some_forall_effect[0] == predicate_label:
                                predicate_pos_mutability += 1
                                
                    elif forall_effect[0] == pddlglobals._NOT_OPERATOR:
                        if forall_effect[1][0] == predicate_label:
                            predicate_neg_mutability += 1
                            
                    elif forall_effect[0] == predicate_label:
                        predicate_pos_mutability += 1
                
                # >> When-Then
                if effect_list[0] == pddlglobals._WHEN_OPERATOR:
                    when_precon = effect_list[1]
                    when_effect = effect_list[3]
                    
                    #===========
                    if when_precon[0] == pddlglobals._NOT_OPERATOR:
                        if when_precon[1][0] == predicate_label:
                            predicate_neg_criticality += 1
                    elif when_precon[0] == predicate_label:
                        predicate_pos_criticality += 1
                        
                    #===========
                    if when_effect[0] == pddlglobals._AND_OPERATOR:
                        for some_forall_effect in when_effect[1]:
                            if some_forall_effect[0] == pddlglobals._NOT_OPERATOR:
                                if some_forall_effect[1][0] == predicate_label:
                                    predicate_neg_mutability += 1
                            elif some_forall_effect[0] == predicate_label:
                                predicate_pos_mutability += 1
                                
                    elif when_effect[0] == pddlglobals._NOT_OPERATOR:
                        if when_effect[1][0] == predicate_label:
                            predicate_neg_mutability += 1
                            
                    elif when_effect[0] == predicate_label:
                        predicate_pos_mutability += 1
        print("---------------------------------------")
        print("Predicate: " + predicate_label)
        print("\tpredicate_pos_criticality :" + str(predicate_pos_criticality))
        print("\tpredicate_neg_criticality :" + str(predicate_neg_criticality))
        print("\tpredicate_abs_criticality :" + str(predicate_abs_criticality))
        print("\tpredicate_pos_mutability  :" + str(predicate_pos_mutability))
        print("\tpredicate_neg_mutability  :" + str(predicate_neg_mutability))
        print("\tpredicate_full_mutability :" + str(predicate_full_mutability))
        
        some_predicate.eval_predicate_pos_criticality = predicate_pos_criticality
        some_predicate.eval_predicate_neg_criticality = predicate_neg_criticality
        some_predicate.eval_predicate_abs_criticality = predicate_abs_criticality
        some_predicate.eval_predicate_pos_mutability  = predicate_pos_mutability
        some_predicate.eval_predicate_neg_mutability  = predicate_neg_mutability
        some_predicate.eval_predicate_full_mutability = predicate_full_mutability
        db.session.commit()
    
    # ACTIONS
    all_actions = db.session.query(ActionDef) \
                        .filter(ActionDef.domain_id == domain_id) \
                        .all()
                        
    for action_A in all_actions:
        has_actions = True
        
        action_A_all_effects = db.session.query(Action_Predicates) \
            .filter(Action_Predicates.type == "SOME_EFFECT") \
            .filter(Action_Predicates.action_full_label == action_A.action_full_label) \
            .all()
        
        enabler_score = 0
        disabler_score = 0
        print("---------------------------------------")
        print("Action: " + action_A.action_full_label)
        
        for action_B in all_actions:
            
            action_B_pos_precons = db.session.query(Action_Predicates) \
                .filter(Action_Predicates.type == "POS_PRECON") \
                .filter(Action_Predicates.action_full_label == action_B.action_full_label) \
                .all()
                
            action_B_neg_precons = db.session.query(Action_Predicates) \
                .filter(Action_Predicates.type == "NEG_PRECON") \
                .filter(Action_Predicates.action_full_label == action_B.action_full_label) \
                .all()
            
            for some_action_A_all_effect in action_A_all_effects:
                
                some_action_A_effect = ast.literal_eval(some_action_A_all_effect.predicate_raw)
                
                #   FORALL
                if some_action_A_effect[0] == pddlglobals._FORALL_OPERATOR:
                    
                    pos_effects = []
                    neg_effects = []
                    
                    parsePossibleEffects("forall", some_action_A_effect, pos_effects, neg_effects)
                    
                    for some_effect in pos_effects:
                        predicate_label = some_effect[0]
                        test_str = "['"+predicate_label+"'"
                        for some_precon in action_B_pos_precons:
                            if test_str in some_precon.predicate_raw:
                                enabler_score += 1
                        
                        for some_precon in action_B_neg_precons:
                            if test_str in some_precon.predicate_raw:
                                disabler_score += 1
                    
                    for some_effect in neg_effects:
                        predicate_label = some_effect[0]
                        test_str = "['not', '"+predicate_label+"'"
                        for some_precon in action_B_neg_precons:
                            if test_str in some_precon.predicate_raw:
                                enabler_score += 1
                        
                        for some_precon in action_B_pos_precons:
                            if test_str in some_precon.predicate_raw:
                                disabler_score += 1
                    
                #   WHEN
                elif some_action_A_effect[0] == pddlglobals._WHEN_OPERATOR:
                    
                    pos_effects = []
                    neg_effects = []
                    
                    parsePossibleEffects("when", some_action_A_effect, pos_effects, neg_effects)
                    
                    for some_effect in pos_effects:
                        predicate_label = some_effect[0]
                        test_str = "['"+predicate_label+"'"
                        for some_precon in action_B_pos_precons:
                            if test_str in some_precon.predicate_raw:
                                enabler_score += 1
                        
                        for some_precon in action_B_neg_precons:
                            if test_str in some_precon.predicate_raw:
                                disabler_score += 1
                    
                    for some_effect in neg_effects:
                        predicate_label = some_effect[0]
                        test_str = "['not', '"+predicate_label+"'"
                        for some_precon in action_B_neg_precons:
                            if test_str in some_precon.predicate_raw:
                                enabler_score += 1
                        
                        for some_precon in action_B_pos_precons:
                            if test_str in some_precon.predicate_raw:
                                disabler_score += 1
            
                #   NOT
                elif some_action_A_effect[0] == pddlglobals._NOT_OPERATOR:
                    predicate_label = some_action_A_effect[1][0]
                    test_str = "['not', ['"+predicate_label+"'"
                    #print("TEST: " + action_B.action_full_label + " - " + test_str)
                    #print("---")
                    for some_precon in action_B_neg_precons:
                        
                        if test_str in some_precon.predicate_raw:
                            #print(some_precon.predicate_raw + ": HIT!")
                            enabler_score += 1
                    
                    for some_precon in action_B_pos_precons:
                        if test_str in some_precon.predicate_raw:
                            #print(some_precon.predicate_raw + ": HIT!")
                            disabler_score += 1
                
                #   ALL OTHERS
                else:                
                    predicate_label = some_action_A_effect[0]
                    test_str = "['"+predicate_label+"'"
                    #print("TEST: " + action_B.action_full_label + " - " + test_str)
                    #print("---")
                    for some_precon in action_B_pos_precons:
                        #print(some_precon.predicate_raw)
                        if test_str in some_precon.predicate_raw:
                            enabler_score += 1
                    
                    for some_precon in action_B_neg_precons:
                        #print(some_precon.predicate_raw)
                        if test_str in some_precon.predicate_raw:
                            disabler_score += 1
                
                

        print("\teval_action_enabler :" + str(enabler_score))
        print("\teval_action_disabler :" + str(disabler_score))
        
        action_A.eval_action_enabler = enabler_score
        action_A.eval_action_disabler = disabler_score
        db.session.commit()
    
#==================================================================================
@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(Post.date_posted.desc()).all()
    return render_template('home.html',title='Home Page',posts=posts)
 
 
@app.route("/about")
def about():
    return render_template('about.html',title='About ISLA.online')
     
#==================================================================================
@app.route("/register", methods=['GET','POST'])
def register():
    #if current_user.is_authenticated:
    #    flash(f'Attempting to register.', 'info')
    #    return redirect(url_for('home'))
         
    form = RegistrationForm()
     
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(    username=form.username.data,
                        email=form.email.data,
                        password=hashed_password
                    )
        db.session.add(user) 
        db.session.commit()
         
        flash(f'Your account has been created.', 'success')
        return redirect(url_for('login'))
         
    else:
        #flash(f'Registration Unsuccessful.','danger')
        pass
         
    return render_template('register.html', title='Register', form=form)
 
#==================================================================================
@app.route("/login", methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        flash(f'You are already logged-in.', 'info')
        return redirect(url_for('home'))
         
    form = LoginForm()
     
    if form.validate_on_submit():
     
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f'Login Successful','success')
            next_page = request.args.get('next')
             
            if next_page:
                return redirect(next_page)
            else:
                return redirect(url_for('home'))
        else:
            flash(f'Login Unsuccessful. Please check username and/or password','danger')
    return render_template('login.html', title='Login', form=form)
     
#==================================================================================
@app.route("/logout")
def logout():
    logout_user()
    flash(f'Logout Successful','success')
    return redirect(url_for('home'))
     
#==================================================================================
@app.route("/account", methods=['GET','POST'])
@login_required
def account():
 
    #posts = Post.query.order_by(Post.date_posted.desc()).all()
    #return render_template('home.html',title='Home Page',posts=posts)
 
    form = UpdateAccountForm()
     
    if form.validate_on_submit():
        if form.picture.data:
            picture_filename = save_picture(form.picture.data)
            current_user.image_file = picture_filename
             
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash(f'Your account has been updated','success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
         
    profile_image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    #narratives = NarrativeInstance.query.order_by(NarrativeInstance.date_created.desc()).filter_by(user_id=current_user.username)
    #narratives = NarrativeInstance.query.join(UserActivePlanners).order_by(NarrativeInstance.date_created.desc()).filter(NarrativeInstance.user_id==current_user.username)
     
    #narratives = db.session.query(NarrativeInstance).join(UserActivePlanners).all()
    #narratives = db.session.query(UserActivePlanners).join(NarrativeInstance).all()
     
    narratives = db.session.query(NarrativeInstance, UserActivePlanners).order_by(NarrativeInstance.date_created.desc()).filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id).filter(NarrativeInstance.user_id == current_user.username).all()
     
     
    return render_template('account.html', 
        title='Account Information', 
        profile_image_file=profile_image_file, 
        form=form, 
        narratives=narratives
    )
     
#==================================================================================
@app.route("/narrative_instance/<narrative_instance_id>")
def narrative_instance(narrative_instance_id):
     
    narrative_instance = NarrativeInstance.query.get_or_404(narrative_instance_id)
    chapter_instance = SolutionChapterInstance.query.order_by(SolutionChapterInstance.id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    chapter_instance_actions = SolutionChapterInstanceAction.query.order_by(SolutionChapterInstanceAction.chapter_id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    hrsequence = SolutionHRSequence.query.order_by(SolutionHRSequence.chapter_id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    
    narrative_instance_summary = db.session.query(ChapterPattern) \
        .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance.story_pattern)) \
        .filter(ChapterPattern.vacant1 is not None) \
        .first()
    
    plan_chapter_instances = db.session.query(PlanChapterInstance) \
        .filter(PlanChapterInstance.narrative_instance_id == narrative_instance_id) \
        .order_by(PlanChapterInstance.chapter_number) \
        .order_by(PlanChapterInstance.chapter_address) \
        .all()
    
    
    return render_template('narrative_instance.html', 
        narrative_instance=narrative_instance, 
        narrative_instance_id = narrative_instance_id,
        narrative_instance_summary=narrative_instance_summary,
        chapter_instance=chapter_instance, 
        chapter_instance_actions=chapter_instance_actions,
        hrsequence=hrsequence,
        plan_chapter_instances=plan_chapter_instances
    )
 

@app.route("/tellability_test")
def tellability_test():
     
    #narrative_instance = NarrativeInstance.query.get_or_404(narrative_instance_id)
    #chapter_instance = SolutionChapterInstance.query.order_by(SolutionChapterInstance.id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    #chapter_instance_actions = SolutionChapterInstanceAction.query.order_by(SolutionChapterInstanceAction.chapter_id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    #hrsequence = SolutionHRSequence.query.order_by(SolutionHRSequence.chapter_id.asc()).filter_by(narrative_instance_id=narrative_instance_id)
    
    
    
    #narratives = db.session.query(NarrativeInstance, ChapterPattern, UserActivePlanners) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .filter(ChapterPattern.vacant1 != "") \
    #    .filter(ChapterPattern.domain.like(str(filter_parameter_domain) + "%"))    \
    #    .filter(NarrativeInstance.narrative_id.like(UserActivePlanners.narrative_id) + "%") \
    #    .filter(UserActivePlanners.status == "SUCCESS") \
    #    .order_by(func.random())                                        \
    #    .all()
    
    bulk = db.session.query(NarrativeInstance, SolutionChapterInstanceAction) \
        .filter(NarrativeInstance.narrative_id == SolutionChapterInstanceAction.narrative_instance_id) \
        .all()
    
    #narrative_instance_summary = db.session.query(ChapterPattern) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .first()
    #
    #plan_chapter_instances = db.session.query(PlanChapterInstance) \
    #    .filter(PlanChapterInstance.narrative_instance_id == narrative_instance_id) \
    #    .order_by(PlanChapterInstance.chapter_number) \
    #    .order_by(PlanChapterInstance.chapter_address) \
    #    .all()
    
    
    return render_template('tellability_test.html', 
        bulk=bulk
    )
 

     
#==================================================================================
@app.route("/post/new", methods=['GET','POST'])
@login_required
def new_post():
     
    form = PostForm()
     
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
         
        flash(f'Post Created','success')
        return redirect(url_for('home'))
    else:
        pass
    return render_template('create_post.html', title='New Post', form=form, legend='New Post')
     
#==================================================================================
@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post.html', title=post.title, post=post)
 
#==================================================================================
@app.route("/post/<int:post_id>/update", methods=['GET','POST'])
@login_required
def update_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
     
    form = PostForm()
     
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash(f'Your post has been updated.','success')
        return redirect(url_for('post', post_id=post.id))
         
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
         
    return render_template('create_post.html', title='Update Post', form=form, legend='Update Post')
     
#==================================================================================
@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
 
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
         
    db.session.delete(post)
    db.session.commit()
     
    flash(f'Your post has been deleted.','success')
     
    return redirect(url_for('home'))
     
     
#==================================================================================
#   DOMAIN stuff
#==================================================================================
 
@app.route("/domains", methods=['GET','POST'])
def domains():
     
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
     
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    return render_template('domains.html', title='Domains',
        loadable_domains  = loadable_domains
    )

@app.route("/_generate_domain_file")
def generate_domain_file():
    
    def convertToRawString(raw_str, level=4):
        
        def listToString(process_list, level,newline=True):
            #====
            padding = ""
            for ctr in range(0,level):
                padding = padding + "\t"
            #====
            output_str = ""
            
            # ==== [ AND
            if (process_list[0] == pddlglobals._AND_OPERATOR):
                head = process_list.pop(0)
                process_list = process_list[0]
                
                output_str += padding + "(and\n"
                for some_elem in process_list:
                    new_output_str = listToString(some_elem, level+1)
                    output_str += new_output_str 
                output_str += padding + ")\n"
            # ==== [ OR
            elif (process_list[0] == pddlglobals._OR_OPERATOR):
                head = process_list.pop(0)
                process_list = process_list[0]
                
                output_str += padding + "(or\n"
                for some_elem in process_list:
                    new_output_str = listToString(some_elem, level+1)
                    output_str += new_output_str 
                output_str += padding + ")\n"
            # ==== [ NOT
            elif process_list[0] == pddlglobals._NOT_OPERATOR:
                head = process_list.pop(0)
                process_list = process_list[0]
                output_str += padding + "(not "+listToString(process_list,0,False)+")\n"
            # ==== [ INTENTION
            elif process_list[0] in pddlglobals._INTENTIONALITY_OPERATORS:
                output_str += padding + "(intends "+process_list[1][0]+" "+listToString(process_list[2][0],0,False)+" )\n"
            # ==== [ TRUE
            elif process_list[0] == [[pddlglobals._TRUE]]:
                output_str += padding + "((true))\n"
            # ==== [ FORALL
            elif process_list[0] == pddlglobals._FORALL_OPERATOR:

                _f1 = process_list.pop(0)
                _f2 = process_list.pop(0)
                
                output_str += padding + "(forall\n"
                output_str += padding + "\t("+_f2[0]+" - "+_f2[1]+")\n"
               
                output_str += listToString(process_list,level+2,True)
                
                output_str += padding + ")\n"
            # ==== [ WHEN-THEN
            elif process_list[0] == pddlglobals._WHEN_OPERATOR:

                output_str += padding + "(when\n"
                output_str += listToString(process_list[1],level+1,True)
                output_str += padding + "then\n"
                output_str += listToString(process_list[3],level+1,True)
                
                output_str += padding + ")\n"
                
            # ==== [ NORMAL PREDICATE
            else:
                #print(process_list)
                head = process_list.pop(0)
                print(head)
                output_str += padding + "(" + head
                
                for some_elem in process_list:
                    output_str += " " + some_elem[0]
                output_str += ")"
                if newline:
                    output_str += "\n"
                
            return output_str
            
        #===============================
        
        output_string = ""
        raw_list = ast.literal_eval(raw_str)
        process_list = copy.deepcopy(raw_list)
        output_string = listToString(process_list,level)
        
        return(output_string)
    
    #===============================================================
    
    domain_id = request.args.get('domain_id', None, type=str)
    result_str = ""
    
    #print(domain_id)
    domain_result = db.session.query(Domains) \
                            .filter(Domains.id == domain_id) \
                            .first()
    
    define_str = domain_result.category_str + domain_result.series
    
    # Output stuff
    domain_filename = "./domainproblem/"+domain_result.domain_full_label+".pddl"
    output_string = ""
    domain_file = open(domain_filename, "w")
    
    # > Start
    output_string += "(define (domain "+define_str+")\n"
    #==================
    # >> Types 
    types_result = db.session.query(ObjectTypes) \
                        .filter(ObjectTypes.domain_id == domain_result.id) \
                        .all()
    output_string += "\t(:types \n"
    for sometype in types_result:
        if (sometype.parent_type is None) or (sometype.parent_type == ""):
            output_string += "\t\t"+sometype.object_type+"\n"
        else:
            output_string += "\t\t("+sometype.object_type+" "+sometype.parent_type+")\n"
    output_string += "\t)\n\n"
    #==================
    # >> Actors
    actors_result = db.session.query(ActorTypes) \
                        .filter(ActorTypes.domain_id == domain_result.id) \
                        .all()
    output_string += "\t(:actors\n"
    for someactor in actors_result:
        output_string += "\t\t"+someactor.object_type+"\n"
    output_string += "\t)\n\n"
    
    #==================
    # >> Predicates
    predicates_result = db.session.query(StatePredicateDef) \
                        .filter(StatePredicateDef.domain_id == domain_result.id) \
                        .all()
    output_string += "\t(:predicates\n"
    for somepredicate in predicates_result:
        output_string += "\t\t(:predicate "+somepredicate.predicate_label+"\n"
        
        # >>> Parameters
        
        output_string += "\t\t\t:parameters     ("
        param_body = ""
        extra_space = ""
        # >>>> P1
        if(somepredicate.parameter1_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter1_label+" - "+somepredicate.parameter1_type+")"
            extra_space = " "
        # >>>> P2
        if(somepredicate.parameter2_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter2_label+" - "+somepredicate.parameter2_type+")"
            extra_space = " "
        # >>>> P3
        if(somepredicate.parameter3_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter3_label+" - "+somepredicate.parameter3_type+")"
            extra_space = " "
        # >>>> P4
        if(somepredicate.parameter4_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter4_label+" - "+somepredicate.parameter4_type+")"
            extra_space = " "
        # >>>> P5
        if(somepredicate.parameter5_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter5_label+" - "+somepredicate.parameter5_type+")"
            extra_space = " "
        # >>>> P6
        if(somepredicate.parameter6_label != ""):
            param_body = param_body + extra_space + "("+somepredicate.parameter6_label+" - "+somepredicate.parameter6_type+")"
            extra_space = " "
        
        output_string += param_body + ")\n"
        # >>> Definition
        output_string += "\t\t\t:definition     ("
        output_string += somepredicate.predicate_label + " " + param_body
        output_string += ")\n"
        
        
        # >>> Primary Object
        print(somepredicate.primary_object)
        primary_obj_raw = ast.literal_eval(somepredicate.primary_object)
        primary_obj_str = ""
        for something in primary_obj_raw:
            #print(str(something) + ":" + str(type(something)))
            primary_obj_str = primary_obj_str + "("+something[0]+" - "+something[1]+")"
        
        output_string += "\t\t\t:primary_obj    ("+primary_obj_str+")\n"
        
        
        # >>> Human Readable Strings
        
        output_string += "\t\t\t:humanreadable  (\n"
        
        # >>>> String 1
        if somepredicate.humanreadable_string1 != "":
            output_string += "\t\t\t\t("+somepredicate.humanreadable_string1+")\n"
        
        # >>>> String 2
        if somepredicate.humanreadable_string2 != "":
            output_string += "\t\t\t\t("+somepredicate.humanreadable_string2+")\n"
        
        # >>>> String 3
        if somepredicate.humanreadable_string3 != "":
            output_string += "\t\t\t\t("+somepredicate.humanreadable_string3+")\n"
        
        # >>>> String 4
        if somepredicate.humanreadable_string4 != "":
            output_string += "\t\t\t\t("+somepredicate.humanreadable_string4+")\n"
        
        output_string += "\t\t\t)\n"
        
        output_string += "\t\t)\n"
        output_string += "\n"
    output_string += "\t)\n\n"
    #==================   
    # >> Actions
    actions_result = db.session.query(ActionDef) \
                        .filter(ActionDef.domain_id == domain_result.id) \
                        .all()
    #output_string += "\t(:actions\n"
    for someaction in actions_result:
        print("ACTION: " + someaction.action_label)
        output_string += "\t\t(:action "+someaction.action_label+"\n"
        
        # >>> Parameters
        parameters_result = db.session.query(Action_Parameters) \
                                .filter(Action_Parameters.action_full_label == someaction.action_full_label) \
                                .order_by(Action_Parameters.parameter_order.asc()) \
                                .all()
                                
        output_string += "\t\t\t:parameters     ("
        
        param_body = ""
        extra_space = ""
        for someparam in parameters_result:
            param_body = param_body + extra_space + "("+someparam.parameter_label+" - "+someparam.parameter_type+")"
            extra_space = " "
        output_string += param_body + ")\n"
        
        
        # >>> Precondition
        output_string += "\t\t\t:precondition\n"
        result_string = convertToRawString(someaction.precondition_str,8)
        output_string += result_string + "\n"
        
        # >>> Effect
        output_string += "\t\t\t:effect\n"
        result_string = convertToRawString(someaction.effect_str,8)
        output_string += result_string + "\n"
        
        # >>> Agents
        
        agents_body = ""
        extra_space = ""
        if str(someaction.agents1_label) != "":
            agents_body += extra_space + "("+someaction.agents1_label+")"
            extra_space = " "
        if str(someaction.agents2_label) != "":
            agents_body += extra_space + "("+someaction.agents2_label+")"
            extra_space = " "
        if str(someaction.agents3_label) != "":
            agents_body += extra_space + "("+someaction.agents3_label+")"
            extra_space = " "
        if str(someaction.agents4_label) != "":
            agents_body += extra_space + "("+someaction.agents4_label+")"
            extra_space = " "
            
        if agents_body != "":
            output_string += "\t\t\t:agents         ("
            output_string += agents_body
            output_string += ")\n"
        
        
        # >>> Human Readable Strings
        
        humanreadable_body =""
        if someaction.humanreadable_string1 != "":
            humanreadable_body += "\t\t\t\t" + "("+someaction.humanreadable_string1+")\n"
        if someaction.humanreadable_string2 != "":
            humanreadable_body += "\t\t\t\t" + "("+someaction.humanreadable_string2+")\n"
        if someaction.humanreadable_string3 != "":
            humanreadable_body += "\t\t\t\t" + "("+someaction.humanreadable_string3+")\n"
        if someaction.humanreadable_string4 != "":
            humanreadable_body += "\t\t\t\t" + "("+someaction.humanreadable_string4+")\n"
            
        if humanreadable_body != "":
            output_string += "\t\t\t:humanreadable  (\n"
            output_string += humanreadable_body
            output_string += "\t\t\t)\n"
        
        # >>> End of Actions
        output_string += "\t\t)\n"
        
    #output_string += "\t)\n"
    #==================
        
    # > Finalize
    output_string += ")\n"
    domain_file.write(output_string)
    
    # > Evaluate Domain
    
    evaluate_domain(domain_id)
    
    #flash(f'Successfully created domain file: '+domain_filename,'success')
    return jsonify(result='Successfully created domain file: '+domain_filename+'/;success')
    
#==================================================================================
 
@app.route("/create_domain", methods=['GET','POST'])
def create_domain(copy_from=""):
     
    #id = db.Column(db.Integer, primary_key=True)
    #category = db.Column(db.String(16), nullable=False)
    #series = db.Column(db.String(8), nullable=False)
    #readable_label = db.Column(db.String(32), nullable=False, unique=True)
    #created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    #last_edited_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    #status = db.Column(db.String(16), nullable=False, default="ACTIVE")
     
     
    if current_user.is_authenticated:
        created_by = current_user.username
        last_edited_by = current_user.username
    else:
        created_by = 'anonymous'
        last_edited_by = 'anonymous'
     
    
    domain_sequence_num = db.session.query(db.func.max(Domains.series)) \
                            .first()
                            
    
    # [TODO] Data should come from source page modal
    # [TODO] Deal with user-category-series unique combination?
    
    category="Custom"
    category_str="custom"
    sub_label="Draft"
    sub_label_str="draft"
    series = utility.zeroStringPad(str((int(domain_sequence_num[0]) + 1)),2)
    
    new_domain = Domains(
                    category            = category       ,
                    category_str        = category_str   ,
                    sub_label           = sub_label      ,
                    sub_label_str       = sub_label_str  ,
                    series              = series         ,
                    domain_full_label   = category_str+"_"+sub_label_str+"_"+series,
                    author_notes        = "",
                    visibility          = "PRIVATE-WRITE",
                    readable_label      = "New Custom Domain",
                    created_by          = created_by,
                    last_edited_by      = last_edited_by,
                    status              ="DRAFT"
                    )
    db.session.add(new_domain)
    db.session.commit()
     
    #==========================
    # Default objects
    new_objtype = ObjectTypes(
                    domain_id   = new_domain.id,
                    object_type = "object",
                    parent_type = "",
                    default_flag = "default"
                    )
    db.session.add(new_objtype)
    new_objtype = ObjectTypes(
                    domain_id   = new_domain.id,
                    object_type = "predicate",
                    parent_type = "",
                    default_flag = "default"
                    )
    db.session.add(new_objtype)
    new_objtype = ObjectTypes(
                    domain_id   = new_domain.id,
                    object_type = "actor",
                    parent_type = "object",
                    default_flag = "default"
                    )
    db.session.add(new_objtype)
    new_objtype = ObjectTypes(
                    domain_id   = new_domain.id,
                    object_type = "admin",
                    parent_type = "actor",
                    default_flag = "default"
                    )
    db.session.add(new_objtype)
    #new_objtype = ObjectTypes(
    #                domain_id   = new_domain.id,
    #                object_type = "creature",
    #                parent_type = "actor",
    #                default_flag = "default"
    #                )
    #db.session.add(new_objtype)
    #new_objtype = ObjectTypes(
    #                domain_id   = new_domain.id,
    #                object_type = "item",
    #                parent_type = "object",
    #                default_flag = "default"
    #                )
    #db.session.add(new_objtype)
    new_objtype = ObjectTypes(
                    domain_id   = new_domain.id,
                    object_type = "location",
                    parent_type = "",
                    default_flag = "default"
                    )
    db.session.add(new_objtype)
    
    
    #==========================
    # Default actors
    new_actor = ActorTypes(
                    domain_id   = new_domain.id,
                    object_type = "actor",
                    default_flag = "default"
                    )
    db.session.add(new_actor)
    new_actor = ActorTypes(
                    domain_id   = new_domain.id,
                    object_type = "admin",
                    default_flag = "default"
                    )
    db.session.add(new_actor)
    db.session.commit()
    
    #==========================
    # Default predicates
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                   ,
        predicate_label         = "intends"                                                       ,
        definition_str          = "['intends', ['?actor', 'actor'], ['?intention', 'predicate']]" ,
        function_string         = "intends(?actor, ?intention)"                                   ,
        parameter1_label        = "?actor"                                                        ,
        parameter1_type         = "actor"                                                         ,
        parameter2_label        = "?intention"                                                    ,
        parameter2_type         = "predicate"                                                     ,
        primary_object          = "[['?actor', 'actor']]"                                         ,
        secondary_object        = "[]"                                                            ,
        mutability              = "DEFAULT"                                                       ,
        humanreadable_string1   = '"?actor intends that ?intention"'
    )
    db.session.add(new_predicate)
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                   ,
        predicate_label         = "equals"                                                        ,
        definition_str          = "['equals', ['?object1', 'object'], ['?object2', 'object']]"    ,
        function_string         = "equals(?object1, ?object2)"                                    ,
        parameter1_label        = "?object1"                                                      ,
        parameter1_type         = "object"                                                        ,
        parameter2_label        = "?object2"                                                      ,
        parameter2_type         = "object"                                                        ,
        primary_object          = "[]"                                                            ,
        secondary_object        = "[]"                                                            ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = "INVISIBLE"                                                     ,
        humanreadable_string1   = ""
    )
    db.session.add(new_predicate)
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                         ,
        predicate_label         = "forall"                                                              ,
        definition_str          = "['forall', ['!object1', 'object'], ['?whenstatement', 'predicate']]" ,
        function_string         = "forall(!object1, ?whenstatement)"                                    ,
        parameter1_label        = "!object1"                                                            ,
        parameter1_type         = "object"                                                              ,
        parameter2_label        = "?whenstatement"                                                      ,
        parameter2_type         = "predicate"                                                           ,
        primary_object          = "[]"                                                                  ,
        secondary_object        = "[]"                                                                  ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = "INVISIBLE"                                                     ,
        humanreadable_string1   = ""
    )
    db.session.add(new_predicate)
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                         ,
        predicate_label         = "if"                                                                  ,
        definition_str          = "['if', ['?somecondition', 'predicate'], ['?iftrue', 'predicate']]"   ,
        function_string         = "if(?somecondition, ?iftrue)"                                         ,
        parameter1_label        = "?somecondition"                                                      ,
        parameter1_type         = "predicate"                                                           ,
        parameter2_label        = "?iftrue"                                                             ,
        parameter2_type         = "predicate"                                                           ,
        primary_object          = "[]"                                                                  ,
        secondary_object        = "[]"                                                                  ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = "INVISIBLE"                                                     ,
        humanreadable_string1   = ""
    )
    db.session.add(new_predicate)
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                                                   ,
        predicate_label         = "ifelse"                                                                                        ,
        definition_str          = "['ifelse', ['?somecondition', 'predicate'], ['?iftrue', 'predicate'], ['?else', 'predicate']]" ,
        function_string         = "ifelse(?somecondition, ?iftrue, ?else)"                                                        ,
        parameter1_label        = "?somecondition"                                                                                ,
        parameter1_type         = "predicate"                                                                                     ,
        parameter2_label        = "?iftrue"                                                                                       ,
        parameter2_type         = "predicate"                                                                                     ,
        parameter3_label        = "?else"                                                                                       ,
        parameter3_type         = "predicate"                                                                                     ,
        primary_object          = "[]"                                                                                         ,
        secondary_object        = "[]"                                                                                     ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = "INVISIBLE"                                                     ,
        humanreadable_string1   = ""
    )
    db.session.add(new_predicate)
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                   ,
        predicate_label         = "at"                                                            ,
        definition_str          = "['at', ['?someobj', 'object'], ['?somelocation', 'location']]" ,
        function_string         = "at(?someobj,?somelocation)"                                    ,
        parameter1_label        = "?someobj"                                                      ,
        parameter1_type         = "object"                                                        ,
        parameter1_min_instances= 1                                                               ,
        parameter1_max_instances= 1                                                               ,
        parameter2_label        = "?somelocation"                                                 ,
        parameter2_type         = "location"                                                      ,
        parameter2_min_instances= 0                                                               ,
        parameter2_max_instances= "many"                                                          ,
        primary_object          = "[['?someobj', 'object']]"                                      ,
        secondary_object        = "[]"                                                            ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = ""                                                     ,
        humanreadable_string1   = '"?someobj is at ?somelocation"'
    )
    db.session.add(new_predicate)
    db.session.commit()
    
    new_predicate = StatePredicateDef(
        domain_id               = new_domain.id                                                   ,
        predicate_label         = "adjacent"                                                      ,
        definition_str          = "['adjacent', ['?fromplace', 'place'], ['?toplace', 'place']]"  ,
        function_string         = "adjacent(?fromplace, ?toplace)"                                ,
        parameter1_label        = "?fromplace"                                                    ,
        parameter1_type         = "location"                                                      ,
        parameter2_label        = "?toplace"                                                      ,
        parameter2_type         = "location"                                                      ,
        primary_object          = "[]"                                                            ,
        secondary_object        = "[]"                                                            ,
        mutability              = "DEFAULT"                                                       ,
        visibility              = "INVISIBLE"                                                     ,
        humanreadable_string1   = '"from ?fromplace, one can reach ?toplace."'
    )
    db.session.add(new_predicate)
    db.session.commit()
    
    
     
    return redirect(url_for('domain_instance',title="Domain Instance",
        domain_instance_id=new_domain.id,
        copy_from=copy_from,
        load_type=1)
    )
 
@app.route("/deactivate_domain/<domain_instance_id>")
def deactivate_domain(domain_instance_id):

    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    domain_instance  = Domains.query.get_or_404(domain_instance_id)
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    if (domain_instance.visibility not in ["PUBLIC-READONLY", "PUBLIC-WRITE"]) and (domain_instance.created_by != user_id):
        abort(403)
    else:
        
        domain_instance.status = "INACTIVE"
        db.session.commit()
        
        
    return redirect(url_for('domains'))
        
        
 
@app.route("/activate_domain/<domain_instance_id>")
def activate_domain(domain_instance_id):

    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    domain_instance  = Domains.query.get_or_404(domain_instance_id)
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    if (domain_instance.visibility not in ["PUBLIC-READONLY", "PUBLIC-WRITE"]) and (domain_instance.created_by != user_id):
        abort(403)
    else:
        
        domain_instance.status = "ACTIVE"
        db.session.commit()
        
        
    return redirect(url_for('domains'))

    
@app.route('/_submit_domain_geninfo')
def submit_domain_geninfo():
     
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    #user_id = request.args.get('user_id', None, type=str)
     
    # ==============
    # Arguments
    domain_id       = request.args.get('domain_id')
    category        = request.args.get('category')
    sub_label       = request.args.get('sub_label')
    readable_label  = request.args.get('readable_label')
    visibility      = request.args.get('visibility')
    author_notes    = request.args.get('author_notes')
     
    # ==============
    # Query
    current_domain = Domains.query.filter_by(id=domain_id).first()
    

    
    old_domain_full_label = current_domain.domain_full_label
    
    
    current_domain.category             = category
    current_domain.category_str         = utility.smallify(category)
    current_domain.sub_label            = sub_label
    current_domain.sub_label_str        = utility.smallify(sub_label)
    current_domain.readable_label       = readable_label
    current_domain.visibility           = visibility
    current_domain.author_notes         = author_notes
    current_domain.last_edited_by       = user_id
    
    
    category_str  = current_domain.category_str
    sub_label_str = current_domain.sub_label_str
    series        = current_domain.series
    new_domain_full_label = category_str + "_" + sub_label_str + "_" + series
    current_domain.domain_full_label    = new_domain_full_label
    
    db.session.commit()
    
    # Update all other references
    
    #=====================
    existing_stuff = db.session.query(ActionDef) \
        .filter(ActionDef.domain_full_label == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain_full_label = new_domain_full_label
        somestuff.action_full_label = somestuff.action_full_label.replace(old_domain_full_label,new_domain_full_label)
    db.session.commit()
    
    #=====================
    existing_stuff = db.session.query(Action_Predicates) \
        .filter(Action_Predicates.action_full_label.like("%"+old_domain_full_label+"%"))
        
    for somestuff in existing_stuff:
        somestuff.action_full_label = somestuff.action_full_label.replace(old_domain_full_label,new_domain_full_label)
    db.session.commit()

    #=====================
    existing_stuff = db.session.query(Action_Parameters) \
        .filter(Action_Parameters.action_full_label.like("%"+old_domain_full_label+"%"))
        
    for somestuff in existing_stuff:
        somestuff.action_full_label = somestuff.action_full_label.replace(old_domain_full_label,new_domain_full_label)
    db.session.commit()

    
    # action_full_label
    #
    # ActionDef
    # - action_full_label
    # 
    # Action_Predicates
    # - action_full_label
    # 
    # Action_Parameters
    # - action_full_label
 
    #UPDATE action_def
    #SET action_full_label = REPLACE(action_full_label,"custom_draft_03","sciencefiction_mecha_03")
    #WHERE
    #action_full_label LIKE "%custom_draft_03%"
    
    #=====================
    existing_stuff = db.session.query(ChapterPattern) \
        .filter(ChapterPattern.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit()

    #=====================
    existing_stuff = db.session.query(SequenceTermCategories) \
        .filter(SequenceTermCategories.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit()        
    
    #=====================
    existing_stuff = db.session.query(SequenceTermActors) \
        .filter(SequenceTermActors.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit()  
    
    #=====================
    existing_stuff = db.session.query(SequenceTermObjects) \
        .filter(SequenceTermObjects.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit()  
    
    #=====================
    existing_stuff = db.session.query(PredicateDescriptors) \
        .filter(PredicateDescriptors.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit() 
    
    #=====================
    existing_stuff = db.session.query(ObjectNames) \
        .filter(ObjectNames.domain == old_domain_full_label)
        
    for somestuff in existing_stuff:
        somestuff.domain = new_domain_full_label
    db.session.commit() 
    
    
    
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)
        
 
@app.route('/_add_domain_objtype')
def add_domain_objtype():
     
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    #user_id = request.args.get('user_id', None, type=str)
     
    # ==============
    # Arguments
    domain_id      = request.args.get('domain_id')
    prevobj_type   = request.args.get('prevobj_type')
    object_type    = request.args.get('object_type')
    parent_type    = request.args.get('parent_type')
     
     
    # ==============
    # Query
    existing_obj_type = ObjectTypes.query                                  \
                            .filter(ObjectTypes.object_type==prevobj_type) \
                            .filter(ObjectTypes.domain_id==domain_id) \
                            .first()
                            
                             
#.filter(domain_id==domain_id)                 \
     
    if existing_obj_type:
        existing_obj_type.object_type = object_type
        existing_obj_type.parent_type = parent_type
        existing_obj_type.default_flag = ""
    else:
     
        new_obj_type = ObjectTypes(
                        domain_id      = domain_id    ,
                        object_type    = object_type     ,
                        parent_type    = parent_type 
                         
                         
                        )
     
        db.session.add(new_obj_type)
     
    db.session.commit()
     
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)
     
@app.route('/_add_domain_predicate_def')
def add_domain_predicate_def():
     
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    #user_id = request.args.get('user_id', None, type=str)
     
    # ==============
    # Arguments
    
    parameter = []
    
    domain_id                 = request.args.get('domain_id')
    domain_full_label         = request.args.get('domain_full_label')
    prevpred_label            = request.args.get('prevpred_label')
    predicate_label           = request.args.get('predicate_label')
    #definition_str            = request.args.get('definition_str')      # THIS IS USELESS, SERVER COMPUTES THIS
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter1_label',"",type=str)
    param_list["type"]          = request.args.get('parameter1_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter1_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter1_max_instances',"",type=str)
    parameter.append(param_list)
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter2_label',"",type=str)
    param_list["type"]          = request.args.get('parameter2_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter2_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter2_max_instances',"",type=str)
    parameter.append(param_list)
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter3_label',"",type=str)
    param_list["type"]          = request.args.get('parameter3_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter3_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter3_max_instances',"",type=str)
    parameter.append(param_list)
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter4_label',"",type=str)
    param_list["type"]          = request.args.get('parameter4_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter4_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter4_max_instances',"",type=str)
    parameter.append(param_list)
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter5_label',"",type=str)
    param_list["type"]          = request.args.get('parameter5_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter5_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter5_max_instances',"",type=str)
    parameter.append(param_list)
    
    param_list = dict()
    param_list["label"]         = request.args.get('parameter6_label',"",type=str)
    param_list["type"]          = request.args.get('parameter6_type',"",type=str)
    param_list["min_instances"] = request.args.get('parameter6_min_instances',"",type=str)
    param_list["max_instances"] = request.args.get('parameter6_max_instances',"",type=str)
    parameter.append(param_list)
    
    primary_object            = "["+request.args.get('primary_object')+"]"
    secondary_object          = "["+request.args.get('secondary_object')+"]"
     
    humanreadable_string1     = request.args.get('humanreadable_string1')
    humanreadable_string2     = request.args.get('humanreadable_string2')
    humanreadable_string3     = request.args.get('humanreadable_string3')
    humanreadable_string4     = request.args.get('humanreadable_string4')
    
    initial_state_affinity     = request.args.get('initial_state_affinity')
    initial_intention_affinity = request.args.get('initial_intention_affinity')
    
    mutability                = request.args.get('mutability')
    visibility                = request.args.get('visibility')
    
    function_string           = request.args.get('function_string')
     
    # ==============
    # Query
    existing_pred_def = StatePredicateDef.query                                        \
                            .filter(StatePredicateDef.predicate_label==prevpred_label) \
                            .filter(StatePredicateDef.domain_id==domain_id)            \
                            .first()
    definition_list = []
    definition_list.append(predicate_label)
    
    for param_ctr in range(0,6):
        if parameter[param_ctr]["label"] != "":
            new_param = [parameter[param_ctr]["label"],parameter[param_ctr]["type"]]
            definition_list.append(new_param)
            
    definition_str = str(definition_list)
    
    
    #========================================================
    # Update/Add to StatePredicateDef
    
    old_predicate_label = ""
    
    if existing_pred_def:
        existing_pred_def.predicate_label           = predicate_label      
        existing_pred_def.definition_str            = definition_str       
        
        existing_pred_def.parameter1_label          = parameter[0]["label"]        
        existing_pred_def.parameter1_type           = parameter[0]["type"]         
        existing_pred_def.parameter1_min_instances  = parameter[0]["min_instances"]
        existing_pred_def.parameter1_max_instances  = parameter[0]["max_instances"]
                                                      
        existing_pred_def.parameter2_label          = parameter[1]["label"]        
        existing_pred_def.parameter2_type           = parameter[1]["type"]         
        existing_pred_def.parameter2_min_instances  = parameter[1]["min_instances"]
        existing_pred_def.parameter2_max_instances  = parameter[1]["max_instances"]
                                                      
        existing_pred_def.parameter3_label          = parameter[2]["label"]        
        existing_pred_def.parameter3_type           = parameter[2]["type"]         
        existing_pred_def.parameter3_min_instances  = parameter[2]["min_instances"]
        existing_pred_def.parameter3_max_instances  = parameter[2]["max_instances"]
                                                      
        existing_pred_def.parameter4_label          = parameter[3]["label"]        
        existing_pred_def.parameter4_type           = parameter[3]["type"]         
        existing_pred_def.parameter4_min_instances  = parameter[3]["min_instances"]
        existing_pred_def.parameter4_max_instances  = parameter[3]["max_instances"]
                                                      
        existing_pred_def.parameter5_label          = parameter[4]["label"]        
        existing_pred_def.parameter5_type           = parameter[4]["type"]         
        existing_pred_def.parameter5_min_instances  = parameter[4]["min_instances"]
        existing_pred_def.parameter5_max_instances  = parameter[4]["max_instances"]
                                                      
        existing_pred_def.parameter6_label          = parameter[5]["label"]        
        existing_pred_def.parameter6_type           = parameter[5]["type"]         
        existing_pred_def.parameter6_min_instances  = parameter[5]["min_instances"]
        existing_pred_def.parameter6_max_instances  = parameter[5]["max_instances"]
         
        existing_pred_def.primary_object            = primary_object       
        existing_pred_def.secondary_object          = secondary_object     
            
        existing_pred_def.humanreadable_string1     = humanreadable_string1
        existing_pred_def.humanreadable_string2     = humanreadable_string2
        existing_pred_def.humanreadable_string3     = humanreadable_string3
        existing_pred_def.humanreadable_string4     = humanreadable_string4
        
        existing_pred_def.initial_state_affinity     = initial_state_affinity
        existing_pred_def.initial_intention_affinity = initial_intention_affinity
        existing_pred_def.mutability                = mutability
        existing_pred_def.visibility                = visibility
        
        existing_pred_def.function_string           = function_string
    else:
    
        new_pred_def = StatePredicateDef(
                                domain_id                = domain_id                ,
                                predicate_label          = predicate_label          ,
                                definition_str           = definition_str           ,
                                
                                parameter1_label         = parameter[0]["label"]         ,
                                parameter1_type          = parameter[0]["type"]          ,
                                parameter1_min_instances = parameter[0]["min_instances"] ,
                                parameter1_max_instances = parameter[0]["max_instances"] ,
                                                           
                                parameter2_label         = parameter[1]["label"]         ,
                                parameter2_type          = parameter[1]["type"]          ,
                                parameter2_min_instances = parameter[1]["min_instances"] ,
                                parameter2_max_instances = parameter[1]["max_instances"] ,
                                                           
                                parameter3_label         = parameter[2]["label"]         ,
                                parameter3_type          = parameter[2]["type"]          ,
                                parameter3_min_instances = parameter[2]["min_instances"] ,
                                parameter3_max_instances = parameter[2]["max_instances"] ,
                                                           
                                parameter4_label         = parameter[3]["label"]         ,
                                parameter4_type          = parameter[3]["type"]          ,
                                parameter4_min_instances = parameter[3]["min_instances"] ,
                                parameter4_max_instances = parameter[3]["max_instances"] ,
                                                           
                                parameter5_label         = parameter[4]["label"]         ,
                                parameter5_type          = parameter[4]["type"]          ,
                                parameter5_min_instances = parameter[4]["min_instances"] ,
                                parameter5_max_instances = parameter[4]["max_instances"] ,
                                                           
                                parameter6_label         = parameter[5]["label"]         ,
                                parameter6_type          = parameter[5]["type"]          ,
                                parameter6_min_instances = parameter[5]["min_instances"] ,
                                parameter6_max_instances = parameter[5]["max_instances"] ,
                                

                                primary_object           = primary_object           ,
                                secondary_object         = secondary_object         ,
    
                                humanreadable_string1    = humanreadable_string1    ,
                                humanreadable_string2    = humanreadable_string2    ,
                                humanreadable_string3    = humanreadable_string3    ,
                                humanreadable_string4    = humanreadable_string4    ,
                                
                                initial_state_affinity     = initial_state_affinity     ,
                                initial_intention_affinity = initial_intention_affinity ,
                                mutability                 = "CUSTOM"                   ,
                                visibility                 = visibility                 ,
                                
                                function_string          = function_string
                        )
     
        db.session.add(new_pred_def)
    
    db.session.commit()
    
    #========================================================
    # Update/Add to PredicateDescriptors
    
    #   id                              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    #   domain (label)                  = db.Column(db.String(32), nullable=False)
    #   main_label                      = db.Column(db.String(32), nullable=False)
    #   main_label_str                  = db.Column(db.String(32), nullable=False)
    #   sub_label                       = db.Column(db.String(16), nullable=True)
    #   sub_label_str                   = db.Column(db.String(16), nullable=True)
    #   name_label_str                  = db.Column(db.String(64), nullable=False)
    #   term_sequence                   = db.Column(db.String(8), nullable=False)
    #   term_sequence_grouping_label    = db.Column(db.String(16), nullable=False)
    #   parameter_label                 = db.Column(db.String(16), nullable=False)
    #   parameter_type                  = db.Column(db.String(16), nullable=False)        
    #   likelihood                      = db.Column(db.Float, nullable=False) 
    #   min_unique                      = db.Column(db.String(16), nullable=False) 
    #   max_unique                      = db.Column(db.String(16), nullable=False) 
    #   duplicates_allowed              = db.Column(db.String(8), nullable=False) 
    #   notes                           = db.Column(db.Text, nullable=True)
    #   status                          = db.Column(db.String(16))
    #   created_by                      = db.Column(db.String(16))
    #   last_edited_by                  = db.Column(db.String(16))
    #   date_created                    = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    #   last_edited                     = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    
    # ==============
    # Query
    
    for param_ctr in range(1,7):
        # 
        
        main_label_str                  = utility.smallify(predicate_label)
        name_label_str                  = domain_full_label + "_" + main_label_str
        term_sequence                   = utility.zeroStringPad(param_ctr,2)
        term_sequence_grouping_label    = domain_full_label + "_" + main_label_str + "_" + term_sequence
        parameter_label                 = parameter[param_ctr-1]["label"]
        parameter_type                  = parameter[param_ctr-1]["type"]
        min_unique                      = parameter[param_ctr-1]["min_instances"]
        max_unique                      = parameter[param_ctr-1]["max_instances"]
        likelihood                      = initial_state_affinity
        duplicates_allowed              = 0
        
        existing_pred_descriptors = PredicateDescriptors.query \
                                .filter(PredicateDescriptors.term_sequence_grouping_label == term_sequence_grouping_label)
        if(parameter_label != ""):
        
            existing_pred_descriptor = existing_pred_descriptors.first()
            if existing_pred_descriptor:
                #existing_pred_descriptor.domain                          = domain_full_label
                existing_pred_descriptor.main_label                      = predicate_label
                existing_pred_descriptor.main_label_str                  = main_label_str
                existing_pred_descriptor.sub_label                       = ""                                          
                existing_pred_descriptor.sub_label_str                   = ""                                          
                existing_pred_descriptor.name_label_str                  = name_label_str
                existing_pred_descriptor.term_sequence                   = term_sequence                               
                existing_pred_descriptor.term_sequence_grouping_label    = term_sequence_grouping_label                
                existing_pred_descriptor.parameter_label                 = parameter_label.replace("?","")
                existing_pred_descriptor.parameter_type                  = parameter_type                              
                existing_pred_descriptor.likelihood                      = likelihood                                  
                existing_pred_descriptor.min_unique                      = min_unique                                  
                existing_pred_descriptor.max_unique                      = max_unique                                  
                existing_pred_descriptor.duplicates_allowed              = duplicates_allowed                          
                #existing_pred_descriptor.notes                           =                                            
                #existing_pred_descriptor.status                          =                                            
                existing_pred_descriptor.last_edited_by                  = user_id                                     
                
            else:
                
                new_pred_descriptor = PredicateDescriptors(
                    
                    domain                          = domain_full_label                             ,
                    main_label                      = predicate_label                               ,
                    main_label_str                  = main_label_str                                ,
                    sub_label                       = ""                                            ,
                    sub_label_str                   = ""                                            ,
                    name_label_str                  = name_label_str                                ,
                    term_sequence                   = term_sequence                                 ,
                    term_sequence_grouping_label    = term_sequence_grouping_label                  ,
                    parameter_label                 = parameter_label.replace("?","")               ,
                    parameter_type                  = parameter_type                                ,
                    likelihood                      = likelihood                                    ,
                    min_unique                      = min_unique                                    ,
                    max_unique                      = max_unique                                    ,
                    duplicates_allowed              = duplicates_allowed                            ,
                    #notes                           =                                              ,
                    #status                          =                                              ,
                    created_by                      = user_id                                       ,
                    last_edited_by                  = user_id                                       
                )
                db.session.add(new_pred_descriptor)
                
        else:
            for something in existing_pred_descriptors.all():
                db.session.delete(something)
                
    db.session.commit()
    
    #========================================================
    # Update to Action_Predicates
    
    if prevpred_label != "":
        
        existing_predicates = db.session.query(Action_Predicates) \
            .filter(Action_Predicates.action_full_label.like(domain_full_label + "%")) \
            .filter(Action_Predicates.predicate_raw.like("%'"+prevpred_label+"'%")) \
            .all()
            
        for some_existing_predicate in existing_predicates:
            some_existing_predicate.predicate_raw = some_existing_predicate.predicate_raw.replace("'"+prevpred_label+"'","'"+predicate_label+"'")
            
        db.session.commit()
        #existing_predicates = db.session.query(Action_Predicates).join(ActionDef, Action_Predicates.)
    success_flag = True
    
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)
        
#==================================================================================
 
@app.route("/domain_instance/<domain_instance_id>")
def domain_instance(domain_instance_id):
     
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
     
    copy_from  = request.args.get('copy_from', "")
    load_type  = request.args.get('load_type', 0)
    
    domain_instance  = Domains.query.get_or_404(domain_instance_id)
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    if (domain_instance.visibility not in ["PUBLIC-READONLY", "PUBLIC-WRITE"]) and (domain_instance.created_by != user_id):
        abort(403)
    else:
        object_types            = ObjectTypes.query.filter_by(domain_id=domain_instance_id).order_by(ObjectTypes.object_type)
        actor_types             = ActorTypes.query.filter_by(domain_id=domain_instance_id).order_by(ActorTypes.object_type)
        state_predicate_defs    = StatePredicateDef.query.filter_by(domain_id=domain_instance_id).order_by(StatePredicateDef.predicate_label)
        action_defs             = ActionDef.query.filter_by(domain_id=domain_instance_id).order_by(ActionDef.action_label)
        
        return render_template('domain_instance.html', title='Domain Instance',
            user_id              = user_id,    
            domain_instance      = domain_instance,
            loadable_domains     = loadable_domains,
            object_types         = object_types,
            actor_types          = actor_types ,
            state_predicate_defs = state_predicate_defs ,
            action_defs          = action_defs,
            copy_from            = copy_from,
            load_type            = load_type
        )
     
#==================================================================================
 
@app.route("/story_generator", methods=['GET','POST'])
def story_generator():
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
        
    form = GenerateStoryForm()
    
    form.domain_full_label.choices = [(d.domain_full_label, d.readable_label) for d in Domains.query.filter_by(status = "ACTIVE").order_by('readable_label')]
     #form.story_pattern.choices = [(sp.grouping_label, sp.readable_label) for sp in StoryPattern.query.order_by('grouping_label')]
    form.story_pattern.choices = [(cp.name_label_str, (cp.main_label + ("" if cp.sub_label == "" else ("-" + cp.sub_label)))) \
            for cp in ChapterPattern.query \
                .with_entities(ChapterPattern.name_label_str, ChapterPattern.main_label, ChapterPattern.sub_label) \
               #.filter(ChapterPattern.status == "ACTIVE") \
                .distinct() \
                .order_by('main_label') \
    ]
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY")).filter_by(status = "ACTIVE")
    own_domains     = Domains.query.filter_by(created_by=user_id).filter_by(status = "ACTIVE")
    loadable_domains = own_domains.union(public_domains).all()
    
    public_maps  = LocationMap.query.filter(or_(LocationMap.visibility=="PUBLIC-WRITE", LocationMap.visibility=="PUBLIC-READONLY"))
    own_maps     = LocationMap.query.filter_by(created_by=user_id)
    loadable_maps = own_maps.union(public_maps).all()
    
    return render_template('story_generator.html', title='Story Generator', 
        form=form,
        loadable_domains = loadable_domains,
        loadable_maps = loadable_maps
    )
     
 
@app.route("/story_archive")
def story_archive():    
     
    narratives = db.session.query(NarrativeInstance, UserActivePlanners)                                                                        \
                    .order_by(NarrativeInstance.date_created.desc())                                                                            \
                    .filter(NarrativeInstance.narrative_id.like("%"+UserActivePlanners.narrative_id+"%"))                                       \
                    .filter(UserActivePlanners.status == "SUCCESS")   \
                    .all()
                    #.filter(NarrativeInstance.narrative_label.like("%Booker7Plots%"))                                                          \
                    
    return render_template('story_archive.html', title='Story Archive', narratives=narratives)
     
#==================================================================================
 
@app.route("/plot_armor_game", methods=['GET','POST'])
def plot_armor_game():
 
    return render_template('plot_armor_game.html', title='Plot Armor Game')
         
#==================================================================================
 
@app.route("/chapter_patterns")
def chapter_patterns():    
    
    chapter_pattern_groups = db.session.query(ChapterPattern.sequence_grouping_label, 
                        ChapterPattern.main_label,                                    
                        ChapterPattern.sub_label,                                     
                        ChapterPattern.pattern_sequence,
                        ChapterPattern.visibility
                    ) \
                    .order_by(ChapterPattern.main_label.asc())  \
                    .distinct()
    
    chapter_pattern_chapters = db.session.query(ChapterPattern)  \
                    .order_by(ChapterPattern.pattern_full_label.asc())  \
                    .all()
                    
    return render_template('chapter_patterns.html', 
        title='Chapter Patterns', 
        chapter_pattern_groups=chapter_pattern_groups, 
        chapter_pattern_chapters=chapter_pattern_chapters
    )
  
@app.route("/chapter_pattern_instance/<string:pattern_sequence>")
def chapter_pattern_instance(pattern_sequence):  

    chapter_pattern_group = db.session.query(ChapterPattern.sequence_grouping_label, 
                        ChapterPattern.main_label,                                    
                        ChapterPattern.sub_label,                                     
                        ChapterPattern.pattern_sequence                               
                    ).filter(ChapterPattern.sequence_grouping_label == pattern_sequence) \
                    .first()
    
    chapter_pattern_chapters = db.session.query(ChapterPattern)  \
                    .filter(ChapterPattern.sequence_grouping_label == pattern_sequence) \
                    .order_by(ChapterPattern.pattern_full_label.asc())  \
                    .all()
    
    sequence_term_cat_labels = db.session.query(ChapterPattern.sequence_term_cat_label) \
                    .filter(ChapterPattern.sequence_grouping_label == pattern_sequence) \
                    .distinct() 
                    
    sequence_terms = db.session.query(SequenceTerms) \
                    .filter(SequenceTerms.sequence_term_cat_label.in_(sequence_term_cat_labels.as_scalar())) \
                    .all()
    
    if len(chapter_pattern_chapters) > 0:
        return render_template('chapter_pattern_instance.html', title='Chapter Pattern Instance', 
            chapter_pattern_group=chapter_pattern_group, 
            chapter_pattern_chapters=chapter_pattern_chapters,
            sequence_terms=sequence_terms
        )
    else:
        abort(404)
    
@app.route("/new_chapter_pattern_instance")
def new_chapter_pattern_instance():    

    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
        
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    sequence_term_cat_labels = db.session.query(SequenceTerms.sequence_term_cat_label) \
                    .distinct() \
                    .order_by(SequenceTerms.sequence_term_cat_label.asc()) \
                    .all()
                    
    return render_template('new_chapter_pattern_instance.html', title='New Chapter Pattern',
                    sequence_term_cat_labels = sequence_term_cat_labels,
                    domains = loadable_domains
    )
    
@app.route("/sequence_term_categories")
def sequence_term_categories():  
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    public_sequece_terms_categories    = SequenceTermCategories.query.filter(or_(SequenceTermCategories.visibility=="PUBLIC-WRITE", SequenceTermCategories.visibility=="PUBLIC-READONLY"))
    own_sequence_terms_categories      = SequenceTermCategories.query.filter_by(created_by=user_id)
    loadable_sequence_terms_categories = own_sequence_terms_categories.union(public_sequece_terms_categories)
    
    lookup_a = own_sequence_terms_categories.union(public_sequece_terms_categories) \
        .with_entities(SequenceTermCategories.sequence_term_cat_label) \
        .as_scalar()
    
    #
    #lookup_a = own_domains.union(public_domains).as_scalar()
    #object_names = db.session.query(ObjectNames) \
    #    .filter(ObjectNames.domain.in_(lookup_a))    
    #
    #
    
    
    sequence_terms_name_labels = db.session.query(SequenceTerms) \
        .filter(SequenceTerms.sequence_term_cat_label.in_(lookup_a)) \
        .order_by(SequenceTerms.name_label_str.asc()) \
        .with_entities(
                SequenceTerms.sequence_term_cat_label,
                SequenceTerms.main_label,
                SequenceTerms.name_label_str
            ) \
        .distinct()
    
    
    
    return render_template('sequence_term_categories.html', title='Sequence Term Categories',
                    loadable_sequence_terms_categories=loadable_sequence_terms_categories.all(),
                    sequence_terms_name_labels=sequence_terms_name_labels
    )
    
    
@app.route("/sequence_term_category_instance")
def sequence_term_category_instance():  
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    # == Domains
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    # == Sequence Term Labels
    existing_sequence_term_labels = db.session.query(SequenceTerms.sequence_term_cat_label) \
                                .distinct() \
                                .all()
    
    return render_template('sequence_term_category_instance.html', title='Sequence Term Category Instance',
        domains = loadable_domains,
        existing_sequence_term_labels = existing_sequence_term_labels
    )
    
@app.route("/new_sequence_term_category_instance")
def new_sequence_term_category_instance(): 

    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"

    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains).all()
    
    #====
    current_main_objs = db.session.query(SequenceTerms.main_object) \
                    .distinct()
    current_main_objs_list = [r for r, in current_main_objs]
    
    #====
    current_supp_objs = db.session.query(SequenceTerms.supporting_objects) \
                    .distinct()
    temp = []
    for someobjraw in current_supp_objs.all():
        if someobjraw.supporting_objects is not None:
            split_obj = someobjraw.supporting_objects.split(";")
            for someobj in split_obj:
                if (someobj not in temp) and (someobj != ""):
                    temp.append(someobj)
    
    current_supp_objs_list = sorted(temp)
    #====
    all_objs_list = sorted(list(set(current_main_objs_list) | set(current_supp_objs_list)))
    #====
    predicate_labels = db.session.query(StatePredicateDef.definition_str, StatePredicateDef.humanreadable_string1) \
                    .all()
    #====
    object_types = db.session.query(ObjectTypes).all()
    #====
    
    #return render_template('new_sequence_term_category_instance.html', title='New Sequence Term Category',
    #    current_main_objs = current_main_objs_list,
    #    current_supp_objs = current_supp_objs_list,
    #    current_all_objs  = all_objs_list,
    #    predicate_labels = predicate_labels,
    #    object_types = object_types
    #)
    
    #=================================
    # New approach
    
    existing_sequence_term_labels = db.session.query(SequenceTerms.sequence_term_cat_label) \
                                .distinct() \
                                .all()
    
    return render_template('new_sequence_term_category_instance.html', title='New Sequence Term Category',
        domains = loadable_domains,
        existing_sequence_term_labels = existing_sequence_term_labels,
        current_all_objs  = all_objs_list,
        predicate_labels = predicate_labels,
        object_types = object_types
    )
    
@app.route("/location_maps")
def location_maps():
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
        
    public_maps  = LocationMap.query.filter(or_(LocationMap.visibility=="PUBLIC-WRITE", LocationMap.visibility=="PUBLIC-READONLY"))
    own_maps     = LocationMap.query.filter_by(created_by=user_id)
    loadable_maps = own_maps.union(public_maps).all()
    
    return render_template('location_maps.html', title='Location Maps',
        loadable_maps = loadable_maps
    )
    
@app.route("/location_map_instance")
def location_map_instance():
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    map_id = request.args.get('map_id', 0, type=int)
    
    if map_id == 0:
        title='New Location Map'
        map_label = ""
    else:
        title='Edit Location Map'
    
        #public_maps  = LocationMap.query.filter(or_(LocationMap.visibility=="PUBLIC-WRITE", LocationMap.visibility=="PUBLIC-READONLY")).with_entities(LocationMap.id)
        #own_maps     = LocationMap.query.filter_by(created_by=user_id).with_entities(LocationMap.id)
        #loadable_maps = own_maps.union(public_maps).as_scalar()
        
        
        somemap = db.session.query(LocationMap) \
            .filter(LocationMap.id == map_id) \
            .first()
        
        print("=====================")
        
        
        print(map_id)
        print(somemap)
        print("====")
        map_label = somemap.map_label
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains)
    
    
    
    return render_template('location_map_instance.html', title=title,
        loadable_domains = loadable_domains,
        map_label = map_label
    )
    
    
@app.route("/random_survey")
def random_survey():
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
        
    title = "Random Survey"
    
    # Get X random narrative instances. At least 1 for each domain
    #narratives = db.session.query(NarrativeInstance, UserActivePlanners)                                                                        \
    #                .order_by(NarrativeInstance.date_created.desc())                                                                            \
    #                .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id).filter(UserActivePlanners.status == "SUCCESS")   \
    #                .all()
                    
    
    
    random_narratives = []
    
    #narrative_instance_main1 = db.session.query(NarrativeInstance)                               \
    #                .order_by(func.random())                                        \
    #                .filter(NarrativeInstance.story_pattern.like("booker7plots%"))    \
    #                .limit(1)                                                       \
    #                .all()
    
    
    narrative_instance_main1 = db.session.query(NarrativeInstance, UserActivePlanners)                               \
                    .order_by(func.random())                                        \
                    .filter(NarrativeInstance.story_pattern.like("booker7plots%"))    \
                    .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id) \
                    .filter(UserActivePlanners.status == "SUCCESS")   \
                    .limit(1)                                                       \
                    .all()
                    
    
    narrative_instance_summary1 = db.session.query(ChapterPattern) \
        .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance_main1[0][0].story_pattern)) \
        .filter(ChapterPattern.vacant1 is not None) \
        .first()
    
    for something in narrative_instance_main1[0]:
        random_narratives.append([something.narrative_id, narrative_instance_summary1.vacant1])
        break
    
    #----
    narrative_instance_main2 = db.session.query(NarrativeInstance, UserActivePlanners)                               \
                    .order_by(func.random())                                        \
                    .filter(NarrativeInstance.story_pattern.like("custom_fva%"))    \
                    .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id) \
                    .filter(UserActivePlanners.status == "SUCCESS")   \
                    .limit(1)                                                       \
                    .all()
                    
    narrative_instance_summary2 = db.session.query(ChapterPattern) \
        .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance_main2[0][0].story_pattern)) \
        .filter(ChapterPattern.vacant1 is not None) \
        .first()
    
    for something in narrative_instance_main2[0]:
        random_narratives.append([something.narrative_id, narrative_instance_summary2.vacant1])
        break
    #----
                    
    narrative_instance_main3 = db.session.query(NarrativeInstance, UserActivePlanners)                               \
                    .order_by(func.random())                                        \
                    .filter(NarrativeInstance.story_pattern.like("custom_sol%"))    \
                    .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id) \
                    .filter(UserActivePlanners.status == "SUCCESS")   \
                    .limit(1)                                                       \
                    .all()
                    
    narrative_instance_summary3 = db.session.query(ChapterPattern) \
        .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance_main3[0][0].story_pattern)) \
        .filter(ChapterPattern.vacant1 is not None) \
        .first()
    
    for something in narrative_instance_main3[0]:
        random_narratives.append([something.narrative_id, narrative_instance_summary3.vacant1])
        break
    
    #narrative_instance_summary = db.session.query(ChapterPattern) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(narrative_instance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .first()
    
    #narratives1 = db.session.query(NarrativeInstance, ChapterPattern) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .filter(NarrativeInstance.story_pattern.like("custom_sol%"))    \
    #    .order_by(func.random())                                        \
    #    .limit(1)                                                       \
    #    .all()
    #
    #narratives2 = db.session.query(NarrativeInstance, ChapterPattern) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .filter(NarrativeInstance.story_pattern.like("booker7plots%"))    \
    #    .order_by(func.random())                                        \
    #    .limit(1)     \
    #    .all()
    #    
    #narratives3 = db.session.query(NarrativeInstance, ChapterPattern) \
    #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
    #    .filter(ChapterPattern.vacant1 is not None) \
    #    .filter(NarrativeInstance.story_pattern.like("custom_fva%"))    \
    #    .order_by(func.random())                                        \
    #    .limit(1)     \
    #    .all()
    
    
    #narratives2 = db.session.query(NarrativeInstance)                               \
    #                .order_by(func.random())                                        \
    #                .filter(NarrativeInstance.story_pattern.like("booker7plots%"))  \
    #                .limit(1)                                                       \
    #                .all()
    #
    #narratives3 = db.session.query(NarrativeInstance)                               \
    #                .order_by(func.random())                                        \
    #                .filter(NarrativeInstance.story_pattern.like("custom_fva%"))    \
    #                .limit(1)                                                       \
    #                .all()
    
    
    #random_narratives = narratives1.union(narratives2).all()
    #random_narratives = random_narratives.union(narratives3).all()
    
    #random_narratives.extend(narratives1)
    #random_narratives.extend(narratives2)
    #random_narratives.extend(narratives3)
    
    
    #print(random_narratives[0])
    return render_template('random_survey.html', title=title,
        narratives = random_narratives
    )
    
@app.route("/object_names")
def object_names():
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    public_domains  = Domains.query.filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = Domains.query.filter_by(created_by=user_id)
    loadable_domains = own_domains.union(public_domains)
    
    #===
    
    public_domains  = db.session.query(Domains.domain_full_label).filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY"))
    own_domains     = db.session.query(Domains.domain_full_label).filter_by(created_by=user_id)
    lookup_a = own_domains.union(public_domains).as_scalar()
    
    #===
    
    
    object_names = db.session.query(ObjectNames) \
        .filter(ObjectNames.domain.in_(lookup_a))
    
    
    return render_template('object_names.html', title='Object Names',
        loadable_domains = loadable_domains.all(),
        object_names = object_names
    )
    
@app.route("/ChuG4O3u0X")
def ChuG4O3u0X():    

    if current_user.is_authenticated:
    
        #surveys = db.session.query(NarrativeInstance, UserActivePlanners)                                                                        \
        #                .order_by(NarrativeInstance.date_created.desc())                                                                            \
        #                .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id).filter(UserActivePlanners.status == "SUCCESS")   \
        #                .filter(NarrativeInstance.narrative_label.like("%Booker7Plots%"))                                                          \
        #                .all()
        surveys = db.session.query(Feedback1)                     \
                        .order_by(Feedback1.date_created.desc())  \
                        .all()
                        
        return render_template('ChuG4O3u0X.html', title='Survey', surveys=surveys)
         
     
    else:
        abort(403)
        
@app.route("/F9fba92c9")
def F9fba92c9():    

    if current_user.is_authenticated:
    
        #surveys = db.session.query(NarrativeInstance, UserActivePlanners)                                                                        \
        #                .order_by(NarrativeInstance.date_created.desc())                                                                            \
        #                .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id).filter(UserActivePlanners.status == "SUCCESS")   \
        #                .filter(NarrativeInstance.narrative_label.like("%Booker7Plots%"))                                                          \
        #                .all()
        surveys = db.session.query(TeachingToolSurvey)                     \
                        .order_by(TeachingToolSurvey.date_created.desc())  \
                        .all()
                        
        return render_template('F9fba92c9.html', title='Teacher Survey', surveys=surveys)
         
     
    else:
        abort(403)
        
        
#==================================================================================
 
@app.route("/ChuG4O3u0X_csv")
def ChuG4O3u0X_csv():    

    if current_user.is_authenticated:
        
        surveys = db.session.query(Feedback1)                     \
                        .order_by(Feedback1.date_created.desc())  \
                        .all()
                        
                        
        #surveys.insert(0,"sep=;")

        return render_template('ChuG4O3u0X.csv', title='Survey', surveys=surveys)
         
     
    else:
        abort(403)
        
@app.route("/F9fba92c9_csv")
def F9fba92c9_csv():    

    if current_user.is_authenticated:
        
        surveys = db.session.query(TeachingToolSurvey)                     \
                        .order_by(TeachingToolSurvey.date_created.desc())  \
                        .all()
                        
                        
        #surveys.insert(0,"sep=;")

        return render_template('F9fba92c9.csv', title='Teacher Survey', surveys=surveys)
         
     
    else:
        abort(403)
        
#===========================
# JSON/AJAX Stuff
#===========================
   
@app.route('/_run_chapter_chainer')    
def run_chapter_chainer():
    
    from chapterchainer import ChapterChainer
    
    run_id                  = request.args.get('run_id', None, type=str)
    user_id                 = request.args.get('user_id', "anonymous", type=str)
    domain_full_label       = request.args.get('domain_full_label', None)
    story_pattern           = request.args.get('story_pattern', None, type=str)
    random_story_pattern    = request.args.get('random_story_pattern', None, type=str)
    neutral_obj_count       = request.args.get('neutral_obj_count', 0, type=int)
    runtime_threshold       = request.args.get('runtime_threshold',30,type=int)
    location_map            = request.args.get('location_map', None, type=str)
    
    
    if random_story_pattern == "false":
        random_story_pattern = False
    elif  random_story_pattern == "true":
        random_story_pattern = True
    else:
        random_story_pattern = None
    chainer = ChapterChainer(
        id                  = run_id, 
        user_id             = user_id,
        domain_full_label   = domain_full_label,
        db                  = db
    )
    
    #location_file = generate_location_file(run_id,location_map)
    
    success_flag = chainer.execute(
        neutral_obj_count=neutral_obj_count,
        story_pattern=story_pattern,
        random_story_pattern=random_story_pattern,
        check_session=2,
        runtime_threshold=runtime_threshold,
        algorithm="goalgraphmultipath",
        location_map=location_map
    )
     
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)

@app.route('/_get_plan_chapter_instances')    
def get_plan_chapter_instances():
    
    run_id = request.args.get('run_id', None, type=str)
    plan_chapter_instances = db.session.query(PlanChapterInstance) \
            .filter(PlanChapterInstance.narrative_instance_id == run_id) \
            .order_by(PlanChapterInstance.chapter_number.asc()) \
            .all()
    result_str = ""
    
    for someplanchapter in plan_chapter_instances:
    
        chapter_actions = db.session.query(PlanChapterInstanceAction) \
            .filter(PlanChapterInstanceAction.chapter_id == someplanchapter.id) \
            .all()
        
        all_actions = ""
        for some_action in chapter_actions:
            all_actions += all_actions + some_action.action_string + ":"
         
        result_str +=   str(someplanchapter.id)              + "/;" + \
                        str(someplanchapter.chapter_number)  + "/;" + \
                        str(someplanchapter.chapter_address) + "/;" + \
                        str(someplanchapter.chapter_label)   + "/;" + \
                        str(someplanchapter.initial_state)   + "/;" + \
                        str(someplanchapter.final_state)     + "/;" + \
                        str(someplanchapter.parent_chapter)  + "/;" + \
                        all_actions                          + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)


@app.route('/_submit_feedback')    
def submit_feedback():

    #if current_user.is_authenticated:
    #    user_id = current_user.username
    #     
    #else:
    #    user_id = "anonymous"
    #user_id = request.args.get('user_id', None, type=str)
    
    user_id = request.args.get('user_email', 'anonymous', type=str)
    narrative_id = request.args.get('narrative_id', None, type=str)
     
    #part_01_question_01  = request.args.get('part_01_question_01' , 0, type=int)
    #part_01_question_02  = request.args.get('part_01_question_02' , None, type=str)
    #part_01_question_02a = request.args.get('part_01_question_02a', None, type=str)
    #part_01_question_03  = request.args.get('part_01_question_03' , None, type=str)
    #part_01_question_03a = request.args.get('part_01_question_03a', None, type=str)
    # 
    #part_02_question_01 = request.args.get('part_02_question_01', 0, type=int)
    # 
    #part_03_question_01 = request.args.get('part_03_question_01', None, type=str)
    #part_03_question_02 = request.args.get('part_03_question_02', None, type=str)
    #part_03_question_03 = request.args.get('part_03_question_03', None, type=str)
    
    
    question_1 = request.args.get('question_1', None, type=str)
    question_2 = request.args.get('question_2', None, type=str)
    question_3 = request.args.get('question_3', None, type=str)
    question_4 = request.args.get('question_4', None, type=str)
    question_5 = request.args.get('question_5', None, type=str)
    question_6 = request.args.get('question_6', None, type=str)
    question_7 = request.args.get('question_7', None, type=str)
    
    
    #new_review = NarrativeUserReview(
    #                    user_id                = user_id                 ,
    #                    narrative_id           = narrative_id            ,
    #                     
    #                    part_01_question_01    = part_01_question_01     ,
    #                    part_01_question_02    = part_01_question_02     ,
    #                    part_01_question_02a   = part_01_question_02a    ,
    #                    part_01_question_03    = part_01_question_03     ,
    #                    part_01_question_03a   = part_01_question_03a    ,
    #                     
    #                    part_02_question_01    = part_02_question_01     ,
    #                     
    #                    part_03_question_01    = part_03_question_01     ,
    #                    part_03_question_02    = part_03_question_02     ,
    #                    part_03_question_03    = part_03_question_03 
    #                )
    
    
    new_feedback = Feedback1(
            user_id                = user_id        ,
            narrative_id           = narrative_id   ,

            question_1             = question_1     ,
            question_2             = question_2     ,
            question_3             = question_3     ,
            question_4             = question_4     ,
            question_5             = question_5     ,
            question_6             = question_6     ,
            question_7             = question_7
        )
        
    db.session.add(new_feedback) 
    db.session.commit()
     
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)
         
#@app.route('/_get_chapter_pattern_chapters')    
#def get_chapter_pattern_chapters():
#    
#    pattern_sequence  = request.args.get('pattern_sequence' , 0, type=int)
#    chapter_pattern_chapters = db.session.query(ChapterPattern)  \
#                    .filter(ChapterPattern.pattern_sequence == pattern_sequence ) \
#                    .order_by(ChapterPattern.date_created.desc())  \
#                    .all()
#    
#    result_str = "FORTHCOMING!!!"
#    
#    
#    return jsonify(result=result_str)
         
@app.route('/_get_chapter_patterns')    
def get_chapter_patterns():
    
    domain_full_label = request.args.get('domain_full_label' , "", type=str)
    
    print(domain_full_label)
    print("-----------------")
    
    chapter_patterns = db.session.query(ChapterPattern) \
        .filter(ChapterPattern.domain == domain_full_label) \
        .with_entities(
            ChapterPattern.chapter_pattern_cat_label,
            ChapterPattern.main_label, 
            ChapterPattern.sub_label,
            ChapterPattern.name_label_str
        ) \
        .distinct()
        
    result_str = ""
    for somechapter in chapter_patterns:
        result_str +=   str(somechapter.chapter_pattern_cat_label)  + "/;" + \
                        str(somechapter.main_label)                 + "/;" + \
                        str(somechapter.sub_label)                  + "/;" + \
                        str(somechapter.name_label_str)             + "/;" + \
                        "/|"
    
    
    return jsonify(result=result_str)
         
@app.route('/_get_narrative_plan_lite')
def get_narrative_plan_lite():
    narrative_id = request.args.get('narrative_id', None, type=str)
     
#class SolutionChapterInstance(db.Model):
#    id = db.Column(db.String(128), primary_key=True)
#    narrative_instance_id = db.Column(db.Integer, db.ForeignKey('narrative_instance.id'))
#    
#    chapter_number = db.Column(db.Integer, nullable=False)
#    chapter_address = db.Column(db.String(64), nullable=False)
#    chapter_label = db.Column(db.String(128), nullable=False)
#    initial_state = db.Column(db.Text)
#    final_state = db.Column(db.Text)
#    parent_chapter = db.Column(db.Integer)
#    chapters = db.relationship('ChapterInstanceAction', backref='chapter_instance', lazy=True)
     
    chapter_nodes = PlanChapterInstance.query.order_by(PlanChapterInstance.chapter_address.asc()).filter_by(narrative_instance_id=narrative_id)
     
    result_str = ""
    for some_chapter in chapter_nodes:
         
        chapter_actions = PlanChapterInstanceAction.query.filter_by(id=some_chapter.id)
        all_actions = ""
        for some_action in some_chapter.actions:
            all_actions += all_actions + some_action.action_string + ":"
         
        result_str +=   str(some_chapter.id)                + "/;" + \
                        str(some_chapter.chapter_number)    + "/;" + \
                        str(some_chapter.chapter_address)   + "/;" + \
                        str(some_chapter.chapter_label)     + "/;" + \
                        str(some_chapter.parent_chapter)    + "/;" + \
                        all_actions                         +       \
                        "/|"
    #if result_str == "":
    #    result_str = "<None yet>"
    return jsonify(result=result_str)

@app.route('/_submit_pattern_instance')    
def submit_pattern_instance():
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"

    chapter_pattern_cat_label   = request.args.get('chapter_pattern_cat_label', None, type=str)        
    main_label                  = request.args.get('main_label', None, type=str)        
    sub_label                   = request.args.get('sub_label', None, type=str)        
    pattern_sequence            = request.args.get('pattern_sequence', None, type=str)        
    domain_full_label           = request.args.get('domain_full_label', None, type=str)        
    chapter_pattern_description = request.args.get('chapter_pattern_description', None, type=str)       
    visibility                  = request.args.get('visibility', None, type=str)        
    
    sequence_term_cat_label = [None] * 6
    sequence_term_cat_label[0]  = request.args.get('sequence_term_cat_label_01', None, type=str)        
    sequence_term_cat_label[1]  = request.args.get('sequence_term_cat_label_02', None, type=str)        
    sequence_term_cat_label[2]  = request.args.get('sequence_term_cat_label_03', None, type=str)        
    sequence_term_cat_label[3]  = request.args.get('sequence_term_cat_label_04', None, type=str)        
    sequence_term_cat_label[4]  = request.args.get('sequence_term_cat_label_05', None, type=str)        
    sequence_term_cat_label[5]  = request.args.get('sequence_term_cat_label_06', None, type=str)        
    
    series_ctr = 0
    for ctr in range(0,6):
        if sequence_term_cat_label[ctr] == "NULL":
            continue
        else:
            
            main_label_str = utility.smallify(main_label)
            sub_label_str  = utility.smallify(sub_label)
            name_label_str = chapter_pattern_cat_label + "_" + main_label_str + ("" if sub_label_str=="" else ("_" + sub_label_str))
            sequence_grouping_label = name_label_str + "_" + pattern_sequence
            series = series_ctr + 1
            pattern_full_label = sequence_grouping_label + "_" + str(series) + "_" + sequence_term_cat_label[ctr]
            
            new_chapter_pattern = ChapterPattern(
                    chapter_pattern_cat_label   = chapter_pattern_cat_label       ,
                    main_label                  = main_label                      ,
                    main_label_str              = main_label_str                  ,
                    sub_label                   = sub_label                       ,
                    sub_label_str               = sub_label_str                   ,
                    name_label_str              = name_label_str                  ,
                    vacant1                     = chapter_pattern_description     ,
                   #vacant2                     =                                 ,
                    pattern_sequence            = pattern_sequence                ,
                    sequence_grouping_label     = sequence_grouping_label         ,
                    series                      = str(series)                     ,
                    pattern_full_label          = pattern_full_label              ,
                    sequence_term_cat_label     = sequence_term_cat_label[ctr]    ,
                    sequence_term_count         = -1                              ,
                   #sequence_term_min_density   =                                 ,
                   #sequence_term_max_density   =                                 ,
                    sequence_term_min_count     = 1                               ,
                    sequence_term_max_count     = 1                               ,
                    duplicates_allowed          = "TRUE"                          ,
                   #vacant3                     =                                 ,
                    vacant4                     = user_id                         ,
                    domain                      = domain_full_label               ,
                    visibility                  = visibility                      ,
                    status                      = "CREATED"                       ,
                    created_by                  = user_id                         ,
                    last_edited_by              = user_id
            )
            db.session.add(new_chapter_pattern) 
            db.session.commit()
            
            series_ctr += 1
            
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)

@app.route('/_get_sequence_term')
def get_sequence_term():
    
    sequence_term_cat_label = request.args.get('sequence_term_cat_label', None, type=str)
    main_label              = request.args.get('main_label', None, type=str)
    main_label_str          = utility.smallify(main_label)
    sub_label               = request.args.get('sub_label', None, type=str)
    sub_label_str           = utility.smallify(sub_label)
    name_label_str          = sequence_term_cat_label + "_" + main_label_str + ("" if sub_label_str=="" else ("_" + sub_label_str))
    
    
    
    sequence_terms = db.session.query(SequenceTerms) \
                        .filter(SequenceTerms.name_label_str == name_label_str) \
                        .all()
    
    result_str = ""
    for someseqterms in sequence_terms:
        result_str +=   str(someseqterms.main_label)                     + "/;" + \
                        str(someseqterms.sub_label)                      + "/;" + \
                        str(someseqterms.term_sequence)                  + "/;" + \
                        str(someseqterms.term_sequence_grouping_label)   + "/;" + \
                        str(someseqterms.sequence_term_full_label)       + "/;" + \
                        str(someseqterms.main_object)                    + "/;" + \
                        str(someseqterms.supporting_objects)             + "/;" + \
                        str(someseqterms.intention_actor)                + "/;" + \
                        str(someseqterms.intention_full_str)             + "/;" + \
                        str(someseqterms.direct_chained_with)            + "/;" + \
                        str(someseqterms.successors)                     + "/;" + \
                        "/|"
        
    return jsonify(result=result_str)
    
@app.route('/_get_sequence_term_extended_info')
def get_sequence_term_extended_info():
    sequence_term_cat_label = request.args.get('sequence_term_cat_label', None, type=str)
    
    # Query 1
    sequence_terms_main = db.session.query(SequenceTerms) \
                    .filter(SequenceTerms.sequence_term_cat_label == sequence_term_cat_label) 
                    #.order_by(SequenceTerms.sequence_term_full_label.asc())
    #--- Subqueries
    lookup_successors = db.session.query(SequenceTerms.successors) \
                    .filter(SequenceTerms.sequence_term_cat_label == sequence_term_cat_label)
                    
    lookup_direct_chained = db.session.query(SequenceTerms.direct_chained_with) \
                    .filter(SequenceTerms.sequence_term_cat_label == sequence_term_cat_label)
                    
    lookup_all = lookup_successors.union(lookup_direct_chained).as_scalar()
    #---
    
    # Query 2
    sequence_terms_ext = db.session.query(SequenceTerms) \
                    .filter(SequenceTerms.term_sequence_grouping_label.in_(lookup_all)) 
                    #.order_by(SequenceTerms.sequence_term_full_label.asc())
                    
    # Query Union
    #sequence_terms = sequence_terms_main.union(sequence_terms_ext).all()
    sequence_terms = sequence_terms_main.all()
    
    result_str = ""
    
    for someseqterms in sequence_terms:
        result_str +=   str(someseqterms.main_label)                     + "/;" + \
                        str(someseqterms.sub_label)                      + "/;" + \
                        str(someseqterms.term_sequence)                  + "/;" + \
                        str(someseqterms.term_sequence_grouping_label)   + "/;" + \
                        str(someseqterms.sequence_term_full_label)       + "/;" + \
                        str(someseqterms.main_object)                    + "/;" + \
                        str(someseqterms.supporting_objects)             + "/;" + \
                        str(someseqterms.intention_actor)                + "/;" + \
                        str(someseqterms.intention_full_str)             + "/;" + \
                        str(someseqterms.direct_chained_with)            + "/;" + \
                        str(someseqterms.successors)                     + "/;" + \
                        "/|"
        
    return jsonify(result=result_str)

@app.route('/_get_sequence_term_category')
def get_sequence_term_category():
    sequence_term_cat_label = request.args.get('sequence_term_cat_label', None, type=str)
    #domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    existing_sequence_term_categories = db.session.query(SequenceTermCategories) \
        .filter(SequenceTermCategories.sequence_term_cat_label == sequence_term_cat_label) \
        .all()
    
    result_str = ""
    
    for someseqtermcats in existing_sequence_term_categories:
        result_str +=   str(someseqtermcats.id                      ) + "/;" + \
                        str(someseqtermcats.sequence_term_cat_label ) + "/;" + \
                        str(someseqtermcats.description             ) + "/;" + \
                        str(someseqtermcats.domain                  ) + "/;" + \
                        str(someseqtermcats.vacant2                 ) + "/;" + \
                        str(someseqtermcats.vacant3                 ) + "/;" + \
                        str(someseqtermcats.visibility              ) + "/;" + \
                        str(someseqtermcats.status                  ) + "/;" + \
                        str(someseqtermcats.created_by              ) + "/;" + \
                        "/|"
    print(sequence_term_cat_label)
    return jsonify(result=result_str)

@app.route('/_get_state_predicate_def_count_by_label')
def get_state_predicate_def_count_by_label():
    domain_id = request.args.get('domain_id', None, type=str)
    predicate_label = request.args.get('predicate_label',None)
    
    existing_predicate = db.session.query(StatePredicateDef) \
        .filter(StatePredicateDef.domain_id == domain_id) \
        .filter(StatePredicateDef.predicate_label == predicate_label) \
        .all()
    
    result_str = 0
    
    for somepred in existing_predicate:
        result_str += 1
    
    return jsonify(result=str(result_str))
    
@app.route('/_get_state_predicate_def_info')
def get_state_predicate_def_info():
    
    domain_id = request.args.get('domain_id', None, type=str)
    definition_str = request.args.get('definition_str', None, type=str)
    
    predicates = db.session.query(StatePredicateDef) \
                    .filter(StatePredicateDef.definition_str == definition_str) \
                    .filter(StatePredicateDef.domain_id == domain_id)
    
    result_str = ""
    
    for somepred in predicates.all():
        result_str +=   str(somepred.id)                                + "/;" + \
                        str(somepred.domain_id)                         + "/;" + \
                        str(somepred.predicate_label)                   + "/;" + \
                        str(somepred.definition_str)                    + "/;" + \
                        str(somepred.parameter1_label)                  + "/;" + \
                        str(somepred.parameter1_type)                   + "/;" + \
                        str(somepred.parameter1_min_instances)          + "/;" + \
                        str(somepred.parameter1_max_instances)          + "/;" + \
                        str(somepred.parameter2_label)                  + "/;" + \
                        str(somepred.parameter2_type)                   + "/;" + \
                        str(somepred.parameter2_min_instances)          + "/;" + \
                        str(somepred.parameter2_max_instances)          + "/;" + \
                        str(somepred.parameter3_label)                  + "/;" + \
                        str(somepred.parameter3_type)                   + "/;" + \
                        str(somepred.parameter3_min_instances)          + "/;" + \
                        str(somepred.parameter3_max_instances)          + "/;" + \
                        str(somepred.parameter4_label)                  + "/;" + \
                        str(somepred.parameter4_type)                   + "/;" + \
                        str(somepred.parameter4_min_instances)          + "/;" + \
                        str(somepred.parameter4_max_instances)          + "/;" + \
                        str(somepred.parameter5_label)                  + "/;" + \
                        str(somepred.parameter5_type)                   + "/;" + \
                        str(somepred.parameter5_min_instances)          + "/;" + \
                        str(somepred.parameter5_max_instances)          + "/;" + \
                        str(somepred.parameter6_label)                  + "/;" + \
                        str(somepred.parameter6_type)                   + "/;" + \
                        str(somepred.parameter6_min_instances)          + "/;" + \
                        str(somepred.parameter6_max_instances)          + "/;" + \
                        str(somepred.primary_object)                    + "/;" + \
                        str(somepred.secondary_object)                  + "/;" + \
                        str(somepred.humanreadable_string1)             + "/;" + \
                        str(somepred.humanreadable_string2)             + "/;" + \
                        str(somepred.humanreadable_string3)             + "/;" + \
                        str(somepred.humanreadable_string4)             + "/;" + \
                        str(somepred.function_string)                   + "/;" + \
                        str(somepred.initial_state_affinity)            + "/;" + \
                        str(somepred.initial_intention_affinity)        + "/;" + \
                        str(somepred.mutability)                        + "/;" + \
                        str(somepred.visibility)                        + "/;" + \
                        str(somepred.attribute1)                        + "/;" + \
                        str(somepred.attribute2)                        + "/;" + \
                        str(somepred.attribute3)                        + "/;" + \
                        str(somepred.status)                            + "/;" + \
                        "/|"                                                            
        print(result_str)
    return jsonify(result=result_str)
    
@app.route('/_get_last_term_sequence')
def get_last_term_sequence():

    sequence_term_cat_label = request.args.get('sequence_term_cat_label', None, type=str)
    
    term_sequence_num = db.session.query(db.func.max(SequenceTerms.term_sequence)) \
                            .filter(SequenceTerms.sequence_term_cat_label == sequence_term_cat_label) \
                            .first()
                            
    if term_sequence_num[0] is None:
        last_term_sequence = 0
    else:
        last_term_sequence = str(term_sequence_num[0])
        
    return jsonify(result=last_term_sequence)
    
@app.route('/_add_sequence_term_category')
def add_sequence_term_category():
    domain_full_label                   = request.args.get('domain_full_label', None, type=str)
    visibility                          = request.args.get('visibility', None, type=str)
    sequence_term_cat_label             = request.args.get('sequence_term_cat_label', None, type=str)
    main_label                          = request.args.get('main_label', None, type=str)
    main_label_str                      = utility.smallify(main_label)
    sub_label                           = request.args.get('sub_label', None, type=str)
    sub_label_str                       = utility.smallify(sub_label)
    name_label_str                      = sequence_term_cat_label + "_" + main_label_str + ("" if sub_label_str=="" else ("_" + sub_label_str))
    term_sequence                       = request.args.get('term_sequence', None, type=str)
    term_sequence_grouping_label        = name_label_str + "_" + utility.zeroStringPad(term_sequence,2)
    series                              = request.args.get('series', None, type=str)
    sequence_term_full_label            = term_sequence_grouping_label + "_" + series
    
    main_object                         = request.args.get('main_object', None, type=str)
    supporting_objects                  = request.args.get('supporting_objects', None, type=str)
    intention_actor                     = request.args.get('intention_actor', None, type=str)
    intention_target_state_predicate    = request.args.get('intention_target_state_predicate', None, type=str)
    intention_full_str                  = request.args.get('intention_full_str', None, type=str)
    prerequisite_target_predicates      = request.args.get('prerequisite_target_predicates', None, type=str)
    
    new_sequence_term = SequenceTerms(
        sequence_term_cat_label             = sequence_term_cat_label           ,
        main_label                          = main_label                        ,
        main_label_str                      = main_label_str                    ,
        sub_label                           = sub_label                         ,
        sub_label_str                       = sub_label_str                     ,
        name_label_str                      = name_label_str                    ,
        term_sequence                       = term_sequence                     ,
        term_sequence_grouping_label        = term_sequence_grouping_label      ,
        series                              = series                            ,
        sequence_term_full_label            = sequence_term_full_label          ,
        #is_flavor                           =                                  ,
        #is_variant                          =                                  ,
        #vacant1                             =                                  ,
        main_object                         = main_object                       ,
        supporting_objects                  = supporting_objects                ,
        intention_actor                     = intention_actor                   ,
        intention_target_state_predicate    = intention_target_state_predicate  ,
        intention_full_str                  = intention_full_str                ,
        intention_type                      = ""                                ,
        predecessor_terms                   = ""                                ,
        direct_chained_with                 = ""                                ,
        successors                          = ""                                ,
        prerequisite_present_predicates     = ""                                ,
        prerequisite_target_predicates      = prerequisite_target_predicates    ,
        required_objects                    = ""                                ,
        in_chapter_pattern                  = ""                                ,
        vacant3                             = "CUSTOM"                          ,
        notes                               = ""                                ,
        status                              = "CREATED"
    )
    db.session.add(new_sequence_term) 
    db.session.commit()
    
    
    existing_sequence_term_category = db.session.query(SequenceTermCategories) \
        .filter(SequenceTermCategories.sequence_term_cat_label == sequence_term_cat_label) \
        .filter(SequenceTermCategories.domain == domain_full_label) \
        .all()
        
    if not existing_sequence_term_category:
        new_sequence_term_category = SequenceTermCategories(
            sequence_term_cat_label = sequence_term_cat_label,
            #description             = description,
            domain                  = domain_full_label,
            visibility              = visibility,
            status                  = "ACTIVE",
            created_by              = current_user.username,
            last_edited_by          = current_user.username
        )
        db.session.add(new_sequence_term_category) 
        db.session.commit()
        
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        flash(f'Successful','success')
        return jsonify(result=sequence_term_full_label)

@app.route('/_get_domain_info_from_label')
def get_domain_info_from_label():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    result_str = ""
    
    domain_result = db.session.query(Domains) \
                    .filter(Domains.domain_full_label == domain_full_label) \
                    .all()
                    
    for somedomain in domain_result:
        result_str +=   str(somedomain.id)                  + "/;" + \
                        str(somedomain.category)            + "/;" + \
                        str(somedomain.category_str)        + "/;" + \
                        str(somedomain.sub_label)           + "/;" + \
                        str(somedomain.sub_label_str)       + "/;" + \
                        str(somedomain.series)              + "/;" + \
                        str(somedomain.domain_full_label)   + "/;" + \
                        str(somedomain.readable_label)      + "/;" + \
                        str(somedomain.author_notes)        + "/;" + \
                        str(somedomain.visibility)          + "/;" + \
                        str(somedomain.created_by)          + "/;" + \
                        str(somedomain.last_edited_by)      + "/;" + \
                        str(somedomain.status)              + "/;" + \
                        "/|"
    return jsonify(result=result_str)
        
@app.route('/_get_objecttypes')
def get_objecttypes():
    
    domain_id = request.args.get('domain_id', None, type=str)
    result_str = ""
    
    objecttypes = db.session.query(ObjectTypes) \
                    .filter(ObjectTypes.domain_id == domain_id) \
                    .order_by(ObjectTypes.object_type.asc()) \
                    .all()
                    
    for someobjtype in objecttypes:
        result_str +=   str(someobjtype.id)             + "/;" + \
                        str(someobjtype.domain_id)      + "/;" + \
                        str(someobjtype.object_type)    + "/;" + \
                        str(someobjtype.parent_type)    + "/;" + \
                        str(someobjtype.default_flag)   + "/;" + \
                        str(someobjtype.status)         + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
    
@app.route('/_get_objecttypes2')
def get_objecttypes2():
    
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    result_str = ""
    
    domain_id = db.session.query(Domains.id) \
        .filter(Domains.domain_full_label == domain_full_label) \
        .first()
        
    objecttypes = db.session.query(ObjectTypes) \
                    .filter(ObjectTypes.domain_id == domain_id[0]) \
                    .order_by(ObjectTypes.object_type.asc()) \
                    .all()
                    
    for someobjtype in objecttypes:
        result_str +=   str(someobjtype.id)             + "/;" + \
                        str(someobjtype.domain_id)      + "/;" + \
                        str(someobjtype.object_type)    + "/;" + \
                        str(someobjtype.parent_type)    + "/;" + \
                        str(someobjtype.default_flag)   + "/;" + \
                        str(someobjtype.status)         + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
   
@app.route('/_add_sequence_term_object')
def add_sequence_term_object():
    
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    variable_name = "?" + request.args.get('variable_name', None, type=str)
    object_type = request.args.get('object_type', None, type=str)
    
    existing_seq_term_objects = db.session.query(SequenceTermObjects) \
                        .filter(SequenceTermObjects.variable_name == variable_name) \
                        .filter(SequenceTermObjects.domain == domain_full_label) \
                        .all()
    
    if existing_seq_term_objects:
        for someobj in existing_seq_term_objects:
            someobj.object_type = object_type
    else:
        new_seq_term_object = SequenceTermObjects(
            domain = domain_full_label,
            variable_name = variable_name,
            object_type = object_type
        )
        db.session.add(new_seq_term_object)
    
    db.session.commit()
    
    result_str = ""
    return jsonify(result=result_str)
    
@app.route('/_add_sequence_term_actor')
def add_sequence_term_actor():
    
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    variable_name = "?" + request.args.get('variable_name', None, type=str)
    object_type = request.args.get('object_type', None, type=str)
    
    existing_seq_term_actors = db.session.query(SequenceTermActors) \
                        .filter(SequenceTermActors.variable_name == variable_name) \
                        .filter(SequenceTermActors.domain == domain_full_label) \
                        .all()
    
    if existing_seq_term_actors:
        for someobj in existing_seq_term_actors:
            someobj.object_type = object_type
    else:
        new_seq_term_object = SequenceTermActors(
            domain = domain_full_label,
            variable_name = variable_name,
            object_type = object_type
        )
        db.session.add(new_seq_term_object)
    
    db.session.commit()
    
    result_str = ""
    return jsonify(result=result_str)
    
@app.route('/_get_objecttypes_of_type')
def get_objecttypes_of_type():
    
    def typeIsOfType(child_type, ancestor_type, type_repository):
        if child_type == ancestor_type:
            return True
        for sometype in type_repository:
            if child_type == sometype[0]:
                print(child_type)
                if sometype[1] == ancestor_type:
                    return True
                else:
                    return typeIsOfType(sometype[1], ancestor_type, type_repository)
        
        return False
    
    domain_id = request.args.get('domain_id', None, type=str)
    ancestor_type = request.args.get('ancestor_type', None, type=str)
    result_str = ""
    
    objecttypes = db.session.query(ObjectTypes) \
                    .filter(ObjectTypes.domain_id == domain_id) \
                    .order_by(ObjectTypes.object_type.asc()) \
                    .all()
    
    all_obj_types = []
    
    for someobjtype in objecttypes:
        all_obj_types.append([someobjtype.object_type, someobjtype.parent_type])
    
    for someobjtype in objecttypes:
    
        if typeIsOfType(someobjtype.object_type,ancestor_type,all_obj_types):
            
            result_str +=   str(someobjtype.id)             + "/;" + \
                            str(someobjtype.domain_id)      + "/;" + \
                            str(someobjtype.object_type)    + "/;" + \
                            str(someobjtype.parent_type)    + "/;" + \
                            str(someobjtype.default_flag)   + "/;" + \
                            str(someobjtype.status)         + "/;" + \
                            "/|"
                            
    return jsonify(result=result_str)

@app.route('/_submit_action_def_pilot')
def submit_action_def_pilot():
    domain_id           = request.args.get('domain_id', None, type=str)
    domain_full_label   = request.args.get('domain_full_label', None, type=str)
    action_label        = request.args.get('action_label', None, type=str)
    
    action_full_label = domain_full_label + "_" + action_label
    
    existing_action = db.session.query(ActionDef) \
                        .filter(ActionDef.action_full_label == action_full_label) \
                        .first()
    
    if existing_action:
        #db.session.commit()
        action_id = existing_action.id
        
    else:
        
        new_action_def = ActionDef(
            domain_id           = domain_id         ,
            domain_full_label   = domain_full_label ,
            action_label        = action_label      ,
            action_full_label   = action_full_label ,
            function_str        = ""                ,
            status              = "DRAFT"
        )
        
        db.session.add(new_action_def)
        db.session.commit()
        action_id = new_action_def.id
    
    success_flag = True
     
    #flash(f'Successful','success')
    return jsonify(result=action_id)

@app.route('/_add_action_parameter')
def add_action_parameter():
    
    action_full_label   = request.args.get('action_full_label', None, type=str)
    parameter_label     = request.args.get('parameter_label', None, type=str)
    parameter_type      = request.args.get('parameter_type', None, type=str)
    parameter_order     = request.args.get('parameter_order', None, type=str)
    
    existing_parameters = db.session.query(Action_Parameters) \
                        .filter(Action_Parameters.action_full_label == action_full_label) \
                        .filter(Action_Parameters.parameter_order == parameter_order) \
                        .all()
    
    if existing_parameters:
        for existing_parameter in existing_parameters:
            
            prev_def_str = "['"+existing_parameter.parameter_label+"', '"+existing_parameter.parameter_type+"']"
            new_def_str = "['?"+parameter_label+"', '"+parameter_type+"']"
            
            # 1. Check existing instances in the preconditions and effects
            try:
                print("[>>>] Search: " + action_full_label)
                existing_action_predicates = db.session.query(Action_Predicates) \
                    .filter(Action_Predicates.action_full_label == action_full_label) \
                    .all()
                
                for somepredicate in existing_action_predicates:
                    somepredicate.predicate_raw = somepredicate.predicate_raw.replace(prev_def_str,new_def_str)
                db.session.commit()
                
            except Exception:
                print("AAAAAAAAAAAAA")
                pass 
            
            # 2. Update the action definition
            try:
                #print("[>>>] Search: " + action_full_label)
                existing_action = db.session.query(ActionDef) \
                    .filter(ActionDef.action_full_label == action_full_label) \
                    .first()
                
                # 2.1 ActionDef precondition_str
                existing_action.precondition_str = existing_action.precondition_str.replace(prev_def_str,new_def_str)
                
                # 2.2 ActionDef effect_str
                existing_action.effect_str = existing_action.effect_str.replace(prev_def_str,new_def_str)
                db.session.commit()
                
                # 2.3 ActionDef human readable strings
                existing_action.humanreadable_string1 = existing_action.humanreadable_string1.replace(existing_parameter.parameter_label, "?"+parameter_label)
                existing_action.humanreadable_string2 = existing_action.humanreadable_string2.replace(existing_parameter.parameter_label, "?"+parameter_label)
                existing_action.humanreadable_string3 = existing_action.humanreadable_string3.replace(existing_parameter.parameter_label, "?"+parameter_label)
                existing_action.humanreadable_string4 = existing_action.humanreadable_string4.replace(existing_parameter.parameter_label, "?"+parameter_label)
                
            except Exception:
                pass
            
            existing_parameter.action_full_label   = action_full_label
            existing_parameter.parameter_label     = "?"+parameter_label  
            existing_parameter.parameter_type      = parameter_type
            existing_parameter.parameter_order     = parameter_order
            db.session.commit()
    else:
        new_parameter = Action_Parameters(
            action_full_label   = action_full_label ,
            parameter_label     = "?"+parameter_label   ,
            parameter_type      = parameter_type    ,
            parameter_order     = parameter_order  
        )
        db.session.add(new_parameter)
        db.session.commit()
    
    
    
    return jsonify(result="")
    
@app.route('/_delete_action_parameter')
def delete_action_parameter():
    action_full_label   = request.args.get('action_full_label', None, type=str)
    parameter_order     = request.args.get('parameter_order', None, type=str)
    
    existing_parameters = db.session.query(Action_Parameters) \
                        .filter(Action_Parameters.action_full_label == action_full_label) \
                        .filter(Action_Parameters.parameter_order == parameter_order) \
                        .all()
    for existing_parameter in existing_parameters:
        db.session.delete(existing_parameter)
        db.session.commit()
    
    #if existing_parameter:
    #    delete_parameter = Action_Parameters(
    #        action_full_label   = action_full_label ,
    #        parameter_order     = parameter_order  
    #    )
    #    db.session.delete(delete_parameter)
    #    db.session.commit()
            
    return jsonify(result="")
    
@app.route('/_add_action_predicate')
def add_action_predicate():
    action_full_label   = request.args.get('action_full_label', None, type=str)
    type                = request.args.get('type', None, type=str)
    predicate_raw       = request.args.get('predicate_raw', None, type=str)
   #predicate_order     = request.args.get('predicate_order', None, type=str)
    
    last_order = db.session.query(db.func.max(Action_Predicates.predicate_order)) \
                    .filter(Action_Predicates.action_full_label == action_full_label) \
                    .filter(Action_Predicates.type == type) \
                    .first()
                    
    if last_order[0] is not None:
        predicate_order = int(last_order[0]) + 1
    else:
        predicate_order = 1
        
    #   ADD
    new_action_predicate = Action_Predicates(
        action_full_label   = action_full_label ,
        type                = type              ,
        predicate_raw       = predicate_raw     ,
        predicate_order     = predicate_order
    )
    
    db.session.add(new_action_predicate) 
    db.session.commit()
    
    result_str = ""
    result_str +=   str(new_action_predicate.id)                        + "/;" + \
                    str(new_action_predicate.action_full_label)         + "/;" + \
                    str(new_action_predicate.type)                      + "/;" + \
                    str(new_action_predicate.predicate_def_id)          + "/;" + \
                    str(new_action_predicate.predicate_instance_id)     + "/;" + \
                    str(new_action_predicate.predicate_raw)             + "/;" + \
                    str(new_action_predicate.predicate_function_str)    + "/;" + \
                    str(new_action_predicate.predicate_order)           + "/;" + \
                    "/|"
    return jsonify(result=result_str)

@app.route('/_delete_action_predicate')
def delete_action_predicate():
    
    predicate_id       = request.args.get('predicate_id', None, type=str)
    existing_predicate = db.session.query(Action_Predicates) \
                            .filter(Action_Predicates.id == predicate_id) \
                            .first()

    db.session.delete(existing_predicate)
    db.session.commit()
    
    return jsonify(result="")

@app.route('/_get_action_def_count_by_label')
def get_action_def_count_by_label():
    domain_id = request.args.get('domain_id', None, type=str)
    action_label = request.args.get('action_label',None)
    
    existing_actions = db.session.query(ActionDef) \
        .filter(ActionDef.domain_id == domain_id) \
        .filter(ActionDef.action_label == action_label) \
        .all()
    
    print("=============")
    print(domain_id)
    print(action_label)
    print("=============")
    result_str = 0
    
    for someaction in existing_actions:
        result_str += 1
    
    return jsonify(result=str(result_str))

@app.route('/_get_action_details')
def get_action_details():

    action_full_label = request.args.get('action_full_label', None, type=str)
    domain_id = request.args.get('domain_id',None,type=str)
    result_str = ""
    
    action_details = db.session.query(ActionDef) \
                            .filter(ActionDef.action_full_label == action_full_label) \
                            .filter(ActionDef.domain_id == domain_id)
                           #.all()
    
    for someaction in action_details:
        result_str +=   str(someaction.id)                      + "/;" + \
                        str(someaction.action_label)            + "/;" + \
                        str(someaction.agents1_label)           + "/;" + \
                        str(someaction.agents1_type)            + "/;" + \
                        str(someaction.agents2_label)           + "/;" + \
                        str(someaction.agents2_type)            + "/;" + \
                        str(someaction.agents3_label)           + "/;" + \
                        str(someaction.agents3_type)            + "/;" + \
                        str(someaction.agents4_label)           + "/;" + \
                        str(someaction.agents4_type)            + "/;" + \
                        str(someaction.humanreadable_string1)   + "/;" + \
                        str(someaction.humanreadable_string2)   + "/;" + \
                        str(someaction.humanreadable_string3)   + "/;" + \
                        str(someaction.humanreadable_string4)   + "/;" + \
                        "/|"
        
    return jsonify(result=result_str)

@app.route('/_get_action_parameters')
def get_action_parameters():
    
    action_full_label = request.args.get('action_full_label', None, type=str)
    result_str = ""
    
    action_parameters = db.session.query(Action_Parameters) \
                            .filter(Action_Parameters.action_full_label == action_full_label) \
                            .order_by(Action_Parameters.parameter_order.asc())
                           #.all()
    
    for someparam in action_parameters:
        result_str +=   str(someparam.id)                   + "/;" + \
                        str(someparam.action_full_label)    + "/;" + \
                        str(someparam.parameter_label)      + "/;" + \
                        str(someparam.parameter_type)       + "/;" + \
                        str(someparam.parameter_order)      + "/;" + \
                        "/|"
    return jsonify(result=result_str)
    
@app.route('/_get_action_predicates')
def get_action_predicates():
    
    action_full_label = request.args.get('action_full_label', None, type=str)
    predicate_type = request.args.get('predicate_type', None, type=str)
    
    copy_to_action_full_label = request.args.get('copy_to_action_full_label', None, type=str)
    
    result_str = ""
    
    action_predicates = db.session.query(Action_Predicates) \
        .filter(Action_Predicates.action_full_label == action_full_label) \
        .filter(Action_Predicates.type.like("%"+predicate_type+"%")) \
        .order_by(Action_Predicates.predicate_order.asc())
                           #.all()
    
    if copy_to_action_full_label == "":
        output_result = action_predicates
    else:
        for somepred in action_predicates:
            
            new_action_predicate = Action_Predicates(
                action_full_label       = copy_to_action_full_label        ,
                type                    = somepred.type                    ,
                predicate_def_id        = somepred.predicate_def_id        ,
                predicate_instance_id   = somepred.predicate_instance_id   ,
                predicate_raw           = somepred.predicate_raw           ,
                predicate_function_str  = somepred.predicate_function_str  ,
                predicate_order         = somepred.predicate_order         
            )
            db.session.add(new_action_predicate) 
            db.session.commit()
        
        output_result = db.session.query(Action_Predicates) \
            .filter(Action_Predicates.action_full_label == copy_to_action_full_label) \
            .filter(Action_Predicates.type.like("%"+predicate_type+"%")) \
            .order_by(Action_Predicates.predicate_order.asc())
        
    for somepred in output_result:
        result_str +=   str(somepred.id)                        + "/;" + \
                        str(somepred.action_full_label)         + "/;" + \
                        str(somepred.type)                      + "/;" + \
                        str(somepred.predicate_def_id)          + "/;" + \
                        str(somepred.predicate_instance_id)     + "/;" + \
                        str(somepred.predicate_raw)             + "/;" + \
                        str(somepred.predicate_function_str)    + "/;" + \
                        str(somepred.predicate_order)           + "/;" + \
                        "/|"
    return jsonify(result=result_str)

@app.route('/_update_action_status')
def update_action_status():
    
    action_full_label = request.args.get('action_full_label', None, type=str)
    status = request.args.get('status', None, type=str)
    function_str = request.args.get('function_str', None, type=str)
    
    agents1_label = request.args.get('agents1_label', "", type=str)
    agents1_type  = request.args.get('agents1_type', "", type=str)
    agents2_label = request.args.get('agents2_label', "", type=str)
    agents2_type  = request.args.get('agents2_type', "", type=str)
    agents3_label = request.args.get('agents3_label', "", type=str)
    agents3_type  = request.args.get('agents3_type', "", type=str)
    agents4_label = request.args.get('agents4_label', "", type=str)
    agents4_type  = request.args.get('agents4_type', "", type=str)
    
    humanreadable_string1 = request.args.get('humanreadable_string1', None, type=str)
    humanreadable_string2 = request.args.get('humanreadable_string2', None, type=str)
    humanreadable_string3 = request.args.get('humanreadable_string3', None, type=str)
    humanreadable_string4 = request.args.get('humanreadable_string4', None, type=str)
    
    existing_action = db.session.query(ActionDef) \
                        .filter(ActionDef.action_full_label == action_full_label) \
                        .first()
                        
    existing_action.status = status
    #db.session.commit()
    
    # ===== AGENTS
    if agents1_label != "":
        existing_action.agents1_label = "?" + agents1_label
        existing_action.agents1_type = agents1_type
    else:
        existing_action.agents1_label = ""
        existing_action.agents1_type = ""
    
    if agents2_label != "":
        existing_action.agents2_label = "?" + agents2_label
        existing_action.agents2_type = agents2_type
    else:
        existing_action.agents2_label = ""
        existing_action.agents2_type = ""

    if agents3_label != "":
        existing_action.agents3_label = "?" + agents3_label
        existing_action.agents3_type = agents3_type
    else:
        existing_action.agents3_label = ""
        existing_action.agents3_type = ""

    if agents4_label != "":
        existing_action.agents4_label = "?" + agents4_label
        existing_action.agents4_type = agents4_type
    else:
        existing_action.agents4_label = ""
        existing_action.agents4_type = ""

    
    # ===== FUNCTION STRING
    existing_action.function_str = function_str
    
    # ===== PRECONDITIONS
    action_precons = db.session.query(Action_Predicates) \
        .filter(Action_Predicates.action_full_label == action_full_label) \
        .filter(Action_Predicates.type.like("%PRECON%")) \
        .all()

    precondition_str = "['and', ["
    
    first_flag = True
    has_precondition = False
    for someprecon in action_precons:
        has_precondition = True
        if first_flag:
            first_flag = False
            precondition_str += someprecon.predicate_raw
        else:
            precondition_str += ", " + someprecon.predicate_raw
    precondition_str += "]]"
    
    if has_precondition:
        existing_action.precondition_str = precondition_str
    else:
        existing_action.precondition_str = "[[['true']]]"
    # ===== EFFECTS
    action_effects = db.session.query(Action_Predicates) \
        .filter(Action_Predicates.action_full_label == action_full_label) \
        .filter(Action_Predicates.type.like("%EFFECT%")) \
        .all()

    effect_str = "['and', ["
    
    first_flag = True
    for someeffect in action_effects:
        if first_flag:
            first_flag = False
            effect_str += someeffect.predicate_raw
        else:
            effect_str += ", " + someeffect.predicate_raw
    effect_str += "]]"
    
    existing_action.effect_str = effect_str
    
    if humanreadable_string1 != "":
        existing_action.humanreadable_string1 = "\"" + humanreadable_string1.replace("\"","") + "\""
    else:
        existing_action.humanreadable_string1 = ""
    if humanreadable_string2 != "":
        existing_action.humanreadable_string2 = "\"" + humanreadable_string2.replace("\"","") + "\""
    else:
        existing_action.humanreadable_string2 = ""
    if humanreadable_string3 != "":
        existing_action.humanreadable_string3 = "\"" + humanreadable_string3.replace("\"","") + "\""
    else:
        existing_action.humanreadable_string3 = ""
    if humanreadable_string4 != "":
        existing_action.humanreadable_string4 = "\"" + humanreadable_string4.replace("\"","") + "\""
    else:
        existing_action.humanreadable_string4 = ""
    
    # ===== COMMIT
    db.session.commit()
    
    
    return jsonify(result="")
    
@app.route('/_delete_objecttype')
def delete_objecttype():
    pass
    
@app.route('/_delete_statepredicate')
def delete_statepredicate():
    pass
    
@app.route('/_delete_action')
def delete_action():
    action_full_label = request.args.get('action_full_label', None, type=str)
    
    # Delete Parameters
    print("Delete Parameters")
    existing_parameters = db.session.query(Action_Parameters) \
                        .filter(Action_Parameters.action_full_label == action_full_label) \
                        .all()
    for some_param in existing_parameters:
        db.session.delete(some_param)
        db.session.commit()
    
    # Delete Predicates
    print("Delete Predicates")
    existing_predicates = db.session.query(Action_Predicates) \
                        .filter(Action_Predicates.action_full_label == action_full_label) \
                        .all()
    for some_pred in existing_predicates:
        db.session.delete(some_pred)
        db.session.commit()
    
    # Delete Action
    print("Delete Action")
    existing_action = db.session.query(ActionDef) \
                        .filter(ActionDef.action_full_label == action_full_label) \
                        .first()
    if existing_action:
        db.session.delete(existing_action)
        db.session.commit()
        
    return jsonify(result="")
    
@app.route('/_get_sequence_term_actors')
def get_sequence_term_actors():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    intention_actors = db.session.query(SequenceTermActors) \
        .filter(SequenceTermActors.domain == domain_full_label) \
        .all()
    
    result_str = ""
    
    for someactor in intention_actors:
        result_str +=   str(someactor.id)               + "/;" + \
                        str(someactor.variable_name)    + "/;" + \
                        str(someactor.object_type)      + "/;" + \
                        str(someactor.domain)           + "/;" + \
                        "/|"
    return jsonify(result=result_str)
    
@app.route('/_get_sequence_term_objects')
def get_sequence_term_objects():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    intention_objects = db.session.query(SequenceTermObjects) \
        .filter(SequenceTermObjects.domain == domain_full_label) \
        .all()
    
    result_str = ""
    
    for someobj in intention_objects:
        result_str +=   str(someobj.id)               + "/;" + \
                        str(someobj.variable_name)    + "/;" + \
                        str(someobj.object_type)      + "/;" + \
                        str(someobj.domain)           + "/;" + \
                        "/|"
    return jsonify(result=result_str)
    
@app.route('/_get_sequence_term_categories_by_domainlabel')
def get_sequence_term_categories_by_domainlabel():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    sequence_term_cats = db.session.query(SequenceTermCategories) \
        .filter(SequenceTermCategories.domain == domain_full_label) \
        .all()
        
    result_str = ""
    
    for sometermcat in sequence_term_cats:
        result_str +=   str(sometermcat.id)                         + "/;" + \
                        str(sometermcat.sequence_term_cat_label)    + "/;" + \
                        str(sometermcat.description)                + "/;" + \
                        str(sometermcat.domain)                     + "/;" + \
                        str(sometermcat.visibility)                 + "/;" + \
                        str(sometermcat.status)                     + "/;" + \
                        str(sometermcat.created_by)                 + "/;" + \
                        str(sometermcat.last_edited_by)             + "/;" + \
                        "/|"
                        
    return jsonify(result=result_str)
                        
@app.route('/_get_sequence_terms_by_domainlabel')
def get_sequence_terms_by_domainlabel():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    sequence_term_cats = db.session.query(SequenceTermCategories.sequence_term_cat_label) \
        .filter(SequenceTermCategories.domain == domain_full_label) \
        .as_scalar()
        
    sequence_terms = db.session.query(SequenceTerms) \
        .filter(SequenceTerms.sequence_term_cat_label.in_(sequence_term_cats)) \
        .all()
    
    result_str = ""
    
    for someterm in sequence_terms:
        result_str +=   str(id)                                 + "/;" + \
                        str(sequence_term_cat_label)            + "/;" + \
                        str(main_label)                         + "/;" + \
                        str(main_label_str)                     + "/;" + \
                        str(sub_label)                          + "/;" + \
                        str(sub_label_str)                      + "/;" + \
                        str(name_label_str)                     + "/;" + \
                        str(term_sequence)                      + "/;" + \
                        str(term_sequence_grouping_label)       + "/;" + \
                        str(series)                             + "/;" + \
                        str(sequence_term_full_label)           + "/;" + \
                        str(is_flavor)                          + "/;" + \
                        str(is_variant)                         + "/;" + \
                        str(main_object)                        + "/;" + \
                        str(supporting_objects)                 + "/;" + \
                        str(intention_actor)                    + "/;" + \
                        str(intention_target_state_predicate)   + "/;" + \
                        str(intention_full_str)                 + "/;" + \
                        str(intention_type)                     + "/;" + \
                        str(predecessor_terms)                  + "/;" + \
                        str(direct_chained_with)                + "/;" + \
                        str(successors)                         + "/;" + \
                        str(prerequisite_present_predicates)    + "/;" + \
                        str(prerequisite_target_predicates)     + "/;" + \
                        str(required_objects)                   + "/;" + \
                        str(in_chapter_pattern)                 + "/;" + \
                        "/|"
                        
    return jsonify(result=result_str)
    
@app.route('/_get_sequence_terms_by_category')
def get_sequence_terms_by_category():
    #domain_full_label = request.args.get('domain_full_label', None, type=str)
    sequence_term_cat_label = request.args.get('sequence_term_cat_label', None, type=str)
    
    #sequence_term_cats = db.session.query(SequenceTermCategories.sequence_term_cat_label) \
    #    .filter(SequenceTermCategories.domain == domain_full_label) \
    #    .filter(SequenceTermCategories.sequence_term_cat_label == sequence_term_cat_label) \
    #    .as_scalar()
    
    sequence_terms = db.session.query(SequenceTerms) \
        .filter(SequenceTerms.sequence_term_cat_label == sequence_term_cat_label) \
        .all()
    
    result_str = ""
   
    for someterm in sequence_terms:
        result_str +=   str(someterm.id)                                 + "/;" + \
                        str(someterm.sequence_term_cat_label)            + "/;" + \
                        str(someterm.main_label)                         + "/;" + \
                        str(someterm.main_label_str)                     + "/;" + \
                        str(someterm.sub_label)                          + "/;" + \
                        str(someterm.sub_label_str)                      + "/;" + \
                        str(someterm.name_label_str)                     + "/;" + \
                        str(someterm.term_sequence)                      + "/;" + \
                        str(someterm.term_sequence_grouping_label)       + "/;" + \
                        str(someterm.series)                             + "/;" + \
                        str(someterm.sequence_term_full_label)           + "/;" + \
                        str(someterm.is_flavor)                          + "/;" + \
                        str(someterm.is_variant)                         + "/;" + \
                        str(someterm.main_object)                        + "/;" + \
                        str(someterm.supporting_objects)                 + "/;" + \
                        str(someterm.intention_actor)                    + "/;" + \
                        str(someterm.intention_target_state_predicate)   + "/;" + \
                        str(someterm.intention_full_str)                 + "/;" + \
                        str(someterm.intention_type)                     + "/;" + \
                        str(someterm.predecessor_terms)                  + "/;" + \
                        str(someterm.direct_chained_with)                + "/;" + \
                        str(someterm.successors)                         + "/;" + \
                        str(someterm.prerequisite_present_predicates)    + "/;" + \
                        str(someterm.prerequisite_target_predicates)     + "/;" + \
                        str(someterm.required_objects)                   + "/;" + \
                        str(someterm.in_chapter_pattern)                 + "/;" + \
                        "/|"
    print(result_str)
    return jsonify(result=result_str)
    
@app.route('/_get_state_predicates_defnstr')
def get_state_predicates_defnstr():
    domain_id = request.args.get('domain_id', None, type=str)
    
    state_predicates = db.session.query(StatePredicateDef) \
        .filter(StatePredicateDef.domain_id == domain_id) \
        .order_by(StatePredicateDef.predicate_label.asc()) \
        .all()
    
    result_str = ""
    
    for somepred in state_predicates:
        result_str +=   str(somepred.predicate_label)       + "/;" + \
                        str(somepred.definition_str)        + "/;" + \
                        str(somepred.humanreadable_string1) + "/;" + \
                        "/|"
                        
    return jsonify(result=result_str)
    

@app.route('/_get_domain_statepredicate_graph')
def get_domain_statepredicate_graph():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    domain_id = db.session.query(Domains) \
        .filter(Domains.domain_full_label == domain_full_label) \
        .first().id
    
    precon_mode = request.args.get('precon_mode', None, type=str)
    effect_mode = request.args.get('precon_mode', None, type=str)
    # 0. Mode:
    #   pos or neg
    
    print(domain_id)
    print("======================")
    
    nodes = ""
    edges = ""
    
    # 1. Nodes
    state_predicates = db.session.query(StatePredicateDef) \
        .filter(StatePredicateDef.domain_id == domain_id) \
        .all()
    
    for some_predicate in state_predicates:
        new_node = some_predicate.predicate_label
        nodes += new_node + "/;"
        
    # 2. Edges
    if precon_mode == "pos":
        action_pred_type = "POS_PRECON"
    if precon_mode == "neg":
        action_pred_type = "NEG_PRECON"
        
    preconditions = db.session.query(ActionDef) \
        .filter(ActionDef.action_full_label.like(domain_full_label+"%")) \
        .filter(ActionDef.type == action_pred_type)

    effects = db.session.query(ActionDef) \
        .filter(ActionDef.action_full_label.like(domain_full_label+"%")) \
        .filter(ActionDef.type == action_pred_type)
    
    
    result_str = nodes + "/|" + edges
    
    return jsonify(result=result_str)
    
@app.route('/_add_location_map')
def add_location_map():
    readable_label  = request.args.get('map_readable_label', None, type=str)
    map_label       = utility.smallify(readable_label)
    domain_id       = request.args.get('domain_id', None, type=str)
    visibility      = request.args.get('visibility', None, type=str)
    status          = "DRAFT"
    notes           = request.args.get('notes', None, type=str)
    
    existing_map = db.session.query(LocationMap) \
        .filter(LocationMap.map_label == map_label) \
        .first()
    
    if not existing_map:
        new_map = LocationMap(
            map_label       = map_label              ,
            readable_label  = readable_label         ,
            domain          = domain_id              ,
            visibility      = visibility             ,
            status          = status                 ,
            notes           = notes                  ,
            created_by      = current_user.username ,
            last_edited_by  = current_user.username 
        )
        db.session.add(new_map)
        db.session.commit()
    
    result_str =""
    return jsonify(result=result_str)
    
@app.route('/_add_location_node')
def add_location_node():
    
    map_readable_label  = request.args.get('map_readable_label', None, type=str)
    map_label           = utility.smallify(map_readable_label)
    node_readable_label = request.args.get('node_readable_label', None, type=str)
    node_label          = utility.smallify(node_readable_label)
    node_type           = request.args.get('node_type', None, type=str)
    description         = request.args.get('description', None, type=str)
    
    existing_node = db.session.query(LocationNode) \
        .filter(LocationNode.map_label == map_label) \
        .filter(LocationNode.node_label == node_label) \
        .first()
        
    if not existing_node:
        new_node = LocationNode(
            map_label       = map_label             ,
            node_label      = node_label            ,
            readable_label  = node_readable_label   ,
            node_type       = node_type             ,
            description     = description
        )
        db.session.add(new_node)
        db.session.commit()
    else:
        existing_node.map_label      = map_label
        existing_node.node_label     = node_label
        existing_node.readable_label = node_readable_label
        existing_node.description    = description
        db.session.commit()
        
        
    result_str =""
    
    location_nodes = db.session.query(LocationNode) \
        .filter(LocationNode.map_label == map_label) \
        .all()
    
    for someloc in location_nodes:
        result_str +=   str(someloc.id)            + "/;" + \
                        str(someloc.map_label)     + "/;" + \
                        str(someloc.node_label)    + "/;" + \
                        str(someloc.readable_label)+ "/;" + \
                        str(someloc.description)   + "/;" + \
                        str(someloc.node_type)   + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
    
@app.route('/_add_location_edges')
def add_location_edges():
    map_label  = request.args.get('map_label', None, type=str)
    from_node  = request.args.get('from_node', None, type=str)
    to_node  = request.args.get('to_node', None, type=str)
    
    existing_edge = db.session.query(LocationEdges) \
        .filter(LocationEdges.map_label == map_label) \
        .filter(LocationEdges.from_node == from_node) \
        .filter(LocationEdges.to_node == to_node) \
        .first()
        
    result_str = ""
    if not existing_edge:
        new_edge = LocationEdges(
            map_label = map_label  ,
            from_node = from_node  ,
            to_node   = to_node
        )
        db.session.add(new_edge)
        db.session.commit()
        result_str = "new"
    else:
        result_str = "existing"
    
    return jsonify(result=result_str)
    
@app.route('/_delete_location_node')
def delete_location_node():
    node_label  = request.args.get('node_id', None, type=str)
    
    existing_node = db.session.query(LocationNode)                      \
        .filter(LocationNode.node_label == node_label)
    
    print(existing_node.first())
    print("====")
    existing_edges = db.session.query(LocationEdges)                    \
        .filter(                                                        \
            or_(                                                        \
                LocationEdges.from_node == existing_node.first().node_label,    \
                LocationEdges.to_node == existing_node.first().node_label       \
            )                                                           \
        ) \
        .delete()
    db.session.commit()
    
    existing_node.delete()
    db.session.commit()
    
    result_str=""
    return jsonify(result=result_str)
    
@app.route('/_delete_location_edge')
def delete_location_edge():
    edge_label  = request.args.get('edge_str', None, type=str)
    map_label   = request.args.get('map_label', None, type=str)
    split_str = edge_label.split("_to_")
    
    existing_edge = db.session.query(LocationEdges)         \
        .filter(LocationEdges.map_label == map_label)       \
        .filter(LocationEdges.from_node == split_str[0])    \
        .filter(LocationEdges.to_node == split_str[1])      
    
    existing_edge.delete()
    db.session.commit()
    
    result_str=""
    return jsonify(result=result_str)
    
@app.route('/_get_location_map')
def get_location_map():
    map_label = request.args.get('map_label', None, type=str)
    
    location_map = db.session.query(LocationMap) \
        .filter(LocationMap.map_label == map_label) \
        .all()
        
    result_str = ""
    for somemap in location_map:
        result_str +=   str(somemap.id)             + "/;" + \
                        str(somemap.map_label)      + "/;" + \
                        str(somemap.readable_label) + "/;" + \
                        str(somemap.domain)         + "/;" + \
                        str(somemap.attribute1)     + "/;" + \
                        str(somemap.attribute2)     + "/;" + \
                        str(somemap.attribute3)     + "/;" + \
                        str(somemap.visibility)     + "/;" + \
                        str(somemap.status)         + "/;" + \
                        str(somemap.notes)          + "/;" + \
                        str(somemap.created_by)     + "/;" + \
                        str(somemap.last_edited_by) + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
    
@app.route('/_get_location_nodes')
def get_location_nodes():
    map_label = request.args.get('map_label', None, type=str)
    
    location_nodes = db.session.query(LocationNode) \
        .filter(LocationNode.map_label == map_label) \
        .all()
    
    result_str = ""
    for somenode in location_nodes:
        result_str +=   str(somenode.id)            + "/;" + \
                        str(somenode.map_label)     + "/;" + \
                        str(somenode.node_label)    + "/;" + \
                        str(somenode.readable_label)+ "/;" + \
                        str(somenode.description)   + "/;" + \
                        str(somenode.node_type)     + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
    
@app.route('/_get_location_edges')
def get_location_edges():
    map_label = request.args.get('map_label', None, type=str)
    
    location_edges = db.session.query(LocationEdges) \
        .filter(LocationEdges.map_label == map_label) \
        .all()
    
    result_str = ""
    for someedge in location_edges:
        result_str +=   str(someedge.id)        + "/;" + \
                        str(someedge.map_label) + "/;" + \
                        str(someedge.from_node) + "/;" + \
                        str(someedge.to_node)   + "/;" + \
                        "/|"
    
    return jsonify(result=result_str)
    
@app.route('/_get_object_names')
def get_object_names():
    domain_full_label = request.args.get('domain_full_label', None, type=str)
    
    object_names = db.session.query(ObjectNames) \
        .filter(ObjectNames.domain == domain_full_label) \
        .all()
        
    result_str = ""
    for somename in object_names:
        result_str +=   str(somename.id)             + "/;" + \
                        str(somename.domain)         + "/;" + \
                        str(somename.main_label)     + "/;" + \
                        str(somename.readable_label) + "/;" + \
                        str(somename.object_type)    + "/;" + \
                        str(somename.attribute1)     + "/;" + \
                        str(somename.attribute2)     + "/;" + \
                        str(somename.attribute3)     + "/;" + \
                        "/|"
           
    return jsonify(result=result_str)
        
@app.route('/_add_object_name')
def add_object_name():
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    domain_id           = request.args.get('domain_full_label', None, type=str)
    readable_label      = request.args.get('readable_label', None, type=str)
    object_type         = request.args.get('object_type', None, type=str)
    attribute1          = request.args.get('attribute1', None, type=str)
    attribute2          = request.args.get('attribute2', None, type=str)
    attribute3          = request.args.get('attribute3', None, type=str)
    
    main_label = utility.smallify(readable_label)
    
    domain_full_label = db.session.query(Domains.domain_full_label) \
        .filter(Domains.id == domain_id) \
        .first() \
    
    existing_name = db.session.query(ObjectNames) \
        .filter(ObjectNames.main_label == main_label.lower()) \
        .filter(ObjectNames.domain == domain_full_label.domain_full_label) \
        .first()
        
    if not existing_name:
        new_name = ObjectNames(
            domain          = domain_full_label.domain_full_label ,
            main_label      = main_label        ,
            readable_label  = readable_label    ,
            object_type     = object_type       ,
            attribute1      = attribute1        ,
            attribute2      = attribute2        ,
            attribute3      = attribute3        ,
            created_by      = user_id           ,
            last_edited_by  = user_id
        )
        db.session.add(new_name)
        db.session.commit()
    
    result_str = ""
    return jsonify(result=result_str)
    

#===========================================

@app.route('/_get_plan_graph_nodes_lite')
def get_plan_graph_nodes_lite():
    
    # 1. Get run id
    # 2. Get the
    # 20200923_104448_ee2b079f_01
    
    filter_mode = request.args.get('filter_mode', "run_id", type=str)
    filter_value = request.args.get('filter_value', "", type=str)
    result_str = ""
    
    # filter by: plan_chapter_instance_id
    if filter_mode == "plan_chapter_instance_id":
        
        plan_graph_nodes = db.session.query(PlanGraphNode) \
            .filter(PlanGraphNode.node_label.like(filter_value+"%")) \
            .order_by(PlanGraphNode.layer.asc()) \
            .all()
        
        for somenode in plan_graph_nodes:
            result_str +=   str(somenode.run_id)                + "/;" + \
                            str(somenode.node_label)            + "/;" + \
                            str(somenode.layer)                 + "/;" + \
                            str(somenode.last_action)           + "/;" + \
                            str(somenode.achieved_author_goals) + "/;" + \
                            "/|"
    return jsonify(result=result_str)
    
@app.route('/_get_plan_graph_edges')
def get_plan_graph_edges():
    
    filter_mode = request.args.get('filter_mode', "run_id", type=str)
    filter_value = request.args.get('filter_value', "", type=str)
    result_str = ""
    
    # filter by: plan_chapter_instance_id
    
    if filter_mode == "plan_chapter_instance_id":
        plan_graph_edges = db.session.query(PlanGraphEdge) \
            .filter(PlanGraphEdge.from_node_label.like(filter_value+"%")) \
            .all()
            
        for someedge in plan_graph_edges:
            result_str +=   str(someedge.from_node_label)    + "/;" + \
                            str(someedge.to_node_label)      + "/;" + \
                            "/|"

    return jsonify(result=result_str)
    
@app.route('/_get_plan_graph_solution_nodes')
def get_plan_graph_solution_nodes():
    
    chapter_id = request.args.get('chapter_id', "", type=str)
    result_str = ""
    
    #print(chapter_id)
    #print("----")
    
    solution_chapters = db.session.query(SolutionChapterInstanceAction) \
        .filter(SolutionChapterInstanceAction.chapter_id == chapter_id) \
        .all()
    
    for somechapter in solution_chapters:
        
        result_str +=   str(somechapter.plan_graph_node_parent)    + "/;" + \
                        str(somechapter.plan_graph_node_label)      + "/;" + \
                        "/|"
        
    return jsonify(result=result_str)


@app.route("/exercise1_introduction")
def exercise1_introduction():  

    return render_template('exercise1_introduction.html', title='Writing Exercise: Introduction'
    )
    

@app.route("/exercise1_proper")
def exercise1_proper():  
    
    old_domains = db.session.query(Domains) \
        .filter(Domains.category_str.like("%anjicustom%"))
    
    custom_domains = db.session.query(Domains) \
        .filter(Domains.category_str.like("%sliceoflife%"))
        
    loadable_domains = old_domains.union(custom_domains).all()
    
    return render_template('exercise1_proper.html', title='Writing Exercise: Proper',
        loadable_domains = loadable_domains,
    )
    

@app.route("/exercise1_survey")
def exercise1_survey():  

    return render_template('exercise1_survey.html', title='Extra Credit: Additional Surveys'
    )
    
@app.route('/_get_narrative_instances_by_domain')
def get_narrative_instances_by_domain():

    filter_mode = request.args.get('filter_mode', "", type=str)
    filter_parameter_domain = request.args.get('filter_parameter_domain', "", type=str)
    filter_parameter_quantity = request.args.get('filter_parameter_quantity', 1, type=int)
    
    result_str = ""
    if filter_mode == "random":

        #narratives = db.session.query(NarrativeInstance, ChapterPattern, UserActivePlanners) \
        #    .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
        #    .filter(ChapterPattern.vacant1 is not None) \
        #    .filter(ChapterPattern.vacant1 != "") \
        #    .filter(ChapterPattern.domain.like(str(filter_parameter_domain) + "%"))    \
        #    .filter(NarrativeInstance.map_label is not None) \
        #    .filter(NarrativeInstance.map_label != "") \
        #    .filter(NarrativeInstance.narrative_id == UserActivePlanners.narrative_id) \
        #    .filter(UserActivePlanners.status == "SUCCESS") \
        #    .order_by(func.random())                                        \
        #    .limit(int(filter_parameter_quantity))     \
        #    .all()
        #    #.filter(ChapterPattern.series == 1) \
            
        narratives = db.session.query(NarrativeInstance, ChapterPattern, UserActivePlanners) \
            .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
            .filter(ChapterPattern.vacant1 is not None) \
            .filter(ChapterPattern.vacant1 != "") \
            .filter(ChapterPattern.domain.like(str(filter_parameter_domain) + "%"))    \
            .filter(NarrativeInstance.map_label is not None) \
            .filter(NarrativeInstance.map_label != "") \
            .filter(NarrativeInstance.narrative_id.like(UserActivePlanners.narrative_id + "%")) \
            .filter(UserActivePlanners.status == "SUCCESS") \
            .order_by(func.random())                                        \
            .limit(int(filter_parameter_quantity))     \
            .all()

            
    elif filter_mode == "ignore_no_map":
        narratives = db.session.query(NarrativeInstance, ChapterPattern, UserActivePlanners) \
            .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
            .filter(ChapterPattern.vacant1 is not None) \
            .filter(ChapterPattern.vacant1 != "") \
            .filter(ChapterPattern.domain.like(str(filter_parameter_domain) + "%"))    \
            .filter(ChapterPattern.name_label_str.notlike("%test%"))    \
            .filter(NarrativeInstance.narrative_id.like(UserActivePlanners.narrative_id + "%")) \
            .filter(UserActivePlanners.status == "SUCCESS") \
            .order_by(func.random())                                        \
            .limit(int(filter_parameter_quantity))     \
            .all()
            
    else:
        narratives = db.session.query(NarrativeInstance, ChapterPattern, UserActivePlanners) \
            .filter(func.lower(ChapterPattern.sequence_grouping_label) == func.lower(NarrativeInstance.story_pattern)) \
            .filter(ChapterPattern.vacant1 is not None) \
            .filter(ChapterPattern.vacant1 != "") \
            .filter(ChapterPattern.domain.like(str(filter_parameter_domain) + "%"))    \
            .filter(NarrativeInstance.narrative_id.like(UserActivePlanners.narrative_id) + "%") \
            .filter(UserActivePlanners.status == "SUCCESS") \
            .order_by(func.random())                                        \
            .all()

    for somenarrative in narratives:
        
        result_str +=   str(somenarrative.NarrativeInstance.narrative_id)    + "/;" + \
                        str(somenarrative.NarrativeInstance.narrative_label)      + "/;" + \
                        str(somenarrative.ChapterPattern.main_label)      + "/;" + \
                        str(somenarrative.ChapterPattern.sub_label)      + "/;" + \
                        str(somenarrative.ChapterPattern.vacant1)      + "/;" + \
                        "/|"
        
    return jsonify(result=result_str)
    
    
@app.route("/story_archive_domain_sampler")
def story_archive_domain_sampler():  
    
    
    if current_user.is_authenticated:
        user_id = current_user.username
    else:
        user_id = "anonymous"
    
    #old_domains = db.session.query(Domains) \
    #    .filter(Domains.category_str.like("%anjicustom%"))
    #
    #custom_domains = db.session.query(Domains) \
    #    .filter(Domains.category_str.like("%sliceoflife%"))
    #
    #loadable_domains = old_domains.union(custom_domains).all()    
    
    public_domains  = Domains.query \
        .filter(or_(Domains.visibility=="PUBLIC-WRITE", Domains.visibility=="PUBLIC-READONLY")) \
        .filter(Domains.status == "ACTIVE")
    
    own_domains     = Domains.query \
        .filter_by(created_by=user_id)  \
        .filter(Domains.status == "ACTIVE")
        
    loadable_domains = own_domains.union(public_domains).all()
        
    
    
    return render_template('story_archive_domain_sampler.html', title='Story Archive - Domain Sampler',
        loadable_domains = loadable_domains,
    )
    
    
@app.route("/teaching_tool_survey")
def teaching_tool_survey():

    return render_template('teaching_tool_survey.html', title='ISLA as a Teaching Tool Assessment'
    )
    
    
@app.route("/_submit_teaching_tool_survey")
def submit_teaching_tool_survey():


    first_name                  = request.args.get('first_name', None, type=str)
    last_name                   = request.args.get('last_name', None, type=str)
    email                       = request.args.get('email', None, type=str)
    affiliate_school            = request.args.get('affiliate_school', None, type=str)
    subject                     = request.args.get('subject', None, type=str)
    number_of_sections          = request.args.get('number_of_sections', None, type=str)
    total_number_of_students    = request.args.get('total_number_of_students', None, type=str)
    
    assessment_question_01      = request.args.get('assessment_question_01', None, type=str)
    assessment_question_02      = request.args.get('assessment_question_02', None, type=str)
    assessment_question_03      = request.args.get('assessment_question_03', None, type=str)
    #assessment_question_04 
    #assessment_question_05 
    #assessment_question_06 
    #assessment_question_07 
    #assessment_question_08 
    #assessment_question_09 
    #assessment_question_10 


    new_feedback = TeachingToolSurvey(

        first_name                  = first_name                ,
        last_name                   = last_name                 ,
        email                       = email                     ,
        affiliate_school            = affiliate_school          ,
        subject                     = subject                   ,
        number_of_sections          = number_of_sections        ,
        total_number_of_students    = total_number_of_students  ,
        assessment_question_01      = assessment_question_01    ,
        assessment_question_02      = assessment_question_02    ,
        assessment_question_03      = assessment_question_03  

    )
        
    db.session.add(new_feedback) 
    db.session.commit()
     
    success_flag = True
     
    if not success_flag:
        return jsonify(result='failed')
    else:
        return jsonify(result=success_flag)
        
#@app.route('/_evaluate_domain')
#def evaluate_domain():
#    
#    pass
#=======