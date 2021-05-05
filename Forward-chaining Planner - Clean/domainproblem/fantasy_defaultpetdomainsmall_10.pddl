(define (domain fantasy10)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(creature actor)
		(person creature)
		(monster creature)
		(item object)
		(valuable item)
		(weapon item)
		(mcguffin item)
		(sanctum location)
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
				("?someobj is at ?somelocation.")
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

		(:predicate has
			:parameters     ((?somecreature - creature) (?someitem - item))
			:definition     (has (?somecreature - creature) (?someitem - item))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature has ?someitem.")
			)
		)

		(:predicate has_weapon
			:parameters     ((?somecreature - creature))
			:definition     (has_weapon (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature has  a weapon.")
			)
		)

		(:predicate is_injured
			:parameters     ((?somecreature - creature))
			:definition     (is_injured (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is injured.")
			)
		)

		(:predicate is_heavily_injured
			:parameters     ((?somecreature - creature))
			:definition     (is_heavily_injured (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is heavily injured.")
			)
		)

		(:predicate alive
			:parameters     ((?somecreature - creature))
			:definition     (alive (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is alive.")
			)
		)

		(:predicate zero_criticality_predicate
			:parameters     ((?someitem - item) (?somesanctum - sanctum))
			:definition     (zero_criticality_predicate (?someitem - item) (?somesanctum - sanctum))
			:primary_obj    ((?someitem - item))
			:humanreadable  (
				("?someitem in ?somesanctum for criticality purposes.")
			)
		)

		(:predicate zero_mutability_predicate
			:parameters     ((?somemonster - monster) (?someweapon - weapon))
			:definition     (zero_mutability_predicate (?somemonster - monster) (?someweapon - weapon))
			:primary_obj    ((?somemonster - monster))
			:humanreadable  (
				("?somemonster and ?someweapon for mutability purposes.")
			)
		)

	)

		(:action travel
			:parameters     ((?somecreature - creature) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?fromloc)
									(not (at ?somecreature ?toloc))
									(not (equals ?fromloc ?toloc))
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?somecreature ?fromloc))
									(at ?somecreature ?toloc)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature travels from ?fromloc to ?toloc.")
			)
		)
		(:action delegate_getquest
			:parameters     ((?fromcreature - creature) (?tocreature - creature) (?somemcguffin - mcguffin) (?someloc - location))
			:precondition
								(and
									(alive ?fromcreature)
									(alive ?tocreature)
									(at ?fromcreature ?someloc)
									(at ?tocreature ?someloc)
									(not (equals ?fromcreature ?tocreature))
								)

			:effect
								(and
									(intends ?tocreature (has ?tocreature ?somemcguffin) )
								)

			:agents         ((?fromcreature) (?tocreature))
			:humanreadable  (
				("Meeting at ?someloc, ?fromcreature instructs ?tocreature to find ?somemcguffin.")
			)
		)
		(:action get_item_from_location
			:parameters     ((?somecreature - creature) (?someitem - item) (?someloc - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?someloc)
									(at ?someitem ?someloc)
								)

			:effect
								(and
									(has ?somecreature ?someitem)
									(not (at ?someitem ?someloc))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?somecreature !trigger_w)
												)
											then
												(and
													(has_weapon ?somecreature)
												)
											)
									)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature gets ?someitem at ?someloc.")
			)
		)
		(:action lose_item_at_location
			:parameters     ((?somecreature - creature) (?someitem - item) (?someloc - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?someloc)
									(has ?somecreature ?someitem)
								)

			:effect
								(and
									(not (has ?somecreature ?someitem))
									(at ?someitem ?someloc)
									(not (has_weapon ?somecreature))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?somecreature !trigger_w)
												)
											then
												(and
													(has_weapon ?somecreature)
												)
											)
									)
								)

			:humanreadable  (
				("?somecreature loses ?someitem at ?someloc.")
			)
		)
		(:action give_item
			:parameters     ((?giver - creature) (?receiver - creature) (?someitem - item) (?someloc - location))
			:precondition
								(and
									(alive ?giver)
									(alive ?receiver)
									(at ?giver ?someloc)
									(at ?receiver ?someloc)
									(not (equals ?giver ?receiver))
									(has ?giver ?someitem)
								)

			:effect
								(and
									(not (has ?giver ?someitem))
									(has ?receiver ?someitem)
									(not (has_weapon ?giver))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?giver !trigger_w)
												)
											then
												(and
													(has_weapon ?giver)
												)
											)
									)
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?receiver !trigger_w)
												)
											then
												(and
													(has_weapon ?receiver)
												)
											)
									)
								)

			:agents         ((?giver) (?receiver))
			:humanreadable  (
				("?giver gives ?someitem to ?receiver at ?someloc.")
			)
		)
		(:action steal_item
			:parameters     ((?thief - creature) (?victim - creature) (?someitem - item) (?someloc - location))
			:precondition
								(and
									(alive ?thief)
									(at ?thief ?someloc)
									(at ?victim ?someloc)
									(has ?victim ?someitem)
									(not (equals ?thief ?victim))
								)

			:effect
								(and
									(has ?thief ?someitem)
									(not (has ?victim ?someitem))
									(not (has_weapon ?victim))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?thief !trigger_w)
												)
											then
												(and
													(has_weapon ?thief)
												)
											)
									)
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?victim !trigger_w)
												)
											then
												(and
													(has_weapon ?victim)
												)
											)
									)
								)

			:agents         ((?thief))
			:humanreadable  (
				("?thief steals ?someitem from ?victim at ?someloc.")
			)
		)
		(:action kill_withweapon
			:parameters     ((?killer - creature) (?victim - creature) (?someloc - location))
			:precondition
								(and
									(alive ?killer)
									(alive ?victim)
									(at ?killer ?someloc)
									(at ?victim ?someloc)
									(has_weapon ?killer)
									(not (equals ?killer ?victim))
								)

			:effect
								(and
									(not (alive ?victim))
								)

			:agents         ((?killer))
			:humanreadable  (
				("Using a weapon, ?killer killed ?victim at ?someloc.")
			)
		)
		(:action kill_noweapon
			:parameters     ((?killer - creature) (?victim - creature) (?someloc - location))
			:precondition
								(and
									(alive ?killer)
									(not (equals ?killer ?victim))
									(alive ?victim)
									(at ?killer ?someloc)
									(at ?victim ?someloc)
								)

			:effect
								(and
									(not (alive ?victim))
								)

			:agents         ((?killer))
			:humanreadable  (
				("Without any weapons, ?killer killed ?victim at ?someloc.")
			)
		)
		(:action injure_withweapon
			:parameters     ((?killer - creature) (?victim - creature) (?someloc - location))
			:precondition
								(and
									(alive ?killer)
									(not (equals ?killer ?victim))
									(alive ?victim)
									(at ?killer ?someloc)
									(at ?victim ?someloc)
									(has_weapon ?killer)
								)

			:effect
								(and
									(when
										(and
											(is_heavily_injured ?victim)
											(alive ?victim)
										)
									then
										(and
											(not (alive ?victim))
										)
									)
									(when
										(and
											(is_injured ?victim)
											(alive ?victim)
										)
									then
										(and
											(is_heavily_injured ?victim)
										)
									)
									(when
										(and
											(not (is_injured ?victim))
											(alive ?victim)
											(not (is_heavily_injured ?victim))
										)
									then
										(and
											(is_injured ?victim)
										)
									)
								)

			:agents         ((?killer))
			:humanreadable  (
				("Using a weapon, ?killer injured ?victim at ?someloc.")
			)
		)
		(:action injure_noweapon
			:parameters     ((?killer - creature) (?victim - creature) (?someloc - location))
			:precondition
								(and
									(alive ?killer)
									(not (equals ?killer ?victim))
									(alive ?victim)
									(at ?killer ?someloc)
									(at ?victim ?someloc)
								)

			:effect
								(and
									(when
										(and
											(is_heavily_injured ?victim)
											(alive ?victim)
										)
									then
										(and
											(not (alive ?victim))
										)
									)
									(when
										(and
											(is_injured ?victim)
											(alive ?victim)
										)
									then
										(and
											(is_heavily_injured ?victim)
										)
									)
									(when
										(and
											(not (is_injured ?victim))
											(alive ?victim)
											(not (is_heavily_injured ?victim))
										)
									then
										(and
											(is_injured ?victim)
										)
									)
								)

			:agents         ((?killer))
			:humanreadable  (
				("Without any weapons, ?killer injured ?victim at ?someloc.")
			)
		)
		(:action bleeds_out
			:parameters     ((?injured - creature))
			:precondition
								(and
									(alive ?injured)
									(is_injured ?injured)
								)

			:effect
								(and
									(not (alive ?injured))
								)

			:humanreadable  (
				("?injured bleeds to death.")
			)
		)
		(:action bleeds_out2
			:parameters     ((?injured - creature))
			:precondition
								(and
									(alive ?injured)
									(is_heavily_injured ?injured)
								)

			:effect
								(and
									(not (alive ?injured))
								)

			:humanreadable  (
				("?injured bleeds to death.")
			)
		)
		(:action dummy_action1
			:parameters     ((?someitem - item) (?somesanctum - sanctum))
			:precondition
								(and
									(at ?someitem ?somesanctum)
								)

			:effect
								(and
									(zero_criticality_predicate ?someitem ?somesanctum)
								)

			:humanreadable  (
				("Add zero_criticality_predicate for ?someitem and ?somesanctum for testing purposes.")
			)
		)
		(:action dummy_action2
			:parameters     ((?someitem - item) (?somesanctum - sanctum))
			:precondition
								(and
									(not (at ?someitem ?somesanctum))
								)

			:effect
								(and
									(not (zero_criticality_predicate ?someitem ?somesanctum))
								)

			:humanreadable  (
				("Remove zero_criticality_predicate for ?someitem and ?somesanctum for testing purposes.")
			)
		)
		(:action modify_zca_pos
			:parameters     ((?someitem - item) (?somesanctum - sanctum))
			:precondition
								(and
									(at ?someitem ?somesanctum)
								)

			:effect
								(and
									(zero_criticality_predicate ?someitem ?somesanctum)
								)

			:humanreadable  (
				("Add zero_criticality_predicate for ?someitem at ?somesanctum.")
			)
		)
		(:action modify_zca_neg
			:parameters     ((?someitem - item) (?somesanctum - sanctum))
			:precondition
								(and
									(at ?someitem ?somesanctum)
								)

			:effect
								(and
									(not (zero_criticality_predicate ?someitem ?somesanctum))
								)

			:humanreadable  (
				("Remove zero_criticality_predicate for ?someitem at ?somesanctum.")
			)
		)
		(:action dummy_action3
			:parameters     ((?somemonster - monster) (?someweapon - weapon))
			:precondition
								(and
									(zero_mutability_predicate ?somemonster ?someweapon)
								)

			:effect
								(and
									(has ?somemonster ?someweapon)
								)

			:humanreadable  (
				("?somemonster now has ?someweapon for test purposes.")
			)
		)
		(:action dummy_action4
			:parameters     ((?somemonster - monster) (?someweapon - weapon))
			:precondition
								(and
									(not (zero_mutability_predicate ?somemonster ?someweapon))
								)

			:effect
								(and
									(not (has ?somemonster ?someweapon))
								)

			:humanreadable  (
				("?somemonster now does not have ?someweapon for test purposes.")
			)
		)
		(:action travel_to_sanctum
			:parameters     ((?somecreature - creature) (?fromloc - location) (?tosanctum - sanctum))
			:precondition
								(and
									(at ?somecreature ?fromloc)
									(not (at ?somecreature ?tosanctum))
									(alive ?somecreature)
								)

			:effect
								(and
									(not (at ?somecreature ?fromloc))
									(at ?somecreature ?tosanctum)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature moves from ?fromloc to ?tosanctum.")
			)
		)
		(:action travel_from_sanctum
			:parameters     ((?somecreature - creature) (?fromsanctum - sanctum) (?toloc - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?fromsanctum)
									(not (at ?somecreature ?toloc))
								)

			:effect
								(and
									(not (at ?somecreature ?fromsanctum))
									(at ?somecreature ?toloc)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature moves from ?fromsanctum to ?toloc.")
			)
		)
)
