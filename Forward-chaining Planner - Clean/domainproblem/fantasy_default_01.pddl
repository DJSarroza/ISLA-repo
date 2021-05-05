(define (domain fantasy01)
	(:types 
		object
		predicate
		(item object)
		(actor object)
		(admin actor)
		(creature actor)
		(person creature)
		(monster creature)
		(valuable item)
		(weapon item)
		(mcguffin item)
		location
	)

	(:actors
		admin
		creature
		person
		monster
	)

	(:predicates
		(:predicate adjacent
			:parameters     ((?fromplace - location) (?toplace - location))
			:definition     (adjacent (?fromplace - location) (?toplace - location))
			:primary_obj    ((?fromplace - location))
			:humanreadable  (
				("?fromplace is adjacent to ?toplace.")
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

		(:predicate single
			:parameters     ((?somecreature - creature))
			:definition     (single (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is single.")
			)
		)

		(:predicate rich
			:parameters     ((?somecreature - creature))
			:definition     (rich (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is rich.")
			)
		)

		(:predicate happy
			:parameters     ((?somecreature - creature))
			:definition     (happy (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is happy.")
			)
		)

		(:predicate hungry
			:parameters     ((?somecreature - creature))
			:definition     (hungry (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is hungry.")
			)
		)

		(:predicate inlove
			:parameters     ((?somecreature - creature))
			:definition     (inlove (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is inlove.")
			)
		)

		(:predicate at
			:parameters     ((?someobject - object) (?someplace - location))
			:definition     (at (?someobject - object) (?someplace - location))
			:primary_obj    ((?someobject - object))
			:humanreadable  (
				("?someobject is at the ?someplace.")
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

		(:predicate itembelongsto
			:parameters     ((?someitem - item) (?somecreature - creature))
			:definition     (itembelongsto (?someitem - item) (?somecreature - creature))
			:primary_obj    ((?someitem - item))
			:humanreadable  (
				("?someitem belongs to ?somecreature.")
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

		(:predicate hasproposedto
			:parameters     ((?proposer - creature) (?proposee - creature))
			:definition     (hasproposedto (?proposer - creature) (?proposee - creature))
			:primary_obj    ((?proposer - creature))
			:humanreadable  (
				("?proposer has proposed to ?proposee.")
			)
		)

		(:predicate hasaccepted
			:parameters     ((?creature1 - creature) (?creature2 - creature))
			:definition     (hasaccepted (?creature1 - creature) (?creature2 - creature))
			:primary_obj    ((?creature1 - creature))
			:humanreadable  (
				("?creature1 has accepted marriage proposal from ?creature2.")
			)
		)

		(:predicate ismarried
			:parameters     ((?somecreature - creature))
			:definition     (ismarried (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is married.")
			)
		)

		(:predicate marriedto
			:parameters     ((?creature1 - creature) (?creature2 - creature))
			:definition     (marriedto (?creature1 - creature) (?creature2 - creature))
			:primary_obj    ((?creature1 - creature))
			:humanreadable  (
				("?creature1 is married to ?creature2.")
			)
		)

		(:predicate hasproposed
			:parameters     ((?proposer - creature))
			:definition     (hasproposed (?proposer - creature))
			:primary_obj    ((?proposer - creature))
			:humanreadable  (
				("?proposer has proposed marriage to someone.")
			)
		)

		(:predicate hasbeenproposedto
			:parameters     ((?proposee - creature))
			:definition     (hasbeenproposedto (?proposee - creature))
			:primary_obj    ((?proposee - creature))
			:humanreadable  (
				("?proposee has been proposed at by someone.")
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

		(:predicate isthief
			:parameters     ((?thief - creature))
			:definition     (isthief (?thief - creature))
			:primary_obj    ((?thief - creature))
			:humanreadable  (
				("?thief is a thief.")
			)
		)

		(:predicate hasrawmeat
			:parameters     ((?somecreature - creature))
			:definition     (hasrawmeat (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature has raw meat.")
			)
		)

		(:predicate issick
			:parameters     ((?somecreature - creature))
			:definition     (issick (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is sick.")
			)
		)

		(:predicate homeofcreature
			:parameters     ((?somecreature - creature) (?home - location))
			:definition     (homeofcreature (?somecreature - creature) (?home - location))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?home is the home of ?somecreature.")
			)
		)

		(:predicate familiarplace
			:parameters     ((?somecreature - creature) (?someplace - location))
			:definition     (familiarplace (?somecreature - creature) (?someplace - location))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("the ?someplace is a familiar place to ?somecreature.")
			)
		)

		(:predicate isdetained
			:parameters     ((?somecreature - creature))
			:definition     (isdetained (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is detained.")
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

		(:predicate ishealer
			:parameters     ((?somecreature - creature))
			:definition     (ishealer (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is a healer.")
			)
		)

		(:predicate emo_goodmood
			:parameters     ((?somecreature - creature))
			:definition     (emo_goodmood (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is in a good mood.")
			)
		)

		(:predicate emo_badmood
			:parameters     ((?somecreature - creature))
			:definition     (emo_badmood (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is in a bad mood.")
			)
		)

		(:predicate emo_feelstrong
			:parameters     ((?somecreature - creature))
			:definition     (emo_feelstrong (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling strong.")
			)
		)

		(:predicate emo_feelweak
			:parameters     ((?somecreature - creature))
			:definition     (emo_feelweak (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling weak.")
			)
		)

		(:predicate emo_confused
			:parameters     ((?somecreature - creature))
			:definition     (emo_confused (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling confused.")
			)
		)

		(:predicate emo_focused
			:parameters     ((?somecreature - creature))
			:definition     (emo_focused (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling focused.")
			)
		)

		(:predicate emo_joy
			:parameters     ((?somecreature - creature))
			:definition     (emo_joy (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling joy.")
			)
		)

		(:predicate emo_sorrow
			:parameters     ((?somecreature - creature))
			:definition     (emo_sorrow (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature is feeling sorrow.")
			)
		)

		(:predicate lackrealized_single
			:parameters     ((?realizer - creature) (?somecreature - creature))
			:definition     (lackrealized_single (?realizer - creature) (?somecreature - creature))
			:primary_obj    ((?realizer - creature))
			:humanreadable  (
				("?realizer realized that ?somecreature is single.")
			)
		)

		(:predicate lackrealized_nothas
			:parameters     ((?realizer - creature) (?somecreature - creature) (?item - item))
			:definition     (lackrealized_nothas (?realizer - creature) (?somecreature - creature) (?item - item))
			:primary_obj    ((?realizer - creature))
			:humanreadable  (
				("?realizer realized that ?somecreature does not have ?item.")
			)
		)

		(:predicate lackrealized_notrich
			:parameters     ((?realizer - creature) (?somecreature - creature))
			:definition     (lackrealized_notrich (?realizer - creature) (?somecreature - creature))
			:primary_obj    ((?realizer - creature))
			:humanreadable  (
				("?realizer realized that ?somecreature is not rich.")
			)
		)

		(:predicate ending_beginjourneyhome
			:parameters     ((?somecreature - creature))
			:definition     (ending_beginjourneyhome (?somecreature - creature))
			:primary_obj    ((?somecreature - creature))
			:humanreadable  (
				("?somecreature begins the journey home.")
			)
		)

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

	)

		(:action travel
			:parameters     ((?somecreature - creature) (?from - location) (?to - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?from)
									(adjacent ?from ?to)
									(not (equals ?from ?to))
								)

			:effect
								(and
									(at ?somecreature ?to)
									(not (at ?somecreature ?from))
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature travels from the ?from to the ?to.")
				("from the ?from, ?somecreature moves to the ?to.")
			)
		)
		(:action bringperson
			:parameters     ((?transporter - creature) (?cargo - creature) (?from - location) (?to - location))
			:precondition
								(and
									(alive ?transporter)
									(at ?transporter ?from)
									(at ?cargo ?from)
									(adjacent ?from ?to)
									(not (equals ?transporter ?cargo))
									(not (equals ?from ?to))
								)

			:effect
								(and
									(at ?transporter ?to)
									(not (at ?transporter ?from))
									(at ?cargo ?to)
									(not (at ?cargo ?from))
								)

			:agents         ((?transporter))
			:humanreadable  (
				("?transporter carried ?cargo from ?from to ?to.")
			)
		)
		(:action delegate_getquest
			:parameters     ((?fromcreature - creature) (?tocreature - creature) (?somemcguffin - mcguffin) (?someplace - location))
			:precondition
								(and
									(alive ?fromcreature)
									(alive ?tocreature)
									(at ?fromcreature ?someplace)
									(at ?tocreature ?someplace)
									(not (equals ?fromcreature ?tocreature))
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
		(:action fallsinlove
			:parameters     ((?inlover - creature) (?inlovee - creature) (?someplace - location))
			:precondition
								(and
									(alive ?inlover)
									(at ?inlover ?someplace)
									(at ?inlovee ?someplace)
									(not (equals ?inlover ?inlovee))
									(not (loves ?inlover ?inlovee))
								)

			:effect
								(and
									(loves ?inlover ?inlovee)
									(inlove ?inlover)
								)

			:agents         ((?inlover))
			:humanreadable  (
				("?inlover falls in love with ?inlovee while they are in ?someplace.")
			)
		)
		(:action fallsinlovefromafar
			:parameters     ((?inlover - creature) (?inlovee - creature))
			:precondition
								(and
									(alive ?inlover)
									(not (equals ?inlover ?inlovee))
									(not (loves ?inlover ?inlovee))
								)

			:effect
								(and
									(loves ?inlover ?inlovee)
									(inlove ?inlover)
									(intends ?inlover (marriedto ?inlover ?inlovee) )
								)

			:agents         ((?inlover))
			:humanreadable  (
				("for some reason, ?inlover fell in love with ?inlovee.")
			)
		)
		(:action proposeformoney
			:parameters     ((?proposer - creature) (?proposee - creature) (?someplace - location))
			:precondition
								(and
									(alive ?proposer)
									(alive ?proposee)
									(at ?proposer ?someplace)
									(at ?proposee ?someplace)
									(single ?proposer)
									(rich ?proposee)
									(not (equals ?proposer ?proposee))
								)

			:effect
								(and
									(hasproposedto ?proposer ?proposee)
									(hasproposed ?proposer)
									(hasbeenproposedto ?proposee)
								)

			:agents         ((?proposer))
			:humanreadable  (
				("hoping to be rich, ?proposer proposed marriage to ?proposee at the ?someplace.")
			)
		)
		(:action proposeforlove
			:parameters     ((?proposer - creature) (?proposee - creature) (?someplace - location))
			:precondition
								(and
									(alive ?proposer)
									(alive ?proposee)
									(at ?proposer ?someplace)
									(at ?proposee ?someplace)
									(single ?proposer)
									(loves ?proposer ?proposee)
									(not (equals ?proposer ?proposee))
								)

			:effect
								(and
									(hasproposedto ?proposer ?proposee)
									(hasproposed ?proposer)
									(hasbeenproposedto ?proposee)
								)

			:agents         ((?proposer))
			:humanreadable  (
				("hopelessly in-love, ?proposer proposed marriage to ?proposee at the ?someplace.")
			)
		)
		(:action accept
			:parameters     ((?accepter - creature) (?proposer - creature))
			:precondition
								(and
									(alive ?accepter)
									(alive ?proposer)
									(hasproposedto ?proposer ?accepter)
									(not (equals ?proposer ?accepter))
								)

			:effect
								(and
									(hasaccepted ?accepter ?proposer)
								)

			:agents         ((?accepter))
			:humanreadable  (
				("?accepter accepted the marriage proposal of ?proposer.")
			)
		)
		(:action marry
			:parameters     ((?groom - creature) (?bride - creature) (?someplace - location))
			:precondition
								(and
									(alive ?groom)
									(hasproposedto ?groom ?bride)
									(single ?groom)
									(alive ?bride)
									(hasaccepted ?bride ?groom)
									(single ?bride)
									(at ?groom ?someplace)
									(at ?bride ?someplace)
									(not (equals ?bride ?groom))
								)

			:effect
								(and
									(marriedto ?groom ?bride)
									(marriedto ?bride ?groom)
									(ismarried ?groom)
									(ismarried ?bride)
									(not (single ?groom))
									(not (single ?bride))
									(forall
										(!marry_valuable - valuable)
											(when
												(has ?groom !marry_valuable)
											then
												(and
													(rich ?bride)
												)
											)
									)
									(forall
										(!marry_valuable - valuable)
											(when
												(has ?bride !marry_valuable)
											then
												(and
													(rich ?groom)
												)
											)
									)
									(when
										(loves ?groom ?bride)
									then
										(happy ?groom)
									)
									(when
										(loves ?bride ?groom)
									then
										(happy ?bride)
									)
								)

			:agents         ((?groom) (?bride))
			:humanreadable  (
				("?groom and ?bride gets married at the ?someplace.")
			)
		)
		(:action takeitemfromcreature
			:parameters     ((?thief - creature) (?victim - creature) (?item - item) (?place - location))
			:precondition
								(and
									(alive ?thief)
									(at ?thief ?place)
									(has ?victim ?item)
									(not (equals ?thief ?victim))
								)

			:effect
								(and
									(has ?thief ?item)
									(not (has ?victim ?item))
									(isthief ?thief)
									(not (hasweapon ?victim))
									(not (rich ?victim))
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?thief !trigger_v)
												)
											then
												(and
													(rich ?thief)
												)
											)
									)
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?victim !trigger_v)
												)
											then
												(and
													(rich ?victim)
												)
											)
									)
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
								)

			:agents         ((?thief))
			:humanreadable  (
				("?thief takes ?item from ?victim while they are at ?place, ?thief is now a thief.")
			)
		)
		(:action creaturegetsitemfromplace
			:parameters     ((?somecreature - creature) (?someitem - item) (?someplace - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?someplace)
									(at ?someitem ?someplace)
								)

			:effect
								(and
									(has ?somecreature ?someitem)
									(not (at ?someitem ?someplace))
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
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?somecreature !trigger_v)
												)
											then
												(and
													(rich ?somecreature)
												)
											)
									)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature obtains ?someitem at the ?someplace.")
			)
		)
		(:action creaturelosesitematplace
			:parameters     ((?somecreature - creature) (?someitem - item) (?someplace - location))
			:precondition
								(and
									(alive ?somecreature)
									(at ?somecreature ?someplace)
									(has ?somecreature ?someitem)
								)

			:effect
								(and
									(at ?someitem ?someplace)
									(not (has ?somecreature ?someitem))
									(not (rich ?somecreature))
									(not (hasweapon ?somecreature))
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?somecreature !trigger_v)
												)
											then
												(and
													(rich ?somecreature)
												)
											)
									)
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
				("?somecreature loses ?someitem at the ?someplace.")
			)
		)
		(:action creaturegiveitemtocreature
			:parameters     ((?giver - creature) (?receiver - creature) (?someitem - item) (?someplace - location))
			:precondition
								(and
									(at ?giver ?someplace)
									(at ?receiver ?someplace)
									(has ?giver ?someitem)
									(not (equals ?giver ?receiver))
								)

			:effect
								(and
									(has ?receiver ?someitem)
									(not (has ?giver ?someitem))
									(not (hasweapon ?giver))
									(not (rich ?giver))
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?giver !trigger_v)
												)
											then
												(and
													(rich ?giver)
												)
											)
									)
									(forall
										(!trigger_v - valuable)
											(when
												(and
													(has ?receiver !trigger_v)
												)
											then
												(and
													(rich ?receiver)
												)
											)
									)
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
													(hasweapon ?giver)
												)
											)
									)
								)

			:agents         ((?giver) (?receiver))
			:humanreadable  (
				("?giver gives ?someitem to ?receiver at the ?someplace.")
			)
		)
		(:action gethungry
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(not (hungry ?somecreature))
								)

			:effect
								(and
									(hungry ?somecreature)
									(intends ?somecreature (not (hungry ?somecreature))
 )
								)

			:humanreadable  (
				("?somecreature becomes hungry.")
			)
		)
		(:action monstereats
			:parameters     ((?monster - monster) (?somecreature - creature) (?someplace - location))
			:precondition
								(and
									(alive ?monster)
									(at ?monster ?someplace)
									(hungry ?monster)
									(alive ?somecreature)
									(at ?somecreature ?someplace)
									(not (equals ?monster ?somecreature))
								)

			:effect
								(and
									(not (hungry ?monster))
									(not (alive ?somecreature))
									(not (rich ?somecreature))
									(not (happy ?somecreature))
								)

			:agents         ((?monster))
			:humanreadable  (
				("?monster devoured ?somecreature at the ?someplace.")
			)
		)
		(:action huntrawmeat
			:parameters     ((?somecreature - creature) (?huntingground - location))
			:precondition
								(and
									(hungry ?somecreature)
									(at ?somecreature ?huntingground)
								)

			:effect
								(and
									(hasrawmeat ?somecreature)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature hunted for meat at ?huntingground.")
			)
		)
		(:action monstereatrawmeat
			:parameters     ((?somecreature - monster))
			:precondition
								(and
									(hasrawmeat ?somecreature)
								)

			:effect
								(and
									(not (hasrawmeat ?somecreature))
									(not (hungry ?somecreature))
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature ate raw meat.")
			)
		)
		(:action personeatrawmeat
			:parameters     ((?somecreature - person))
			:precondition
								(and
									(hasrawmeat ?somecreature)
								)

			:effect
								(and
									(not (hasrawmeat ?somecreature))
									(not (hungry ?somecreature))
									(issick ?somecreature)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature ate raw meat and became sick.")
			)
		)
		(:action creaturedetainssperson
			:parameters     ((?detainer - creature) (?victim - person) (?someplace - location))
			:precondition
								(and
									(at ?detainer ?someplace)
									(at ?victim ?someplace)
									(not (equals ?detainer ?victim))
								)

			:effect
								(and
									(isdetained ?victim)
								)

			:agents         ((?detainer))
			:humanreadable  (
				("?detainer detains ?victim at the ?someplace.")
			)
		)
		(:action monsterdetainssperson
			:parameters     ((?detainer - monster) (?victim - person) (?someplace - location))
			:precondition
								(and
									(at ?detainer ?someplace)
									(at ?victim ?someplace)
									(not (equals ?detainer ?victim))
									(not (hasweapon ?victim))
								)

			:effect
								(and
									(isdetained ?victim)
								)

			:agents         ((?detainer))
			:humanreadable  (
				("?detainer detains ?victim at the ?someplace.")
			)
		)
		(:action creatureescapes
			:parameters     ((?victim - person) (?fromplace - location) (?toplace - location))
			:precondition
								(and
									(isdetained ?victim)
									(at ?victim ?fromplace)
									(adjacent ?fromplace ?toplace)
								)

			:effect
								(and
									(not (isdetained ?victim))
									(at ?victim ?toplace)
									(not (at ?victim ?fromplace))
								)

			:agents         ((?victim))
			:humanreadable  (
				("?victim escapes detention from the ?fromplace to the ?toplace.")
			)
		)
		(:action creaturerescueperson
			:parameters     ((?rescuer - creature) (?victim - person) (?fromplace - location) (?toplace - location))
			:precondition
								(and
									(isdetained ?victim)
									(at ?victim ?fromplace)
									(at ?rescuer ?fromplace)
									(adjacent ?fromplace ?toplace)
									(not (equals ?fromplace ?toplace))
									(not (equals ?rescuer ?victim))
								)

			:effect
								(and
									(not (isdetained ?victim))
									(at ?victim ?toplace)
									(not (at ?victim ?fromplace))
								)

			:agents         ((?rescuer) (?victim))
			:humanreadable  (
				("?rescuer rescues ?victim from the ?fromplace, they escape to the ?toplace.")
			)
		)
		(:action creaturekillcreature_withweapon
			:parameters     ((?offender - creature) (?defender - creature) (?someplace - location))
			:precondition
								(and
									(alive ?offender)
									(alive ?defender)
									(hasweapon ?offender)
									(at ?offender ?someplace)
									(at ?defender ?someplace)
									(not (equals ?offender ?defender))
								)

			:effect
								(and
									(not (alive ?defender))
								)

			:agents         ((?offender))
			:humanreadable  (
				("?offender kills ?defender at the ?someplace using a weapon.")
			)
		)
		(:action creaturekillcreature_noweapon
			:parameters     ((?offender - creature) (?defender - creature) (?someplace - location))
			:precondition
								(and
									(alive ?offender)
									(alive ?defender)
									(at ?offender ?someplace)
									(at ?defender ?someplace)
									(not (equals ?offender ?defender))
								)

			:effect
								(and
									(not (alive ?defender))
								)

			:agents         ((?offender))
			:humanreadable  (
				("?offender kills ?defender at the ?someplace.")
			)
		)
		(:action creatureinjurescreature_withweapon
			:parameters     ((?offender - creature) (?defender - creature) (?someplace - location))
			:precondition
								(and
									(alive ?offender)
									(alive ?defender)
									(hasweapon ?offender)
									(at ?offender ?someplace)
									(at ?defender ?someplace)
									(not (equals ?offender ?defender))
								)

			:effect
								(and
									(when
										(and
											(isheavilyinjured ?defender)
											(alive ?defender)
										)
									then
										(and
											(not (alive ?defender))
										)
									)
									(when
										(and
											(isinjured ?defender)
											(alive ?defender)
										)
									then
										(and
											(not (isinjured ?defender))
											(isheavilyinjured ?defender)
										)
									)
									(when
										(and
											(not (isinjured ?defender))
											(not (isheavilyinjured ?defender))
											(alive ?defender)
										)
									then
										(and
											(isinjured ?defender)
										)
									)
								)

			:agents         ((?offender))
			:humanreadable  (
				("?offender injures ?defender at the ?someplace with a weapon.")
			)
		)
		(:action creatureinjurescreature_noweapon
			:parameters     ((?offender - creature) (?defender - creature) (?someplace - location))
			:precondition
								(and
									(alive ?offender)
									(alive ?defender)
									(at ?offender ?someplace)
									(at ?defender ?someplace)
									(not (equals ?offender ?defender))
								)

			:effect
								(and
									(when
										(and
											(isheavilyinjured ?defender)
											(alive ?defender)
										)
									then
										(and
											(not (alive ?defender))
										)
									)
									(when
										(and
											(isinjured ?defender)
											(alive ?defender)
										)
									then
										(and
											(not (isinjured ?defender))
											(isheavilyinjured ?defender)
										)
									)
									(when
										(and
											(not (isinjured ?defender))
											(not (isheavilyinjured ?defender))
											(alive ?defender)
										)
									then
										(and
											(isinjured ?defender)
										)
									)
								)

			:agents         ((?offender))
			:humanreadable  (
				("?offender injures ?defender at the ?someplace.")
			)
		)
		(:action creaturebleedsout
			:parameters     ((?injured - creature))
			:precondition
								(and
									(alive ?injured)
									(isinjured ?injured)
									(isheavilyinjured ?injured)
								)

			:effect
								(and
									(not (isinjured ?injured))
									(not (alive ?injured))
								)

			:humanreadable  (
				("injured, ?injured bleeds to death.")
			)
		)
		(:action creaturehealsinjury
			:parameters     ((?healer - creature) (?injured - creature) (?someplace - location))
			:precondition
								(and
									(alive ?healer)
									(alive ?injured)
									(at ?healer ?someplace)
									(at ?injured ?someplace)
									(isinjured ?injured)
								)

			:effect
								(and
									(not (isinjured ?injured))
								)

			:agents         ((?healer) (?injured))
			:humanreadable  (
				("?healer heals the injuries of ?injured at the ?someplace.")
			)
		)
		(:action creature_lackrealized_single
			:parameters     ((?realizer - creature) (?somecreature - creature))
			:precondition
								(and
									(single ?somecreature)
									(not (lackrealized_single ?realizer ?somecreature))
								)

			:effect
								(and
									(lackrealized_single ?realizer ?somecreature)
								)

			:humanreadable  (
				("?realizer realized that ?somecreature is single. ?realizer may decide to do something about this.")
			)
		)
		(:action creature_lackrealized_nothas
			:parameters     ((?realizer - creature) (?somecreature - creature) (?someitem - item))
			:precondition
								(and
									(not (has ?somecreature ?someitem))
									(not (lackrealized_nothas ?realizer ?somecreature ?someitem))
								)

			:effect
								(and
									(lackrealized_nothas ?realizer ?somecreature ?someitem)
								)

			:humanreadable  (
				("?realizer realized that ?somecreature does not have ?someitem. ?realizer may decide to do something about this.")
			)
		)
		(:action creature_lackrealized_notrich
			:parameters     ((?realizer - creature) (?somecreature - creature))
			:precondition
								(and
									(not (rich ?somecreature))
								)

			:effect
								(and
									(lackrealized_notrich ?realizer ?somecreature)
								)

			:humanreadable  (
				("?realizer realized that ?somecreature is not rich. ?realizer may decide to do something about this.")
			)
		)
		(:action creature_goodmoods_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_goodmood ?target))
								)

			:effect
								(and
									(emo_goodmood ?target)
								)

			:agents         ((?actor) (?target))
			:humanreadable  (
				("?actor did something at the ?someplace which put ?target in a good mood.")
			)
		)
		(:action creature_badmoods_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_badmood ?target))
								)

			:effect
								(and
									(emo_badmood ?target)
								)

			:agents         ((?actor))
			:humanreadable  (
				("?actor did something at the ?someplace which put ?target in a bad mood.")
			)
		)
		(:action creature_encourage_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_feelstrong ?target))
								)

			:effect
								(and
									(emo_feelstrong ?target)
								)

			:agents         ((?actor))
			:humanreadable  (
				("?actor encourages ?target at the ?someplace, ?target feels stronger.")
			)
		)
		(:action creature_discourage_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_feelweak ?target))
								)

			:effect
								(and
									(emo_feelweak ?target)
								)

			:agents         ((?actor))
			:humanreadable  (
				("?actor discourages ?target at the ?someplace. ?target feels weaker.")
			)
		)
		(:action creature_enfocus_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_focused ?target))
								)

			:effect
								(and
									(emo_focused ?target)
								)

			:agents         ((?actor))
			:humanreadable  (
				("?actor did something at the ?someplace to increase the focus of ?target.")
			)
		)
		(:action creature_confuse_creature
			:parameters     ((?actor - creature) (?target - creature) (?someplace - location))
			:precondition
								(and
									(at ?actor ?someplace)
									(at ?target ?someplace)
									(not (equals ?actor ?target))
									(not (emo_confused ?target))
								)

			:effect
								(and
									(emo_confused ?target)
								)

			:agents         ((?actor))
			:humanreadable  (
				("?actor did something at the ?someplace to create confusion for ?target.")
			)
		)
		(:action creature_beginjourneyhome
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(equals ?somecreature ?somecreature)
								)

			:effect
								(and
									(ending_beginjourneyhome ?somecreature)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("?somecreature begins the journey home.")
			)
		)
		(:action creature_becomessick
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(not (issick ?somecreature))
								)

			:effect
								(and
									(issick ?somecreature)
								)

			:humanreadable  (
				("?somecreature suddenly becomes sick.")
			)
		)
		(:action creature_healsick
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(issick ?somecreature)
								)

			:effect
								(and
									(not (issick ?somecreature))
								)

			:humanreadable  (
				("?somecreature recovers from sickness.")
			)
		)
		(:action creature_healscreature
			:parameters     ((?healer - creature) (?sickone - creature) (?someplace - location))
			:precondition
								(and
									(issick ?sickone)
									(ishealer ?healer)
									(at ?healer ?someplace)
									(at ?sickone ?someplace)
								)

			:effect
								(and
									(not (issick ?sickone))
								)

			:agents         ((?healer))
			:humanreadable  (
				("?healer heals the sickness of ?sickone at the ?someplace.")
			)
		)
		(:action creature_infects_creature
			:parameters     ((?infector - creature) (?infectee - creature) (?someplace - location))
			:precondition
								(and
									(issick ?infector)
									(at ?infector ?someplace)
									(at ?infectee ?someplace)
									(not (equals ?infector ?infectee))
									(not (issick ?infectee))
								)

			:effect
								(and
									(issick ?infectee)
								)

			:humanreadable  (
				("?infector infects ?infectee at the ?someplace.")
			)
		)
		(:action trigger_itemgain
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(equals ?somecreature ?somecreature)
								)

			:effect
								(and
									(forall
										(!trigger_v - valuable)
											(when
												(has ?somecreature !trigger_v)
											then
												(and
													(rich ?somecreature)
												)
											)
									)
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

			:humanreadable  (
				("trigger_itemgain for ?somecreature")
			)
		)
		(:action trigger_itemlose
			:parameters     ((?somecreature - creature))
			:precondition
								(and
									(equals ?somecreature ?somecreature)
								)

			:effect
								(and
									(forall
										(!trigger_v - valuable)
											(when
												(not (has ?somecreature !trigger_v))
											then
												(not (rich ?somecreature))
											)
									)
									(forall
										(!trigger_w - weapon)
											(when
												(not (has ?somecreature !trigger_w))
											then
												(not (hasweapon ?somecreature))
											)
									)
								)

			:agents         ((?somecreature))
			:humanreadable  (
				("trigger_itemlose for ?somecreature")
			)
		)
)
