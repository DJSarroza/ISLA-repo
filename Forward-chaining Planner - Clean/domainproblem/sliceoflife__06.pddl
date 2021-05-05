(define (domain sliceoflife06)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(student actor)
		(teacher actor)
		(clique group)
		(school group)
		(group predicate)
		(mundane_thing physical_thing)
		(special_thing physical_thing)
		(physical_thing object)
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

		(:predicate rel_marker
			:parameters     ((?actor1 - actor) (?actor2 - actor))
			:definition     (rel_marker (?actor1 - actor) (?actor2 - actor))
			:primary_obj    ((?actor1 - actor))
			:humanreadable  (
				("unresolved relationship marker between ?actor1 and ?actor2.")
			)
		)

		(:predicate belongs_to_group
			:parameters     ((?someactor - actor) (?somegroup - group))
			:definition     (belongs_to_group (?someactor - actor) (?somegroup - group))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor belongs to ?somegroup.")
			)
		)

		(:predicate likes
			:parameters     ((?liker - actor) (?likee - actor))
			:definition     (likes (?liker - actor) (?likee - actor))
			:primary_obj    ((?liker - actor))
			:humanreadable  (
				("?liker likes ?likee.")
			)
		)

		(:predicate is_popular
			:parameters     ((?someactor - actor))
			:definition     (is_popular (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is popular.")
			)
		)

		(:predicate is_embarassed
			:parameters     ((?someactor - actor))
			:definition     (is_embarassed (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is embarassed.")
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

		(:predicate has_thing
			:parameters     ((?someactor - actor) (?something - physical_thing))
			:definition     (has_thing (?someactor - actor) (?something - physical_thing))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has ?something.")
			)
		)

		(:predicate dislikes
			:parameters     ((?person1 - actor) (?person2 - actor))
			:definition     (dislikes (?person1 - actor) (?person2 - actor))
			:primary_obj    ((?person1 - actor))
			:humanreadable  (
				("?person1 dislikes ?person2.")
			)
		)

		(:predicate is_aloof
			:parameters     ((?someactor - actor))
			:definition     (is_aloof (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is aloof.")
			)
		)

		(:predicate is_indifferent
			:parameters     ((?someactor - actor))
			:definition     (is_indifferent (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is indifferent.")
			)
		)

		(:predicate loves
			:parameters     ((?person1 - actor) (?person2 - actor))
			:definition     (loves (?person1 - actor) (?person2 - actor))
			:primary_obj    ((?person1 - actor))
			:humanreadable  (
				("?person1 loves ?person2.")
			)
		)

		(:predicate hates
			:parameters     ((?person1 - actor) (?person2 - actor))
			:definition     (hates (?person1 - actor) (?person2 - actor))
			:primary_obj    ((?person1 - actor))
			:humanreadable  (
				("?person1 hates ?person2.")
			)
		)

		(:predicate friends_with
			:parameters     ((?first_person - student) (?another_person - student))
			:definition     (friends_with (?first_person - student) (?another_person - student))
			:primary_obj    ((?first_person - student))
			:humanreadable  (
				("?first_person is friends with ?another_person.")
			)
		)

	)

		(:action move
			:parameters     ((?someactor - actor) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?someactor ?fromloc)
									(not (at ?someactor ?toloc))
									(not (equals ?fromloc ?toloc))
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
		(:action give_mundane_item
			:parameters     ((?giver - student) (?recepient - student) (?thingie - mundane_thing) (?loc1 - location) (?random_person - student))
			:precondition
								(and
									(at ?giver ?loc1)
									(at ?recepient ?loc1)
									(at ?thingie ?loc1)
									(at ?random_person ?loc1)
									(not (equals ?giver ?recepient))
									(not (equals ?giver ?random_person))
									(not (equals ?recepient ?random_person))
									(has_thing ?giver ?thingie)
								)

			:effect
								(and
									(not (has_thing ?giver ?thingie))
									(has_thing ?recepient ?thingie)
									(rel_marker ?giver ?recepient)
									(rel_marker ?recepient ?random_person)
									(rel_marker ?random_person ?giver)
								)

			:agents         ((?giver))
			:humanreadable  (
				("?giver gives ?thingie to ?recepient at ?loc1, ?random_person witnessed the event.")
			)
		)
		(:action rm_hates
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(hates ?actor1 ?actor2)
									(not (rel_marker ?actor1 ?actor2))
								)

			:humanreadable  (
				("?actor1 now hates ?actor2.")
			)
		)
		(:action rm_loves
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(loves ?actor1 ?actor2)
								)

			:humanreadable  (
				("?actor1 now loves ?actor2.")
			)
		)
		(:action give_item
			:parameters     ((?giver - student) (?receiver - student) (?thingie - physical_thing) (?loc1 - location) (?random_person - student))
			:precondition
								(and
									(at ?giver ?loc1)
									(at ?receiver ?loc1)
									(at ?thingie ?loc1)
									(at ?random_person ?loc1)
									(not (equals ?giver ?receiver))
									(not (equals ?giver ?random_person))
									(not (equals ?receiver ?random_person))
									(has_thing ?giver ?thingie)
								)

			:effect
								(and
									(not (has_thing ?giver ?thingie))
									(has_thing ?receiver ?thingie)
									(rel_marker ?giver ?receiver)
									(rel_marker ?receiver ?random_person)
									(rel_marker ?random_person ?giver)
								)

			:agents         ((?giver))
			:humanreadable  (
				("?giver gives ?thingie to ?receiver at ?loc1, ?random_person witnessed the event.")
			)
		)
		(:action rm_likes
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(likes ?actor1 ?actor2)
									(not (rel_marker ?actor1 ?actor2))
								)

			:humanreadable  (
				("?actor1 now likes ?actor2.")
			)
		)
		(:action rm_dislikes
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(dislikes ?actor1 ?actor2)
								)

			:humanreadable  (
				("?actor1 now dislikes ?actor2.")
			)
		)
		(:action rm_aloof
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(is_aloof ?actor1)
								)

			:humanreadable  (
				("?actor1 is now aloof because of ?actor2.")
			)
		)
		(:action rm_confident
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(is_confident ?actor1)
								)

			:humanreadable  (
				("?actor1 is now confident because of ?actor2.")
			)
		)
		(:action rm_embarassed
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(is_embarassed ?actor1)
								)

			:humanreadable  (
				("?actor1 is now embarassed because of ?actor2.")
			)
		)
		(:action rm_indifferent
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(is_indifferent ?actor1)
								)

			:humanreadable  (
				("?actor1 is now indifferent because of ?actor2.")
			)
		)
		(:action rm_popular
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(is_popular ?actor1)
								)

			:humanreadable  (
				("?actor1 is now somehow popular because of ?actor2.")
			)
		)
		(:action take_thing
			:parameters     ((?taker - actor) (?victim - actor) (?thingie - physical_thing) (?loc1 - location))
			:precondition
								(and
									(at ?taker ?loc1)
									(at ?thingie ?loc1)
									(has_thing ?victim ?thingie)
									(not (equals ?taker ?victim))
								)

			:effect
								(and
									(not (has_thing ?victim ?thingie))
									(has_thing ?taker ?thingie)
									(rel_marker ?victim ?taker)
								)

			:agents         ((?taker))
			:humanreadable  (
				("?taker took ?thingie from ?victim at ?loc1.")
			)
		)
		(:action pick_up_thing
			:parameters     ((?taker - student) (?thingie - physical_thing) (?loc1 - location))
			:precondition
								(and
									(at ?taker ?loc1)
									(at ?thingie ?loc1)
									(not (has_thing ?taker ?thingie))
								)

			:effect
								(and
									(forall
										(!potential_owner - actor)
											(when
												(and
													(has_thing !potential_owner ?thingie)
												)
											then
												(and
													(not (has_thing !potential_owner ?thingie))
												)
											)
									)
									(has_thing ?taker ?thingie)
									(not (at ?thingie ?loc1))
								)

			:agents         ((?taker))
			:humanreadable  (
				("?taker picked up ?thingie at ?loc1.")
			)
		)
		(:action do_cool_thing
			:parameters     ((?mainactor - student) (?someloc - location) (?something - physical_thing) (?audience1 - student))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(at ?something ?someloc)
									(at ?mainactor ?someloc)
									(not (equals ?mainactor ?audience1))
								)

			:effect
								(and
									(rel_marker ?mainactor ?audience1)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something cool involving ?something at ?someloc. ?audience1 and witnessed the event.")
			)
		)
		(:action rm_not_aloof
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(not (is_aloof ?actor1))
								)

			:humanreadable  (
				("?actor1 is no longer aloof because of ?actor2.")
			)
		)
		(:action rm_not_confident
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(not (is_confident ?actor1))
								)

			:humanreadable  (
				("?actor1 is no longer confident because of ?actor2.")
			)
		)
		(:action rm_not_embarassed
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(not (is_embarassed ?actor1))
								)

			:humanreadable  (
				("?actor1 is no longer embarassed because of ?actor2.")
			)
		)
		(:action rm_not_indifferent
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(not (is_indifferent ?actor1))
								)

			:humanreadable  (
				("?actor1 is no longer indifferent because of ?actor2.")
			)
		)
		(:action rm_not_popular
			:parameters     ((?actor1 - student) (?actor2 - student))
			:precondition
								(and
									(rel_marker ?actor1 ?actor2)
								)

			:effect
								(and
									(not (rel_marker ?actor1 ?actor2))
									(not (is_popular ?actor1))
								)

			:humanreadable  (
				("?actor1 is no longer popular because of ?actor2.")
			)
		)
		(:action do_embarassing_thing
			:parameters     ((?mainactor - student) (?someloc - location) (?something - physical_thing) (?audience1 - student))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(not (equals ?mainactor ?audience1))
									(at ?something ?someloc)
									(at ?mainactor ?someloc)
								)

			:effect
								(and
									(rel_marker ?mainactor ?audience1)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something embarassing involving ?something at ?someloc. ?audience1 and witnessed the event.")
			)
		)
		(:action do_elegant_thing
			:parameters     ((?mainactor - student) (?someloc - location) (?something - physical_thing) (?audience1 - student))
			:precondition
								(and
									(at ?mainactor ?someloc)
									(not (equals ?mainactor ?audience1))
									(at ?something ?someloc)
									(at ?mainactor ?someloc)
								)

			:effect
								(and
									(rel_marker ?mainactor ?audience1)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did something elegant involving ?something at ?someloc. ?audience1 and witnessed the event.")
			)
		)
		(:action friendly_act
			:parameters     ((?mainactor - student) (?person1 - student) (?loc1 - location) (?random_person - student))
			:precondition
								(and
									(at ?mainactor ?loc1)
									(not (equals ?mainactor ?person1))
									(at ?person1 ?loc1)
									(not (equals ?mainactor ?random_person))
									(at ?random_person ?loc1)
									(not (equals ?person1 ?random_person))
								)

			:effect
								(and
									(friends_with ?mainactor ?person1)
									(rel_marker ?random_person ?mainactor)
									(rel_marker ?person1 ?random_person)
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did a friendly act towards ?person1 at ?loc1. ?random_person saw this.")
			)
		)
		(:action unfriendly_act
			:parameters     ((?mainactor - student) (?person1 - student) (?loc1 - location) (?random_person - student))
			:precondition
								(and
									(at ?mainactor ?loc1)
									(not (equals ?mainactor ?person1))
									(at ?person1 ?loc1)
									(not (equals ?mainactor ?random_person))
									(at ?random_person ?loc1)
									(not (equals ?person1 ?random_person))
								)

			:effect
								(and
									(not (friends_with ?person1 ?mainactor))
									(not (friends_with ?mainactor ?person1))
									(not (rel_marker ?random_person ?mainactor))
								)

			:agents         ((?mainactor))
			:humanreadable  (
				("?mainactor did an unfriendly act towards ?person1 at ?loc1. ?random_person saw this.")
			)
		)
		(:action befriend
			:parameters     ((?friender - student) (?friendee - student) (?loc1 - location))
			:precondition
								(and
									(not (equals ?friender ?friendee))
									(at ?friender ?loc1)
									(at ?friendee ?loc1)
									(not (friends_with ?friender ?friendee))
								)

			:effect
								(and
									(friends_with ?friender ?friendee)
								)

			:agents         ((?friender))
			:humanreadable  (
				("?friender befriended ?friendee at ?loc1.")
			)
		)
)
