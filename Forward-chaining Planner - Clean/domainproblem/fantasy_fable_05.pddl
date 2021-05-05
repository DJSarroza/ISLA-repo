(define (domain fantasy05)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(creature actor)
		(human creature)
		(elf creature)
		(fairy creature)
		(dragon creature)
		(orc creature)
		(item object)
		(weapon item)
		(mcguffin item)
		(valuable item)
		(creature_group predicate)
		(party creature_group)
		(nation creature_group)
		(clique creature_group)
	)

	(:actors
		actor
		admin
	)

	(:predicates
		(:predicate intends
			:parameters     ((?actor - actor) (?intention - predicate))
			:definition     (intends (?actor - actor) (?intention - predicate))
			:primary_obj    ((?actor - actor))
			:humanreadable  (
				("?actor intends that ?intention")
			)
		)

		(:predicate equals
			:parameters     ((?object1 - object) (?object2 - object))
			:definition     (equals (?object1 - object) (?object2 - object))
			:primary_obj    ()
			:humanreadable  (
			)
		)

		(:predicate forall
			:parameters     ((!object1 - object) (?whenstatement - predicate))
			:definition     (forall (!object1 - object) (?whenstatement - predicate))
			:primary_obj    ()
			:humanreadable  (
			)
		)

		(:predicate if
			:parameters     ((?somecondition - predicate) (?iftrue - predicate))
			:definition     (if (?somecondition - predicate) (?iftrue - predicate))
			:primary_obj    ()
			:humanreadable  (
			)
		)

		(:predicate ifelse
			:parameters     ((?somecondition - predicate) (?iftrue - predicate) (?else - predicate))
			:definition     (ifelse (?somecondition - predicate) (?iftrue - predicate) (?else - predicate))
			:primary_obj    ()
			:humanreadable  (
			)
		)

		(:predicate at
			:parameters     ((?someobj - object) (?somelocation - location))
			:definition     (at (?someobj - object) (?somelocation - location))
			:primary_obj    ((?someobj - object))
			:humanreadable  (
				("?someobject is at ?somelocation")
			)
		)

		(:predicate adjacent
			:parameters     ((?fromplace - location) (?toplace - location))
			:definition     (adjacent (?fromplace - location) (?toplace - location))
			:primary_obj    ()
			:humanreadable  (
				("from ?fromplace, one can reach ?toplace.")
			)
		)

		(:predicate is_alive
			:parameters     ((?creature - creature))
			:definition     (is_alive (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is alive.")
			)
		)

		(:predicate has_item
			:parameters     ((?creature - creature) (?item - item))
			:definition     (has_item (?creature - creature) (?item - item))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature has ?item.")
			)
		)

		(:predicate has_weapon
			:parameters     ((?creature - creature))
			:definition     (has_weapon (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature has a weapon.")
			)
		)

		(:predicate is_hungry
			:parameters     ((?creature - creature))
			:definition     (is_hungry (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is hungry.")
			)
		)

		(:predicate is_inlove
			:parameters     ((?creature - creature))
			:definition     (is_inlove (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is in love.")
			)
		)

		(:predicate is_detained_at
			:parameters     ((?creature - creature) (?prison - location))
			:definition     (is_detained_at (?creature - creature) (?prison - location))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is detained at ?prison.")
			)
		)

		(:predicate is_immobilized
			:parameters     ((?creature - creature))
			:definition     (is_immobilized (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is immobilized.")
			)
		)

		(:predicate is_married
			:parameters     ((?creature - creature))
			:definition     (is_married (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is married.")
			)
		)

		(:predicate is_healer
			:parameters     ((?creature - creature))
			:definition     (is_healer (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is a healer.")
			)
		)

		(:predicate loves
			:parameters     ((?lover - creature) (?lovee - creature))
			:definition     (loves (?lover - creature) (?lovee - creature))
			:primary_obj    ((?lover - creature))
			:humanreadable  (
				("?lover loves ?lovee.")
			)
		)

		(:predicate is_injured
			:parameters     ((?creature - creature))
			:definition     (is_injured (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is injured.")
			)
		)

		(:predicate belongs_to_group
			:parameters     ((?creature - creature) (?group - creature_group))
			:definition     (belongs_to_group (?creature - creature) (?group - creature_group))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature belongs to the group ?group.")
			)
		)

		(:predicate _rule_g2g__aggression_not_allowed
			:parameters     ((?group1 - creature_group) (?group2 - creature_group))
			:definition     (_rule_g2g__aggression_not_allowed (?group1 - creature_group) (?group2 - creature_group))
			:primary_obj    ((?group1 - creature_group))
			:humanreadable  (
				("aggression between ?group1 and ?group2 is not allowed.")
			)
		)

		(:predicate fairy_mind_control_human
			:parameters     ((?fairy - fairy) (?human - human))
			:definition     (fairy_mind_control_human (?fairy - fairy) (?human - human))
			:primary_obj    ((?fairy - fairy))
			:humanreadable  (
				("?fairy is in control of ?human's mind.")
			)
		)

		(:predicate is_coupled_with
			:parameters     ((?c1 - creature) (?c2 - creature))
			:definition     (is_coupled_with (?c1 - creature) (?c2 - creature))
			:primary_obj    ((?c1 - creature))
			:humanreadable  (
				("?c1 and ?c2 is a couple. they are romantically involved. yes it is mutual.")
				("?c1 and ?c2 loves each other is .. you know, a thing.")
			)
		)

		(:predicate is_married_to
			:parameters     ((?c1 - creature) (?c2 - creature))
			:definition     (is_married_to (?c1 - creature) (?c2 - creature))
			:primary_obj    ((?c1 - creature))
			:humanreadable  (
				("?c1 is married to ?c2.")
			)
		)

		(:predicate is_tired
			:parameters     ((?creature - creature))
			:definition     (is_tired (?creature - creature))
			:primary_obj    ((?creature - creature))
			:humanreadable  (
				("?creature is tired.")
			)
		)

		(:predicate party_exists
			:parameters     ((?party - party))
			:definition     (party_exists (?party - party))
			:primary_obj    ((?party - party))
			:humanreadable  (
				("?party exists.")
			)
		)

	)

		(:action lure_creature
			:parameters     ((?c1 - creature) (?c2 - creature) (?loc1 - location) (?loc2 - location))
			:precondition
								(and
									(is_alive ?c1)
									(is_alive ?c2)
									(at ?c1 ?loc1)
									(at ?c2 ?loc1)
									(not (at ?c1 ?loc2))
									(not (at ?c2 ?loc2))
									(not (equals ?loc1 ?loc2))
									(not (equals ?c1 ?c2))
								)

			:effect
								(and
									(not (at ?c1 ?loc1))
									(not (at ?c2 ?loc1))
									(at ?c1 ?loc2)
									(at ?c2 ?loc2)
									(forall
										(!carried_item - item)
											(when
												(and
													(has_item ?c1 !carried_item)
												)
											then
												(and
													(not (at !carried_item ?loc1))
													(at !carried_item ?loc2)
												)
											)
									)
									(forall
										(!carried_item - item)
											(when
												(and
													(has_item ?c2 !carried_item)
												)
											then
												(and
													(not (at !carried_item ?loc1))
													(at !carried_item ?loc2)
												)
											)
									)
								)

			:agents         ((?c1))
			:humanreadable  (
				("?c1 lures ?c2 from ?loc1 to ?loc2.")
			)
		)
		(:action basic_move
			:parameters     ((?creature - creature) (?loc1 - location) (?loc2 - location))
			:precondition
								(and
									(at ?creature ?loc1)
									(not (at ?creature ?loc2))
									(not (equals ?loc1 ?loc2))
								)

			:effect
								(and
									(not (at ?creature ?loc1))
									(at ?creature ?loc2)
								)

			:agents         ((?creature))
			:humanreadable  (
				("?creature moves from ?loc1 to ?loc2.")
			)
		)
		(:action recover_from_injury
			:parameters     ((?creature - creature))
			:precondition
								(and
									(is_injured ?creature)
								)

			:effect
								(and
									(not (is_injured ?creature))
								)

			:agents         ((?creature))
			:humanreadable  (
				("?creature recovers from its injuries.")
			)
		)
		(:action healer_heals_creature
			:parameters     ((?healer - creature) (?injured - creature) (?loc1 - location))
			:precondition
								(and
									(is_healer ?healer)
									(is_injured ?injured)
									(at ?healer ?loc1)
									(at ?injured ?loc1)
								)

			:effect
								(and
									(not (is_injured ?injured))
								)

			:agents         ((?healer))
			:humanreadable  (
				("?healer heals ?injured's injuries at ?loc1.")
			)
		)
		(:action human_kills_creature_withweapon
			:parameters     ((?human - human) (?victim - creature) (?weapon - weapon) (?loc1 - location))
			:precondition
								(and
									(at ?human ?loc1)
									(is_alive ?human)
									(has_item ?human ?weapon)
									(at ?victim ?loc1)
									(is_alive ?victim)
									(not (equals ?human ?victim))
								)

			:effect
								(and
									(not (is_alive ?victim))
								)

			:agents         ((?human))
			:humanreadable  (
				("?human kills ?victim at ?loc1 using ?weapon.")
			)
		)
		(:action fairy_mindcontrols_human
			:parameters     ((?fairy - fairy) (?human - human) (?loc1 - location))
			:precondition
								(and
									(at ?fairy ?loc1)
									(is_alive ?fairy)
									(at ?human ?loc1)
									(is_alive ?human)
									(not (fairy_mind_control_human ?fairy ?human))
								)

			:effect
								(and
									(fairy_mind_control_human ?fairy ?human)
								)

			:agents         ((?fairy))
			:humanreadable  (
				("?fairy mind controls ?human at ?loc1.")
			)
		)
		(:action creature_get_item_from_location
			:parameters     ((?finder - creature) (?item - item) (?loc1 - location))
			:precondition
								(and
									(is_alive ?finder)
									(at ?finder ?loc1)
									(at ?item ?loc1)
								)

			:effect
								(and
									(has_item ?finder ?item)
									(forall
										(!others - creature)
											(when
												(and
													(has_item !others ?item)
													(not (equals !others ?finder))
												)
											then
												(and
													(not (has_item ?finder ?item))
												)
											)
									)
								)

			:agents         ((?finder))
			:humanreadable  (
				("?finder obtains ?item at ?loc1.")
			)
		)
		(:action creature_lose_item_at_location
			:parameters     ((?loser - creature) (?item - item) (?loc1 - location))
			:precondition
								(and
									(has_item ?loser ?item)
									(at ?loser ?loc1)
								)

			:effect
								(and
									(not (has_item ?loser ?item))
									(at ?item ?loc1)
								)

			:humanreadable  (
				("?loser loses ?item at ?loc1.")
			)
		)
		(:action dragon_firebreaths_creature
			:parameters     ((?dragon - dragon) (?victim - creature) (?loc1 - location))
			:precondition
								(and
									(at ?dragon ?loc1)
									(is_alive ?dragon)
									(is_alive ?victim)
									(at ?victim ?loc1)
									(not (equals ?dragon ?victim))
								)

			:effect
								(and
									(when
										(and
											(is_injured ?victim)
										)
									then
										(and
											(not (is_injured ?victim))
											(not (is_alive ?victim))
										)
									)
									(when
										(and
											(not (is_injured ?victim))
										)
									then
										(and
											(is_injured ?victim)
										)
									)
								)

			:agents         ((?dragon))
			:humanreadable  (
				("?dragon breathes fire at ?victim at ?loc1.")
			)
		)
		(:action dragon_slashes_creature
			:parameters     ((?dragon - dragon) (?victim - creature) (?loc1 - location))
			:precondition
								(and
									(at ?dragon ?loc1)
									(at ?victim ?loc1)
									(is_alive ?dragon)
									(is_alive ?victim)
									(not (equals ?dragon ?victim))
								)

			:effect
								(and
									(not (is_alive ?victim))
								)

			:agents         ((?dragon))
			:humanreadable  (
				("?dragon slashes ?victim at ?loc1.")
			)
		)
		(:action creature_loots_creature
			:parameters     ((?looter - creature) (?dead_one - creature) (?loc1 - location))
			:precondition
								(and
									(at ?looter ?loc1)
									(at ?dead_one ?loc1)
									(is_alive ?looter)
									(not (is_alive ?dead_one))
								)

			:effect
								(and
									(forall
										(!loot - item)
											(when
												(and
													(has_item ?dead_one !loot)
													(at !loot ?loc1)
												)
											then
												(and
													(has_item ?looter !loot)
													(not (has_item ?dead_one !loot))
												)
											)
									)
								)

			:agents         ((?looter))
			:humanreadable  (
				("?looter loots ?dead_one's corpse at ?loc1.")
			)
		)
		(:action creature_injures_creature
			:parameters     ((?attacker - creature) (?victim - creature) (?loc1 - location))
			:precondition
								(and
									(at ?attacker ?loc1)
									(at ?victim ?loc1)
								)

			:effect
								(and
									(when
										(and
											(is_injured ?victim)
										)
									then
										(and
											(not (is_injured ?victim))
											(not (is_alive ?victim))
										)
									)
									(when
										(and
											(not (is_injured ?victim))
										)
									then
										(and
											(is_injured ?victim)
										)
									)
								)

			:agents         ((?attacker))
			:humanreadable  (
				("?attacker injures ?victim at ?loc1.")
			)
		)
		(:action creature_fallsinlove_noreason
			:parameters     ((?lover - creature) (?victim - creature) (?loc1 - location))
			:precondition
								(and
									(at ?lover ?loc1)
									(at ?victim ?loc1)
									(is_alive ?lover)
									(is_alive ?victim)
									(not (loves ?lover ?victim))
								)

			:effect
								(and
									(loves ?lover ?victim)
								)

			:humanreadable  (
				("?lover falls in love with ?victim, for no good reason, at ?loc1.")
			)
		)
		(:action marry
			:parameters     ((?c1 - creature) (?c2 - creature) (?loc1 - location))
			:precondition
								(and
									(at ?c1 ?loc1)
									(at ?c2 ?loc1)
									(is_alive ?c1)
									(is_alive ?c2)
									(not (is_married ?c1))
									(not (is_married ?c2))
								)

			:effect
								(and
									(is_married ?c1)
									(is_married ?c2)
									(is_married_to ?c1 ?c2)
									(is_married_to ?c2 ?c1)
								)

			:agents         ((?c1) (?c2))
			:humanreadable  (
				("?c1 and ?c2 got married at ?loc1.")
			)
		)
		(:action becomes_couple
			:parameters     ((?creature1 - creature) (?creature2 - creature) (?loc1 - location))
			:precondition
								(and
									(at ?creature1 ?loc1)
									(at ?creature2 ?loc1)
									(is_alive ?creature1)
									(is_alive ?creature2)
									(loves ?creature1 ?creature2)
									(loves ?creature2 ?creature1)
								)

			:effect
								(and
									(is_coupled_with ?creature1 ?creature2)
									(is_coupled_with ?creature2 ?creature1)
								)

			:agents         ((?creature1) (?creature2))
			:humanreadable  (
				("?creature1 and ?creature2 is now a couple. this happened at ?loc1.")
			)
		)
		(:action creature_steals_item_from_creature
			:parameters     ((?thief - creature) (?victim - creature) (?item - item) (?loc1 - location))
			:precondition
								(and
									(at ?thief ?loc1)
									(at ?victim ?loc1)
									(at ?item ?loc1)
									(is_alive ?thief)
									(has_item ?victim ?item)
									(not (has_item ?thief ?item))
								)

			:effect
								(and
									(has_item ?thief ?item)
									(not (has_item ?victim ?item))
								)

			:agents         ((?thief))
			:humanreadable  (
				("?thief steals ?item from ?victim at ?loc1.")
			)
		)
		(:action creature_gives_item_to_creature
			:parameters     ((?giver - creature) (?receiver - creature) (?item - item) (?loc1 - location))
			:precondition
								(and
									(at ?giver ?loc1)
									(at ?receiver ?loc1)
									(at ?item ?loc1)
									(has_item ?giver ?item)
									(not (has_item ?receiver ?item))
									(is_alive ?giver)
								)

			:effect
								(and
									(not (has_item ?giver ?item))
									(has_item ?receiver ?item)
								)

			:agents         ((?giver))
			:humanreadable  (
				("?giver gives ?item to ?receiver at ?loc1.")
			)
		)
		(:action elf_anti-orc_aoe_spell
			:parameters     ((?elf - elf) (?loc1 - location))
			:precondition
								(and
									(at ?elf ?loc1)
									(is_alive ?elf)
								)

			:effect
								(and
									(when
										(and
											(is_injured ?elf)
										)
									then
										(and
											(not (is_injured ?elf))
											(not (is_alive ?elf))
										)
									)
									(when
										(and
											(not (is_injured ?elf))
										)
									then
										(and
											(is_injured ?elf)
										)
									)
									(forall
										(!orc - orc)
											(when
												(and
													(at !orc ?loc1)
													(is_injured !orc)
												)
											then
												(and
													(not (is_injured !orc))
													(not (is_alive !orc))
												)
											)
									)
									(forall
										(!orc - orc)
											(when
												(and
													(at !orc ?loc1)
													(not (is_injured !orc))
												)
											then
												(and
													(is_injured !orc)
												)
											)
									)
								)

			:agents         ((?elf))
			:humanreadable  (
				("?elf performs an anti-orc offensive spell, affecting all orcs in ?loc1.")
			)
		)
		(:action elf_aoe_heal
			:parameters     ((?healer - elf) (?group - creature_group) (?loc1 - location))
			:precondition
								(and
									(at ?healer ?loc1)
									(is_alive ?healer)
									(belongs_to_group ?healer ?group)
									(not (is_tired ?healer))
								)

			:effect
								(and
									(forall
										(!groupmates - creature)
											(when
												(and
													(belongs_to_group !groupmates ?group)
													(at !groupmates ?loc1)
												)
											then
												(and
													(not (is_injured !groupmates))
												)
											)
									)
									(is_tired ?healer)
								)

			:agents         ((?healer))
			:humanreadable  (
				("?healer performs elven healing magic and heals all members of ?group in ?loc1.")
			)
		)
		(:action creature_rests
			:parameters     ((?creature - creature))
			:precondition
								(and
									(is_tired ?creature)
								)

			:effect
								(and
									(not (is_tired ?creature))
								)

			:agents         ((?creature))
			:humanreadable  (
				("?creature rests.")
			)
		)
		(:action creature_join_party
			:parameters     ((?outsider - creature) (?insider - creature) (?party - party) (?loc1 - location))
			:precondition
								(and
									(at ?outsider ?loc1)
									(at ?insider ?loc1)
									(belongs_to_group ?insider ?party)
									(not (belongs_to_group ?outsider ?party))
									(is_alive ?outsider)
									(is_alive ?outsider)
								)

			:effect
								(and
									(belongs_to_group ?outsider ?party)
								)

			:agents         ((?outsider) (?insider))
			:humanreadable  (
				("?insider admits ?outsider to the ?party party at ?loc1.")
				("?outsider requested to be part of ?party at ?loc1 and ?insider agreed.")
			)
		)
		(:action creature_leaves_party
			:parameters     ((?leaver - creature) (?party - party))
			:precondition
								(and
									(belongs_to_group ?leaver ?party)
								)

			:effect
								(and
									(not (belongs_to_group ?leaver ?party))
								)

			:agents         ((?leaver))
			:humanreadable  (
				("for some reason, ?leaver leaves the ?party party.")
			)
		)
		(:action creature_forms_party
			:parameters     ((?creature - creature) (?party - party) (?loc1 - location))
			:precondition
								(and
									(at ?creature ?loc1)
									(is_alive ?creature)
									(not (belongs_to_group ?creature ?party))
									(not (party_exists ?party))
								)

			:effect
								(and
									(belongs_to_group ?creature ?party)
									(party_exists ?party)
								)

			:agents         ((?creature))
			:humanreadable  (
				("?creature forms the ?party party at ?loc1.")
			)
		)
		(:action orc_kills_creature
			:parameters     ((?orc - orc) (?victim - creature) (?loc1 - location))
			:precondition
								(and
									(at ?orc ?loc1)
									(at ?victim ?loc1)
									(is_alive ?orc)
									(is_alive ?victim)
									(not (equals ?orc ?victim))
								)

			:effect
								(and
									(not (is_alive ?victim))
								)

			:agents         ((?orc))
			:humanreadable  (
				("?orc brutally murders ?victim at ?loc1.")
			)
		)
)
