(define (domain anjicustom09)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(alien actor)
		(marine human)
		(technological_object object)
		(biological_object object)
		(alien_biomatter biological_object)
		(human_tech technological_object)
		(alien_tech technological_object)
		(unknown_biomatter biological_object)
		(human actor)
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
			:parameters     ((?someobj2 - object) (?somelocation - location))
			:definition     (at (?someobj2 - object) (?somelocation - location))
			:primary_obj    ((?someobj2 - object))
			:humanreadable  (
				("?someobj2 is at ?somelocation.")
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

		(:predicate has_object
			:parameters     ((?someactor - actor) (?someobj - object))
			:definition     (has_object (?someactor - actor) (?someobj - object))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor has ?someobj.")
			)
		)

		(:predicate alive
			:parameters     ((?someactor - actor))
			:definition     (alive (?someactor - actor))
			:primary_obj    ((?someactor - actor))
			:humanreadable  (
				("?someactor is alive.")
			)
		)

		(:predicate has_primary_ammo
			:parameters     ((?somemarine - marine))
			:definition     (has_primary_ammo (?somemarine - marine))
			:primary_obj    ((?somemarine - marine))
			:humanreadable  (
				("?somemarine has primary weapon ammo.")
			)
		)

		(:predicate has_secondary_ammo
			:parameters     ((?somemarine - marine))
			:definition     (has_secondary_ammo (?somemarine - marine))
			:primary_obj    ((?somemarine - marine))
			:humanreadable  (
				("?somemarine has secondary weapon ammo.")
			)
		)

		(:predicate has_special_ammo
			:parameters     ((?somemarine - marine))
			:definition     (has_special_ammo (?somemarine - marine))
			:primary_obj    ((?somemarine - marine))
			:humanreadable  (
				("?somemarine has special weapon ammo.")
			)
		)

		(:predicate __primary_weapon_state_marker
			:parameters     ((?somemarine - marine))
			:definition     (__primary_weapon_state_marker (?somemarine - marine))
			:primary_obj    ((?somemarine - marine))
			:humanreadable  (
				("Unresolved primary weapon state marker for ?somemarine.")
			)
		)

		(:predicate __secondary_weapon_state_marker
			:parameters     ((?somemarine - marine))
			:definition     (__secondary_weapon_state_marker (?somemarine - marine))
			:primary_obj    ((?somemarine - marine))
			:humanreadable  (
				("Unresolved secondary weapon state marker for ?somemarine.")
			)
		)

		(:predicate __emotion_state_marker
			:parameters     ((?somehuman - human))
			:definition     (__emotion_state_marker (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("Unresolved emotion state marker for ?somehuman.")
			)
		)

		(:predicate is_afraid
			:parameters     ((?somehuman - human))
			:definition     (is_afraid (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman is afraid.")
			)
		)

		(:predicate is_panicking
			:parameters     ((?somehuman - human))
			:definition     (is_panicking (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman is panicking.")
			)
		)

		(:predicate is_stressed
			:parameters     ((?somehuman - human))
			:definition     (is_stressed (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman is stressed.")
			)
		)

		(:predicate is_berserk
			:parameters     ((?somehuman - human))
			:definition     (is_berserk (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman has gone berserk.")
			)
		)

		(:predicate location_marked_secure
			:parameters     ((?somelocation - location))
			:definition     (location_marked_secure (?somelocation - location))
			:primary_obj    ((?somelocation - location))
			:humanreadable  (
				("?somelocation has been marked as secure.")
			)
		)

		(:predicate extraction_point_set
			:parameters     ((?somelocation - location))
			:definition     (extraction_point_set (?somelocation - location))
			:primary_obj    ((?somelocation - location))
			:humanreadable  (
				("?somelocation has been designated as the extraction point for the marines.")
			)
		)

		(:predicate human_abandoned
			:parameters     ((?somehuman - human))
			:definition     (human_abandoned (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman has been abandoned.")
			)
		)

		(:predicate human_extracted
			:parameters     ((?somehuman - human))
			:definition     (human_extracted (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman has been extracted from the field.")
			)
		)

		(:predicate is_excited
			:parameters     ((?somehuman - human))
			:definition     (is_excited (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman is excited.")
			)
		)

		(:predicate is_focused
			:parameters     ((?somehuman - human))
			:definition     (is_focused (?somehuman - human))
			:primary_obj    ((?somehuman - human))
			:humanreadable  (
				("?somehuman is focused.")
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
									(alive ?someactor)
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
		(:action alien_kills_human
			:parameters     ((?somealien - alien) (?somehuman - human) (?someloc - location))
			:precondition
								(and
									(at ?somealien ?someloc)
									(at ?somehuman ?someloc)
									(alive ?somealien)
									(alive ?somehuman)
								)

			:effect
								(and
									(not (alive ?somehuman))
									(forall
										(!someobj - object)
											(when
												(and
													(has_object ?somehuman !someobj)
												)
											then
												(and
													(not (has_object ?somehuman !someobj))
													(at !someobj ?someloc)
												)
											)
									)
								)

			:agents         ((?somealien))
			:humanreadable  (
				("?somealien kills ?somehuman at ?someloc.")
			)
		)
		(:action marine_kills_alien_pw
			:parameters     ((?somemarine - marine) (?somealien - alien) (?someloc - location))
			:precondition
								(and
									(at ?somemarine ?someloc)
									(at ?somealien ?someloc)
									(alive ?somemarine)
									(alive ?somealien)
									(has_primary_ammo ?somemarine)
								)

			:effect
								(and
									(not (alive ?somealien))
									(__primary_weapon_state_marker ?somemarine)
								)

			:agents         ((?somemarine))
			:humanreadable  (
				("Using the primary weapon, ?somemarine kills ?somealien at ?someloc.")
			)
		)
		(:action kill_indiscriminately
			:parameters     ((?somemarine - marine) (?someactor - actor) (?someloc - location))
			:precondition
								(and
									(at ?somemarine ?someloc)
									(alive ?somemarine)
									(has_primary_ammo ?somemarine)
									(is_berserk ?somemarine)
									(alive ?someactor)
									(at ?someactor ?someloc)
								)

			:effect
								(and
									(__primary_weapon_state_marker ?somemarine)
									(not (alive ?someactor))
									(forall
										(!someobj - object)
											(when
												(and
													(has_object ?someactor !someobj)
												)
											then
												(and
													(not (has_object ?someactor !someobj))
													(at !someobj ?someloc)
												)
											)
									)
								)

			:agents         ((?somemarine))
			:humanreadable  (
				("Having gone berserk, ?somemarine indiscriminately kills ?someactor at ?someloc.")
			)
		)
		(:action force_secure_location
			:parameters     ((?somemarine1 - marine) (?somemarine2 - marine) (?somelocation - location))
			:precondition
								(and
									(at ?somemarine1 ?somelocation)
									(at ?somemarine2 ?somelocation)
									(alive ?somemarine1)
									(alive ?somemarine2)
								)

			:effect
								(and
									(forall
										(!somealien - alien)
											(when
												(and
													(at !somealien ?somelocation)
													(alive !somealien)
												)
											then
												(and
													(not (alive !somealien))
												)
											)
									)
									(location_marked_secure ?somelocation)
									(__emotion_state_marker ?somemarine1)
									(__emotion_state_marker ?somemarine2)
									(__primary_weapon_state_marker ?somemarine1)
									(__primary_weapon_state_marker ?somemarine2)
									(__secondary_weapon_state_marker ?somemarine1)
									(__secondary_weapon_state_marker ?somemarine2)
								)

			:agents         ((?somemarine1) (?somemarine2))
			:humanreadable  (
				("Marines ?somemarine1 and ?somemarine2 secured ?somelocation, killing all aliens in the area.")
			)
		)
		(:action _resolve_emo_afraid
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(not (is_afraid ?somehuman))
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(is_afraid ?somehuman)
								)

			:humanreadable  (
				("?somehuman became afraid.")
			)
		)
		(:action _resolve_emo_panic
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(not (is_panicking ?somehuman))
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(is_panicking ?somehuman)
								)

			:humanreadable  (
				("?somehuman is now panicking.")
			)
		)
		(:action _resolve_emo_stressed
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(is_stressed ?somehuman)
								)

			:humanreadable  (
				("?somehuman is now stressed.")
			)
		)
		(:action _resolve_emo_berserk
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(not (is_berserk ?somehuman))
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(when
										(and
											(is_afraid ?somehuman)
										)
									then
										(and
											(is_berserk ?somehuman)
										)
									)
									(when
										(and
											(is_panicking ?somehuman)
										)
									then
										(and
											(is_berserk ?somehuman)
										)
									)
									(when
										(and
											(is_stressed ?somehuman)
										)
									then
										(and
											(is_berserk ?somehuman)
										)
									)
									(is_afraid ?somehuman)
									(is_panicking ?somehuman)
									(is_stressed ?somehuman)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman is going through a lot of stress and may go berserk.")
			)
		)
		(:action recover_from_berserk
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(is_berserk ?somehuman)
								)

			:effect
								(and
									(not (is_berserk ?somehuman))
									(__emotion_state_marker ?somehuman)
								)

			:humanreadable  (
				("?somehuman recovers from being in berserk state.")
			)
		)
		(:action _resolve_emo_not_afraid
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_afraid ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_afraid ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer afraid.")
			)
		)
		(:action _resolve_emo_not_stressed
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_stressed ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_stressed ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer stressed.")
			)
		)
		(:action _resolve_emo_not_panic
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_panicking ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_panicking ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer panicking.")
			)
		)
		(:action _resolve_emo_not_berserk
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_berserk ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_berserk ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer in berserk state.")
			)
		)
		(:action failed_secure_area
			:parameters     ((?somemarine - marine) (?somealien - alien) (?somelocation - location))
			:precondition
								(and
									(at ?somemarine ?somelocation)
									(at ?somealien ?somelocation)
									(alive ?somemarine)
									(alive ?somealien)
								)

			:effect
								(and
									(alive ?somemarine)
									(forall
										(!someobj - object)
											(when
												(and
													(has_object ?somemarine !someobj)
												)
											then
												(and
													(not (has_object ?somemarine !someobj))
													(at !someobj ?someloc)
												)
											)
									)
								)

			:agents         ((?somemarine))
			:humanreadable  (
				("?somemarine attempted to secure ?somelocation, but ?somealien prevented this, killing ?somemarine in the process.")
			)
		)
		(:action clean_forced_entry
			:parameters     ((?somemarine - marine) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(alive ?somemarine)
									(has_primary_ammo ?somemarine)
									(has_secondary_ammo ?somemarine)
									(at ?somemarine ?fromloc)
									(not (at ?somemarine ?toloc))
									(not (equals ?fromloc ?toloc))
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?somemarine ?fromloc))
									(at ?somemarine ?toloc)
									(__emotion_state_marker ?somemarine)
									(__primary_weapon_state_marker ?somemarine)
									(__secondary_weapon_state_marker ?somemarine)
									(location_marked_secure ?toloc)
									(forall
										(!somealien - alien)
											(when
												(and
													(at !somealien ?toloc)
													(alive !somealien)
												)
											then
												(and
													(not (alive !somealien))
												)
											)
									)
								)

			:agents         ((?somemarine))
			:humanreadable  (
				("?somemarine performed a clean forced entry maneuver from ?fromloc to ?toloc, killing all aliens in ?toloc and securing the area.")
			)
		)
		(:action alien_ambush_location
			:parameters     ((?somealien - alien) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?somealien ?fromloc)
									(not (at ?somealien ?toloc))
									(alive ?somealien)
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(forall
										(!somemarine - marine)
											(when
												(and
													(at !somemarine ?toloc)
													(alive !somemarine)
												)
											then
												(and
													(not (alive !somemarine))
												)
											)
									)
									(not (at ?somealien ?fromloc))
									(at ?somealien ?toloc)
								)

			:agents         ((?somealien))
			:humanreadable  (
				("Moving from ?fromloc, ?somealien ambushed the marines at ?toloc, killing them all.")
			)
		)
		(:action get_bio_object
			:parameters     ((?somehuman - human) (?someobj - biological_object) (?somelocation - location))
			:precondition
								(and
									(at ?somehuman ?somelocation)
									(at ?someobj ?somelocation)
									(alive ?somehuman)
								)

			:effect
								(and
									(not (at ?someobj ?somelocation))
									(has_object ?somehuman ?someobj)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman obtained ?someobj at ?somelocation.")
			)
		)
		(:action get_tech_object
			:parameters     ((?somehuman - human) (?someobj - technological_object) (?somelocation - location))
			:precondition
								(and
									(at ?somehuman ?somelocation)
									(alive ?somehuman)
									(at ?someobj ?somelocation)
								)

			:effect
								(and
									(not (at ?someobj ?somelocation))
									(has_object ?somehuman ?someobj)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman obtained ?someobj at ?somelocation.")
			)
		)
		(:action designate_extraction_point
			:parameters     ((?somemarine - marine) (?somelocation - location))
			:precondition
								(and
									(at ?somemarine ?somelocation)
									(alive ?somemarine)
									(not (extraction_point_set ?somelocation))
								)

			:effect
								(and
									(forall
										(!otherloc - location)
											(when
												(and
													(extraction_point_set !otherloc)
												)
											then
												(and
													(not (extraction_point_set !otherloc))
												)
											)
									)
									(extraction_point_set ?somelocation)
								)

			:agents         ((?somemarine))
			:humanreadable  (
				("?somemarine called for extraction at ?somelocation. Previous extraction points have been rescinded")
			)
		)
		(:action execute_extraction
			:parameters     ((?somelocation - location))
			:precondition
								(and
									(extraction_point_set ?somelocation)
								)

			:effect
								(and
									(forall
										(!somehuman - human)
											(when
												(and
													(at !somehuman ?somelocation)
												)
											then
												(and
													(human_extracted !somehuman)
												)
											)
									)
									(forall
										(!somehuman - human)
											(when
												(and
													(not (at !somehuman ?somelocation))
												)
											then
												(and
													(human_abandoned !somehuman)
												)
											)
									)
								)

			:humanreadable  (
				("Extraction procedures have been initiated at ?somelocation. All other humans in the field have been abandoned.")
			)
		)
		(:action _resolve_emo_excited
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(not (is_excited ?somehuman))
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(is_excited ?somehuman)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman becomes excited.")
			)
		)
		(:action _resolve_emo_focused
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(not (is_focused ?somehuman))
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(is_focused ?somehuman)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman became focused.")
			)
		)
		(:action _resolve_emo_not_excited
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_excited ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_excited ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer excited.")
			)
		)
		(:action _resolve_emo_not_focused
			:parameters     ((?somehuman - human))
			:precondition
								(and
									(__emotion_state_marker ?somehuman)
									(is_focused ?somehuman)
								)

			:effect
								(and
									(not (__emotion_state_marker ?somehuman))
									(not (is_focused ?somehuman))
								)

			:humanreadable  (
				("?somehuman is no longer focused.")
			)
		)
		(:action lure_alien
			:parameters     ((?somehuman - human) (?somealien - alien) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?somehuman ?fromloc)
									(at ?somealien ?toloc)
									(alive ?somehuman)
									(alive ?somealien)
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?somehuman ?fromloc))
									(not (at ?somealien ?fromloc))
									(at ?somehuman ?toloc)
									(at ?somealien ?toloc)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman lured ?somealien from ?fromloc to ?toloc.")
			)
		)
		(:action bring_human
			:parameters     ((?somehuman - human) (?anotherhuman - human) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?somehuman ?fromloc)
									(alive ?somehuman)
									(at ?anotherhuman ?fromloc)
									(alive ?anotherhuman)
									(not (equals ?somehuman ?anotherhuman))
									(adjacent ?fromloc ?toloc)
								)

			:effect
								(and
									(not (at ?somehuman ?fromloc))
									(at ?somehuman ?toloc)
									(not (at ?anotherhuman ?fromloc))
									(at ?anotherhuman ?toloc)
								)

			:agents         ((?somehuman))
			:humanreadable  (
				("?somehuman led ?anotherhuman from ?fromloc to ?toloc.")
			)
		)
		(:action rush_to_location
			:parameters     ((?someactor - actor) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?someactor ?fromloc)
									(not (at ?someactor ?toloc))
									(not (equals ?fromloc ?toloc))
									(alive ?someactor)
								)

			:effect
								(and
									(not (at ?someactor ?fromloc))
									(at ?someactor ?toloc)
								)

			:agents         ((?someactor))
			:humanreadable  (
				("?someactor rushes to ?toloc from ?fromloc.")
			)
		)
		(:action receive_mission_get_object
			:parameters     ((?somemarine - marine) (?someobject - object))
			:precondition
								(and
									(alive ?somemarine)
								)

			:effect
								(and
									(intends ?somemarine (has_object ?somemarine ?someobject) )
									(__emotion_state_marker ?somemarine)
								)

			:humanreadable  (
				("?somemarine received a mission to obtain ?someobject.")
			)
		)
		(:action receive_mission_extraction
			:parameters     ((?somemarine - marine))
			:precondition
								(and
									(not (human_extracted ?somemarine))
									(alive ?somemarine)
								)

			:effect
								(and
									(intends ?somemarine (human_extracted ?somemarine) )
									(__emotion_state_marker ?somemarine)
								)

			:humanreadable  (
				("?somemarine received orders to get extracted.")
			)
		)
		(:action cancel_mission_get_object
			:parameters     ((?somemarine - marine) (?someobject - object))
			:precondition
								(and
									(alive ?somemarine)
								)

			:effect
								(and
									(__emotion_state_marker ?somemarine)
									(not (intends ?somemarine (has_object ?somemarine ?someobject) )
)
								)

			:humanreadable  (
				("?somemarine was order to cancel the mission to obtain ?someobject.")
			)
		)
		(:action cancel_mission_extraction
			:parameters     ((?somemarine - marine))
			:precondition
								(and
									(not (human_extracted ?somemarine))
									(alive ?somemarine)
								)

			:effect
								(and
									(__emotion_state_marker ?somemarine)
									(not (intends ?somemarine (human_extracted ?somemarine) )
)
								)

			:humanreadable  (
				("?somemarine received orders to stay behind.")
			)
		)
		(:action alien_steals_tech
			:parameters     ((?somealien - alien) (?somemarine - marine) (?sometech - alien_tech) (?someloc - location))
			:precondition
								(and
									(alive ?somealien)
									(alive ?somemarine)
									(has_object ?somemarine ?sometech)
									(at ?somealien ?someloc)
									(at ?somemarine ?someloc)
								)

			:effect
								(and
									(not (has_object ?somemarine ?sometech))
									(__emotion_state_marker ?somemarine)
									(has_object ?somealien ?sometech)
								)

			:agents         ((?somealien))
			:humanreadable  (
				("?somealien steals ?sometech from ?somemarine at ?someloc.")
			)
		)
		(:action marine_drops_object
			:parameters     ((?somemarine - marine) (?someobj - object) (?someloc - location))
			:precondition
								(and
									(has_object ?somemarine ?someobj)
									(at ?somemarine ?someloc)
								)

			:effect
								(and
									(at ?someobj ?someloc)
									(not (has_object ?somemarine ?someobj))
								)

			:humanreadable  (
				("?somemarine drops ?someobj at ?someloc.")
			)
		)
		(:action alien_disintegrates_human
			:parameters     ((?somealien - alien) (?somehuman - human) (?someloc - location))
			:precondition
								(and
									(alive ?somealien)
									(alive ?somealien)
									(at ?somealien ?someloc)
									(at ?somehuman ?someloc)
								)

			:effect
								(and
									(not (alive ?somehuman))
									(forall
										(!someobj - object)
											(when
												(and
													(has_object ?somehuman !someobj)
												)
											then
												(and
													(at !someobj ?someloc)
													(not (has_object ?somehuman !someobj))
												)
											)
									)
								)

			:agents         ((?somealien))
			:humanreadable  (
				("?somealien disintegrates ?somehuman at ?someloc.")
			)
		)
)
