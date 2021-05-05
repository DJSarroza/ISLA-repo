(define (domain fantasy11)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(item object)
		(creature actor)
		(monster creature)
		(person creature)
		(weapon item)
		(mcguffin item)
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
				("?someobj is at ?somelocation")
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

		(:predicate alive
			:parameters     ((?somecreature - creature))
			:definition     (alive (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is alive.")
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

		(:predicate hasweapon
			:parameters     ((?somecreature - creature))
			:definition     (hasweapon (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature has a weapon.")
			)
		)

		(:predicate isinjured
			:parameters     ((?somecreature - creature))
			:definition     (isinjured (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is injured.")
			)
		)

		(:predicate isheavilyinjured
			:parameters     ((?somecreature - creature))
			:definition     (isheavilyinjured (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is heavily injured.")
			)
		)

	)

		(:action creaturegetsitemfromplace
			:parameters     ((?somecreature - creature) (?someitem - item) (?somelocation - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?somelocation)
									(at ?someitem ?somelocation)
								)

			:effect
								(and
									(has ?somecreature ?someitem)
									(not (at ?someitem ?somelocation))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?somecreature !trigger_w)
												)
											then
												(and
													(hasweapon ?somecreature)
												)
											)
									)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature obtains ?someitem at the ?somelocation.")
			)
		)
		(:action creaturelosesitematplace
			:parameters     ((?somecreature - creature) (?someitem - item) (?somelocation - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?somelocation)
									(has ?somecreature ?someitem)
								)

			:effect
								(and
									(not (has ?somecreature ?someitem))
									(at ?someitem ?somelocation)
									(not (hasweapon ?somecreature))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?somecreature !trigger_w)
												)
											then
												(and
													(hasweapon ?somecreature)
												)
											)
									)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature loses ?someitem at the ?somelocation.")
			)
		)
		(:action creaturegiveitemtocreature
			:parameters     ((?giver - creature) (?receiver - creature) (?someitem - item) (?someplace - location))
			:precondition
								(and
									(at ?giver ?someplace)
									(at ?receiver ?someplace)
									(alive ?giver)
									(alive ?receiver)
									(has ?giver ?someitem)
									(not (equals ?giver ?receiver))
								)

			:effect
								(and
									(not (has ?giver ?someitem))
									(has ?receiver ?someitem)
									(not (hasweapon ?giver))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?giver !trigger_w)
												)
											then
												(and
													(hasweapon ?giver)
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
													(hasweapon ?receiver)
												)
											)
									)
								)

			:agents         ((?giver) (?receiver))
			:humanreadable  (
				("?giver gives ?someitem to ?receiver at the ?someplace.")
			)
		)
		(:action steal
			:parameters     ((?thief - creature) (?victim - creature) (?someitem - item) (?somelocation - location))
			:precondition
								(and
									(at ?thief ?somelocation)
									(at ?victim ?somelocation)
									(alive ?thief)
									(has ?victim ?someitem)
									(not (equals ?thief ?victim))
								)

			:effect
								(and
									(not (has ?victim ?someitem))
									(not (hasweapon ?victim))
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?victim !trigger_w)
												)
											then
												(and
													(hasweapon ?victim)
												)
											)
									)
									(has ?thief ?someitem)
									(forall
										(!trigger_w - weapon)
											(when
												(and
													(has ?thief !trigger_w)
												)
											then
												(and
													(hasweapon ?thief)
												)
											)
									)
								)

			:agents         ((?thief))
			:humanreadable  (
				("?thief steals ?someitem from ?victim at ?somelocation.")
			)
		)
		(:action creaturekillcreature_withweapon
			:parameters     ((?assailant - creature) (?victim - creature) (?somelocation - location))
			:precondition
								(and
									(at ?assailant ?somelocation)
									(at ?victim ?somelocation)
									(not (equals ?assailant ?victim))
									(alive ?assailant)
									(alive ?victim)
									(hasweapon ?assailant)
								)

			:effect
								(and
									(not (alive ?victim))
								)

			:agents         ((?assailant))
			:humanreadable  (
				("?assailant killed ?victim with a weapon at ?somelocation.")
			)
		)
		(:action creaturekillcreature_noweapon
			:parameters     ((?assailant - creature) (?victim - creature) (?somelocation - location))
			:precondition
								(and
									(at ?assailant ?somelocation)
									(not (equals ?assailant ?victim))
									(at ?victim ?somelocation)
									(alive ?assailant)
									(alive ?victim)
								)

			:effect
								(and
									(not (alive ?victim))
								)

			:agents         ((?assailant))
			:humanreadable  (
				("?assailant killed ?victim at ?somelocation.")
			)
		)
		(:action creatureinjurescreature_withweapon
			:parameters     ((?assailant - creature) (?victim - creature) (?somelocation - location))
			:precondition
								(and
									(at ?assailant ?somelocation)
									(not (equals ?assailant ?victim))
									(at ?victim ?somelocation)
									(alive ?assailant)
									(alive ?victim)
									(hasweapon ?assailant)
								)

			:effect
								(and
									(when
										(and
											(isheavilyinjured ?victim)
										)
									then
										(and
											(not (alive ?victim))
										)
									)
									(when
										(and
											(isinjured ?victim)
										)
									then
										(and
											(isheavilyinjured ?victim)
											(not (isinjured ?victim))
										)
									)
									(when
										(and
											(not (isinjured ?victim))
											(not (isheavilyinjured ?victim))
										)
									then
										(and
											(isinjured ?victim)
										)
									)
								)

			:agents         ((?assailant))
			:humanreadable  (
				("?assailant injured ?victim with a weapon at ?somelocation.")
			)
		)
		(:action creatureinjurescreature_noweapon
			:parameters     ((?assailant - creature) (?victim - creature) (?somelocation - location))
			:precondition
								(and
									(at ?assailant ?somelocation)
									(not (equals ?assailant ?victim))
									(at ?victim ?somelocation)
									(alive ?assailant)
									(alive ?victim)
								)

			:effect
								(and
									(when
										(and
											(isheavilyinjured ?victim)
										)
									then
										(and
											(not (alive ?victim))
										)
									)
									(when
										(and
											(isinjured ?victim)
										)
									then
										(and
											(isheavilyinjured ?victim)
											(not (isinjured ?victim))
										)
									)
									(when
										(and
											(not (isinjured ?victim))
											(not (isheavilyinjured ?victim))
										)
									then
										(and
											(isinjured ?victim)
										)
									)
								)

			:agents         ((?assailant))
			:humanreadable  (
				("?assailant injured ?victim with a weapon at ?somelocation.")
			)
		)
		(:action creaturebleedsout
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(alive ?somecreature)
									(isinjured ?somecreature)
								)

			:effect
								(and
									(not (isinjured ?somecreature))
									(not (alive ?somecreature))
								)

			:humanreadable  (
				("injured, ?somecreature bleeds to death.")
			)
		)
		(:action creaturebleedsout2
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(alive ?somecreature)
									(isheavilyinjured ?somecreature)
								)

			:effect
								(and
									(not (isinjured ?somecreature))
									(not (alive ?somecreature))
								)

			:humanreadable  (
				("heavily injured, ?somecreature bleeds to death.")
			)
		)
		(:action delegate_getquest
			:parameters     ((?fromcreature - creature) (?tocreature - creature) (?somemcguffin - mcguffin) (?someplace - location))
			:precondition
								(and
									(alive ?fromcreature)
									(not (equals ?fromcreature ?tocreature))
									(alive ?tocreature)
									(at ?fromcreature ?someplace)
									(at ?tocreature ?someplace)
								)

			:effect
								(and
									(intends ?tocreature (has ?tocreature ?somemcguffin) )
								)

			:agents         ((?fromcreature) (?tocreature))
			:humanreadable  (
				("?fromcreature told ?tocreature to obtain ?somemcguffin from ?someplace.")
			)
		)
		(:action move
			:parameters     ((?somecreature - creature) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?fromloc)
									(not (at ?somecreature ?toloc))
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?somecreature ?fromloc))
									(at ?somecreature ?toloc)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature moved from ?fromloc to ?toloc.")
			)
		)
)
