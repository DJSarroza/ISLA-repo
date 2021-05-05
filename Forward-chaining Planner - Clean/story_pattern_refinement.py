import sys
import random
import customgalib
import secrets
import datetime
import copy
from chapterchainer import ChapterChainer
from flask_app import db
import utility as util


#------------------------------------------------
#    GLOBAL DECLARATIONS 
_INPUT_DIR = "./domainproblem/"
_MAX_POPULATION = 6
_STOP_THRESHOLD = 0.8
_MUTATION_CHANCE = 0.05
_LOG_EXECUTION_LOGFILE = ["","","",""]
_LOG_DIR = "./logs/"

#================================================

class PatternRefinery:
    def __init__(self, 
                gene_dict=None, 
                master_pattern=None, 
                max_population=0, 
                gene_var_range=None,
                stop_threshold=0.9,
                mutation_chance=0.05,
                enable_planner=True
                ):
        self.gene_dict       = copy.deepcopy(gene_dict)
        self.master_pattern  = master_pattern
        self.max_population  = max_population 
        self.gene_var_range  = gene_var_range
        self.stop_threshold  = stop_threshold
        self.mutation_chance = mutation_chance        
        self.enable_planner  = enable_planner
        
        temp = copy.copy(master_pattern)
        temp = temp.replace("%-","")
        temp = temp.replace("-%","")
        temp = temp.split("-")
        
        self.immune_genes = copy.copy(temp)
        self.pivot = copy.copy(temp[round((len(temp)-1)/2)])
        
        
    def setMasterPattern(self, master_pattern:str):
        
        self.master_pattern = copy.copy(master_pattern)

    def generateInitialPopulation(self):
        
        output_population = []
        split_pattern = self.master_pattern.split("-")
        
        gene_values = list(self.gene_dict.keys())
        
        for pop_cnt in range(0,self.max_population):
            
            individual = ""
            
            for some_gene in split_pattern:
                if some_gene == "%":
                    
                    range_value = random.choice(self.gene_var_range)
                    for range_ctr in range(0,range_value):
                        input_gene = random.choice(gene_values)
                        individual += "-" + input_gene
                
                else:
                    individual += "-" + some_gene
                    
            
            output_population.append((individual.strip("-"),0))
            
        return output_population

    #================================================

    def generateOffspring(self, parent_A_str, parent_B_str, pivot_str):

        split_parent_A = parent_A_str.split("-")
        split_parent_B = parent_B_str.split("-")
        
        pivot_index_A = split_parent_A.index(pivot_str)
        pivot_index_B = split_parent_B.index(pivot_str)
        
        substr_Aa = ""
        for index in range(0,pivot_index_A):
            substr_Aa += "-" + split_parent_A[index]
        
        substr_Ab = ""
        for index in range(pivot_index_A, len(split_parent_A)):
            substr_Ab += "-" + split_parent_A[index]
            
        substr_Ba = ""
        for index in range(0,pivot_index_B):
            substr_Ba += "-" + split_parent_B[index]
        
        substr_Bb = ""
        for index in range(pivot_index_B, len(split_parent_B)):
            substr_Bb += "-" + split_parent_B[index]
            
        if random.choice([True,False]):
            offspring = substr_Aa + substr_Bb
        else:
            offspring = substr_Ba + substr_Ab
        
        return offspring.strip("-")

    def generateNewPopulation(self, scored_population, fit_population_percentage, stopping_threshold=_STOP_THRESHOLD):
        
        scored_population.sort(key=lambda tup: tup[1], reverse=True)
        output_population = []
        
        
        average_score = 0
        max_score = 0
        total_score = 0
        
        ctr = 0
        
        max_score = scored_population[0][1]
        
        for some_individual in scored_population:
            ctr += 1
            print(ctr)
            print((len(scored_population) * fit_population_percentage))
            if ctr <= (len(scored_population) * fit_population_percentage):
                total_score += some_individual[1]
                average_score = total_score / ctr
                #print("Adding [1]")
                output_population.append(copy.copy(some_individual))
            else:
                break
                
        if max_score >= stopping_threshold:
        #if average_score >= stopping_threshold:
            print("Best one: " + str(scored_population[0]))
            
            self.saveToPatternFile(scored_population[0][0], _INPUT_DIR + "ncs_patterns_refined_overcome_monster_fantasy-01.csv",write_mode="a+")
            
            return "PASSED"
        else:
            print("[Refinery] CURRENT MAX_SCORE: " + str(scored_population[0]))
            parent_A_list = copy.copy(output_population)
            parent_B_list = copy.copy(output_population)
            
            pActr = 0
            for parent_A in parent_A_list:
                pActr += 1
                pBctr = 0
                for parent_B in parent_B_list:
                    pBctr += 1
                    
                    if pActr < pBctr:
                        offspring = self.generateOffspring(parent_A[0], parent_B[0], self.pivot)
                        mutate = random.random()
                        if mutate <= _MUTATION_CHANCE:
                            
                            mutant_before = random.choice(offspring.split("-"))
                            mutant_after = random.choice(list(self.gene_dict.keys()))
                            
                            if not (mutant_before in self.immune_genes):
                                offspring = offspring.replace(mutant_before,mutant_after,1)
                                #print("Mutation! " + mutant_before + " -> " + mutant_after)
                        
                        #print("Adding [2] " + str(pActr) + "/" +  str(pBctr))
                        output_population.append((copy.copy(offspring),0))
                        
            return copy.deepcopy(output_population)
            
            
    def saveToPatternFile(self, individual_str, pattern_filename, write_mode="w"):
    
        pattern_file = open(pattern_filename,write_mode)
        split_pattern = individual_str.split("-")
        
        ctr = 0
        for some_gene in split_pattern:
            ctr +=1 
            
            # Villain
            #pattern_line = ",Booker7Plots,Overcome the Villain,overcomevillain,Refinery 01,refinery,Booker7Plots_overcomevillain_refinery,,,01,Booker7Plots_overcomevillain_refinery_01,"+str(ctr)+",Booker7Plots_overcomevillain_refinery_01_1_"+self.gene_dict[some_gene]+","+self.gene_dict[some_gene]+",0,,,1,1,TRUE,,,,,,,,,,,\n"
            
            # Monster
            #pattern_line = ",Booker7Plots,Overcome the Monster,overcomemonster,Refinery 01,refinery,Booker7Plots_overcomemonster_refinery,,,01,Booker7Plots_overcomemonster_refinery_01,"+str(ctr)+",Booker7Plots_overcomemonster_refinery_01_1_"+self.gene_dict[some_gene]+","+self.gene_dict[some_gene]+",0,,,1,1,TRUE,,,,,,,,,,,\n"
            
            # The Quest
            pattern_line = ",Booker7Plots,The Quest,thequest,Refinery 01,refinery,Booker7Plots_thequest_refinery,,,01,Booker7Plots_thequest_refinery_01,"+str(ctr)+",Booker7Plots_thequest_refinery_01_1_"+self.gene_dict[some_gene]+","+self.gene_dict[some_gene]+",0,,,1,1,TRUE,,,,,,,,,,,\n"
            
            
            pattern_file.write(pattern_line)
        
        pattern_file.close()
        

    def execute(self):

        # 0. Data Dictionaries
        now = datetime.datetime.now()
        now_str = now.strftime("%Y%m%d_%H%M%S")
        _LOG_EXECUTION_LOGFILE[0] = _LOG_DIR + "Refinery/LOG_refinery_consolidated_" + now_str + ".txt"
        
        current_population = self.generateInitialPopulation()
        
        # 3. Population scoring
        generation = 0
        while True:
            generation += 1
            scored_population = []
            for individual in current_population:
                
                #   Save to pattern file
                self.saveToPatternFile(individual[0], _INPUT_DIR + "ncs_patterns_refinery_fantasy-01.csv","w")
                
                score = 0
                for ctr in range(0,6):
                    now = datetime.datetime.now()
                    now_str = now.strftime("%Y%m%d_%H%M%S")
                    run_id = secrets.token_hex(8) + "_refinery_" + now_str
                    chainer = ChapterChainer(
                        id=run_id, 
                        user_id="refinery",
                        category="fantasy", 
                        series="01",
                        db=db
                    )
                    
                    # Villain
                    #story_pattern = "overcomevillain"
                    
                    # Monster
                    #story_pattern = "overcomemonster"
                    
                    # The Quesst
                    story_pattern = "thequest"
                    
                    if self.enable_planner:
                        success_flag = chainer.execute(
                            neutral_obj_count=0,
                            story_pattern=story_pattern,
                            custom_story_pattern=story_pattern,
                            random_story_pattern=False,
                            check_session=2,
                            runtime_threshold=8,
                            algorithm="ggp_dr1_hybrid"
                        )
                    else:
                        success_flag = random.choice([True,False,True])
                    if success_flag:
                        score += 1
                        
                score = score / 6
                scored_population.append((individual[0],score))
            #print("======================")
            #for something in scored_population:
            #    print(something)
            #input()
            
            # 4.
            
            new_population = self.generateNewPopulation(scored_population, 0.5)
            scored_population.sort(key=lambda tup: tup[1], reverse=True)
            logstr = "Generation " + str(generation) + ": Best individual: " + str(scored_population[0])
            util.log(_LOG_EXECUTION_LOGFILE[0], logstr, "line/txt", enabled=True)

            if new_population == "PASSED":
                print("Success")
                break
            else:
                current_population = new_population
                
        
        return True


