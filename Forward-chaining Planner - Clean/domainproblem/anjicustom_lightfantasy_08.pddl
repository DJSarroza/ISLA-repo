(define (domain anjicustom08)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(mundane_thing thing)
		(special_thing thing)
		(person actor)
		(animal actor)
		(thing object)
		(portal_key special_thing)
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
			:parameters     ((?someobj - object) (?somelocation2 - location))
			:definition     (at (?someobj - object) (?somelocation2 - location))
			:primary_obj    ((?someobj - object))
			:humanreadable  (
				("?someobj is at ?somelocation2.")
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

		(:predicate has_thing
			:parameters     ((?someactor - actor) (?something - thing))
			:definition     (has_thing (?someactor - actor) (?something - thing))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has ?something.")
			)
		)

		(:predicate exit_portal_open
			:parameters     ((?someloc - location))
			:definition     (exit_portal_open (?someloc - location))
			:primary_obj    ((?someloc - location))
			:humanreadable  (
				("The exit portal at ?someloc is open.")
			)
		)

		(:predicate is_confident
			:parameters     ((?someactor - actor))
			:definition     (is_confident (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is confident.")
			)
		)

		(:predicate is_scared
			:parameters     ((?someactor - actor))
			:definition     (is_scared (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is scared.")
			)
		)

		(:predicate is_tired
			:parameters     ((?someactor - actor))
			:definition     (is_tired (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is tired.")
			)
		)

		(:predicate familiar_place
			:parameters     ((?someactor - actor) (?someloc - location))
			:definition     (familiar_place (?someactor - actor) (?someloc - location))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is familiar with ?someloc.")
			)
		)

		(:predicate __emotion
			:parameters     ((?someactor - actor))
			:definition     (__emotion (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("unresolved emotion marker for ?someactor.")
			)
		)

		(:predicate portal_location
			:parameters     ((?someloc - location))
			:definition     (portal_location (?someloc - location))
			:primary_obj    ((?someloc - location))
			:humanreadable  (
				("?someloc is the location of an exit portal.")
			)
		)

		(:predicate seen_portal_at_location
			:parameters     ((?someactor - actor) (?somelocation - location))
			:definition     (seen_portal_at_location (?someactor - actor) (?somelocation - location))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has seen the portal at ?somelocation.")
			)
		)

		(:predicate found_a_portal
			:parameters     ((?someactor - actor))
			:definition     (found_a_portal (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has found a portal.")
			)
		)

		(:predicate used_the_portal
			:parameters     ((?someactor - actor))
			:definition     (used_the_portal (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has used the portal.")
			)
		)

	)

		(:action move
			:parameters     ((?someactor - actor) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(not (equals ?fromloc ?toloc))
									(at ?someactor ?fromloc)
									(not (at ?someactor ?toloc))
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?someactor ?fromloc))
									(at ?someactor ?toloc)
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor moves from ?fromloc to ?toloc.")
			)
		)
		(:action do_cool_thing
			:parameters     ((?mainactor - actor) (?someloc - location) (?something - thing))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(has_thing ?mainactor ?something)
								)

			:effect
								(and
									(__emotion ?mainactor)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something cool involving ?something at ?someloc.")
			)
		)
		(:action __resolve_emotion_confident
			:parameters     ((?someactor - actor))
			:precondition
								(and
									(__emotion ?someactor)
								)

			:effect
								(and
									(not (__emotion ?someactor))
									(is_confident ?someactor)
								)

			:humanreadable  (
				("?someactor becomes confident.")
				("?someactor gains confidence.")
			)
		)
		(:action get_thing_from_place
			:parameters     ((?someactor - actor) (?something - thing) (?someplace - location))
			:precondition
								(and
									(at ?someactor ?someplace)
									(at ?something ?someplace)
									(not (has_thing ?someactor ?something))
								)

			:effect
								(and
									(forall
										(!otheractors - actor)
											(when
												(and
													(has_thing !otheractors ?something)
												)
											then
												(and
													(not (has_thing !otheractors ?something))
												)
											)
									)
									(has_thing ?someactor ?something)
									(not (at ?something ?someplace))
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor obtains ?something at ?someplace.")
			)
		)
		(:action open_portal_using_key
			:parameters     ((?someactor - actor) (?key - portal_key) (?someloc - location))
			:precondition
								(and
									(at ?someactor ?someloc)
									(has_thing ?someactor ?key)
									(portal_location ?someloc)
									(not (exit_portal_open ?someloc))
								)

			:effect
								(and
									(exit_portal_open ?someloc)
									(not (has_thing ?someactor ?key))
									(at ?key ?someloc)
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor opened the portal at ?someloc with ?key.")
			)
		)
		(:action lose_thing_at_place
			:parameters     ((?someactor - actor) (?something - thing) (?someloc - location))
			:precondition
								(and
									(has_thing ?someactor ?something)
									(at ?someactor ?someloc)
								)

			:effect
								(and
									(at ?something ?someloc)
									(not (has_thing ?someactor ?something))
								)

			:humanreadable  (
				("?someactor loses ?something at ?someloc.")
				("?someactor somehow dropped ?something at ?someloc.")
			)
		)
		(:action __resolve_emotion_scared
			:parameters     ((?someactor - actor))
			:precondition
								(and
									(__emotion ?someactor)
								)

			:effect
								(and
									(not (__emotion ?someactor))
									(is_scared ?someactor)
								)

			:humanreadable  (
				("?someactor becomes scared.")
			)
		)
		(:action __resolve_emotion_tired
			:parameters     ((?someactor - actor))
			:precondition
								(and
									(__emotion ?someactor)
								)

			:effect
								(and
									(not (__emotion ?someactor))
									(is_tired ?someactor)
								)

			:humanreadable  (
				("?someactor becomes tired.")
			)
		)
		(:action do_embarassing_thing
			:parameters     ((?mainactor - actor) (?someloc - location) (?something - thing))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(has_thing ?mainactor ?something)
								)

			:effect
								(and
									(__emotion ?mainactor)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something embarassing involving ?something at ?someloc.")
			)
		)
		(:action do_elegant_thing
			:parameters     ((?mainactor - actor) (?someloc - location) (?something - thing))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(has_thing ?mainactor ?something)
								)

			:effect
								(and
									(__emotion ?mainactor)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something elegant involving ?something at ?someloc.")
			)
		)
		(:action do_awkward_thing
			:parameters     ((?mainactor - actor) (?someloc - location) (?something - thing))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(has_thing ?mainactor ?something)
								)

			:effect
								(and
									(__emotion ?mainactor)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something awkward involving ?something at ?someloc.")
			)
		)
		(:action inspect_portal
			:parameters     ((?someactor - actor) (?somelocation - location))
			:precondition
								(and
									(portal_location ?somelocation)
									(at ?someactor ?somelocation)
								)

			:effect
								(and
									(seen_portal_at_location ?someactor ?somelocation)
									(found_a_portal ?someactor)
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor inspects the portal at ?somelocation.")
			)
		)
		(:action use_portal
			:parameters     ((?mainactor - actor) (?somelocation - location))
			:precondition
								(and
									(at ?mainactor ?somelocation)
									(seen_portal_at_location ?mainactor ?somelocation)
									(exit_portal_open ?somelocation)
									(not (used_the_portal ?mainactor))
								)

			:effect
								(and
									(used_the_portal ?mainactor)
									(not (at ?mainactor ?somelocation))
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor used the portal at ?somelocation.")
			)
		)
		(:action use_portal_withkey
			:parameters     ((?mainactor - actor) (?somelocation - location) (?somekey - portal_key))
			:precondition
								(and
									(at ?mainactor ?somelocation)
									(not (used_the_portal ?mainactor))
									(seen_portal_at_location ?mainactor ?somelocation)
									(has_thing ?mainactor ?somekey)
								)

			:effect
								(and
									(used_the_portal ?mainactor)
									(not (at ?mainactor ?somelocation))
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor used the portal at ?somelocation using ?somekey.")
			)
		)
		(:action long_trek
			:parameters     ((?someactor - actor) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(not (equals ?fromloc ?toloc))
									(at ?someactor ?fromloc)
									(not (at ?someactor ?toloc))
									(not (adjacent ?fromloc ?toloc))
								)

			:effect
								(and
									(not (at ?someactor ?fromloc))
									(at ?someactor ?toloc)
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor takes a long trek from ?fromloc to ?toloc.")
			)
		)
)