#================================================


#================================================



#================================================

def main(self):
    
    
    

    
    gene_dict = {   
                    "_CG1"    : "ConfrontGuardian1",
                    "_DEP1"   : "Departure1",
                    "_DEP2"   : "Departure2",
                    "_DEP3"   : "Departure3",
                    "_DTA1"   : "DifficultTaskArises1",
                    "_HLP1"   : "Helper1",
                    "_HLPX1"  : "HelperLost1",
                    "_HL1"    : "HeroLost1",
                    "_HR1"    : "HeroReward1",
                    "_LACK1"  : "Lack1",
                    "_MON1"   : "Monsters1",
                    "_MON2"   : "Monsters2",
                    "_QSTA1"  : "QuestAssigned1",
                    "_QSTR1"  : "QuestResolution1",
                    "_RECO1"  : "Recovery1",
                    "_RET1"   : "ReturnJourney1",
                    "_STRM1"  : "StruggleMonster1",
                    "_STRV1"  : "StruggleVillain1",
                    "_SVHLP1" : "StruggleVillainHelper1",
                    "_TRAN1"  : "Transfiguration1",
                    "_VAM1"   : "VictoryAgainstMonster1",
                    "_VAV1"   : "VictoryAgainstVillainy1",
                    "_VAV2"   : "VictoryAgainstVillainy2",
                 #   "_VREP1"  : "VillainRepentance1",
                    "_VREW1"  : "VillainReward1",
                    "_VIL1"   : "Villainy1",
                    "_VIL2"   : "Villainy2"
                }
    
    
    # 1. Set immutable master pattern
    # Villain
    #master_pattern = "%-_VIL1-%-%-_VAV1-%-%-_HR1"
    # Monster
    #master_pattern = "%-_MON1-%-%-_VAM1-%-%-_HR1"
    # The Quest
    master_pattern = "_DTA1-%-_QSTA1-%-%-%-_QSTR1"
    
    gene_var_range = range(0,2)
    
    pattern_dict = {
                        "overcomevillain" : "%-_VIL1-%-%-_VAV1-%-%-_HR1",
                        "overcomemonster" : "%-_MON1-%-%-_VAM1-%-%-_HR1",
                        "thequest"        : "_DTA1-%-_QSTA1-%-%-%-_QSTR1"
                   }
        
    refinery = PatternRefinery(
                gene_dict        = gene_dict, 
                master_pattern   = master_pattern, 
                max_population   = _MAX_POPULATION, 
                gene_var_range   = gene_var_range,
                stop_threshold   = _STOP_THRESHOLD,
                mutation_chance  = _MUTATION_CHANCE,
                enable_planner   = True                 # [CRITICAL!!! ALWAYS CHECK THIS ]
    )
    
    
    refinery.execute()


if __name__ == '__main__':
    main(sys.argv)