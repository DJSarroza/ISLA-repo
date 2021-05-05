(define (domain sciencefiction03)
	(:types 
		object
		predicate
		(actor object)
		(admin actor)
		location
		(mech_gear object)
		(ammo object)
		(mech_suit object)
		(alien organic)
		(farmer organic)
		(gear_repair mech_gear)
		(gear_weapon mech_gear)
		(structure_defensive structure)
		(alien_individual alien)
		(alien_swarm alien)
		(livestock organic)
		(structure object)
		(sentient actor)
		(organic sentient)
		(mechanical sentient)
		(ai_core mechanical)
		(weapon_gun gear_weapon)
		(weapon_missile gear_weapon)
		(weapon_energy gear_weapon)
		(gun_ammo ammo)
		(full_cache_ammo ammo)
		(missile_ammo ammo)
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

		(:predicate adjacent
			:parameters     ((?fromplace - location) (?toplace - location))
			:definition     (adjacent (?fromplace - location) (?toplace - location))
			:primary_obj    ()
			:humanreadable  (
				("from ?fromplace, one can reach ?toplace.")
			)
		)

		(:predicate attached_to_mech
			:parameters     ((?attachment - mech_gear) (?base - mech_suit))
			:definition     (attached_to_mech (?attachment - mech_gear) (?base - mech_suit))
			:primary_obj    ((?attachment - mech_gear))
			:humanreadable  (
				("?attachment is attached to ?base.")
			)
		)

		(:predicate gear_damaged_light
			:parameters     ((?gear - mech_gear))
			:definition     (gear_damaged_light (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is lightly damaged.")
			)
		)

		(:predicate gear_damaged_medium
			:parameters     ((?gear - mech_gear))
			:definition     (gear_damaged_medium (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is significantly damaged.")
			)
		)

		(:predicate gear_damaged_heavy
			:parameters     ((?gear - mech_gear))
			:definition     (gear_damaged_heavy (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is heavily damaged.")
			)
		)

		(:predicate gear_destroyed
			:parameters     ((?gear - mech_gear))
			:definition     (gear_destroyed (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is destroyed.")
			)
		)

		(:predicate alive
			:parameters     ((?some_actor - actor))
			:definition     (alive (?some_actor - actor))
			:primary_obj    ((?some_actor - actor))
			:humanreadable  (
				("?some_actor is alive.")
			)
		)

		(:predicate pilot
			:parameters     ((?creature - sentient))
			:definition     (pilot (?creature - sentient))
			:primary_obj    ((?creature - sentient))
			:humanreadable  (
				("?creature is a pilot.")
			)
		)

		(:predicate mech_disarmed
			:parameters     ((?mech - mech_suit))
			:definition     (mech_disarmed (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech is disarmed.")
			)
		)

		(:predicate mech_immobilized
			:parameters     ((?mech - mech_suit))
			:definition     (mech_immobilized (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech is immobilized.")
			)
		)

		(:predicate mech_destroyed
			:parameters     ((?mech - mech_suit))
			:definition     (mech_destroyed (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech is destroyed.")
			)
		)

		(:predicate mech_damaged_20
			:parameters     ((?mech - mech_suit))
			:definition     (mech_damaged_20 (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech sustained 20 percent damage.")
			)
		)

		(:predicate mech_damaged_40
			:parameters     ((?mech - mech_suit))
			:definition     (mech_damaged_40 (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech sustained 40 percent damage.")
			)
		)

		(:predicate mech_damaged_60
			:parameters     ((?mech - mech_suit))
			:definition     (mech_damaged_60 (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech sustained 60 percent damage.")
			)
		)

		(:predicate mech_damaged_80
			:parameters     ((?mech - mech_suit))
			:definition     (mech_damaged_80 (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech sustained 80 percent damage.")
			)
		)

		(:predicate mech_damaged_95
			:parameters     ((?mech - mech_suit))
			:definition     (mech_damaged_95 (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech sustained 95 percent damage.")
			)
		)

		(:predicate at
			:parameters     ((?something - object) (?someloc - location))
			:definition     (at (?something - object) (?someloc - location))
			:primary_obj    ((?something - object))
			:humanreadable  (
				("?something is at ?someloc.")
				("?something is located at ?someloc.")
			)
		)

		(:predicate creature_immobilized
			:parameters     ((?somecreature - sentient))
			:definition     (creature_immobilized (?somecreature - sentient))
			:primary_obj    ((?somecreature - sentient))
			:humanreadable  (
				("?somecreature is immobilized.")
				("?somecreature is unable to move.")
			)
		)

		(:predicate alien_biter
			:parameters     ((?alien - alien))
			:definition     (alien_biter (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien is a biter.")
			)
		)

		(:predicate alien_charger
			:parameters     ((?alien - alien))
			:definition     (alien_charger (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien trample hostiles it encounter.")
				("?alien is a charger.")
			)
		)

		(:predicate alien_shredder
			:parameters     ((?alien - alien))
			:definition     (alien_shredder (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien shreds enemies it encounter.")
				("?alien is a shredder.")
			)
		)

		(:predicate alien_spitter
			:parameters     ((?alien - alien))
			:definition     (alien_spitter (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien spits corrosive substance.")
				("?alien is a spitter.")
			)
		)

		(:predicate gear_undamaged
			:parameters     ((?gear - mech_gear))
			:definition     (gear_undamaged (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is undamaged.")
			)
		)

		(:predicate mech_undamaged
			:parameters     ((?mech - mech_suit))
			:definition     (mech_undamaged (?mech - mech_suit))
			:primary_obj    ((?mech - mech_suit))
			:humanreadable  (
				("?mech is undamaged.")
				("?mech is at full health.")
			)
		)

		(:predicate gear_disabled
			:parameters     ((?gear - mech_gear))
			:definition     (gear_disabled (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is disabled.")
				("?gear suffered a malfunction.")
			)
		)

		(:predicate pilot_mounted_mech
			:parameters     ((?pilot - sentient) (?mech - mech_suit))
			:definition     (pilot_mounted_mech (?pilot - sentient) (?mech - mech_suit))
			:primary_obj    ((?pilot - sentient))
			:humanreadable  (
				("?pilot is piloting ?mech.")
			)
		)

		(:predicate gear_unattached
			:parameters     ((?gear - mech_gear))
			:definition     (gear_unattached (?gear - mech_gear))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is not attached to anything.")
			)
		)

		(:predicate alien_undamaged
			:parameters     ((?alien - alien))
			:definition     (alien_undamaged (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien is undamaged.")
			)
		)

		(:predicate alien_damaged_20
			:parameters     ((?alien - alien))
			:definition     (alien_damaged_20 (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien sustained 20 percent damage.")
			)
		)

		(:predicate alien_damaged_40
			:parameters     ((?alien - alien))
			:definition     (alien_damaged_40 (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien sustained 40 percent damage.")
			)
		)

		(:predicate alien_damaged_60
			:parameters     ((?alien - alien))
			:definition     (alien_damaged_60 (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien sustained 60 percent damage.")
			)
		)

		(:predicate alien_damaged_80
			:parameters     ((?alien - alien))
			:definition     (alien_damaged_80 (?alien - alien))
			:primary_obj    ((?alien - alien))
			:humanreadable  (
				("?alien sustained 80 percent damage.")
			)
		)

		(:predicate swarm_size_01
			:parameters     ((?alien - alien_swarm))
			:definition     (swarm_size_01 (?alien - alien_swarm))
			:primary_obj    ((?alien - alien_swarm))
			:humanreadable  (
				("?alien swarm is size level 01")
			)
		)

		(:predicate swarm_size_02
			:parameters     ((?alien - alien_swarm))
			:definition     (swarm_size_02 (?alien - alien_swarm))
			:primary_obj    ((?alien - alien_swarm))
			:humanreadable  (
				("?alien swarm is size level 02")
			)
		)

		(:predicate swarm_size_03
			:parameters     ((?alien - alien_swarm))
			:definition     (swarm_size_03 (?alien - alien_swarm))
			:primary_obj    ((?alien - alien_swarm))
			:humanreadable  (
				("?alien swarm is size level 03")
			)
		)

		(:predicate ammo_level_00
			:parameters     ((?weapon - gear_weapon))
			:definition     (ammo_level_00 (?weapon - gear_weapon))
			:primary_obj    ((?weapon - gear_weapon))
			:humanreadable  (
				("?weapon has ammo level 00.")
			)
		)

		(:predicate ammo_level_01
			:parameters     ((?weapon - gear_weapon))
			:definition     (ammo_level_01 (?weapon - gear_weapon))
			:primary_obj    ((?weapon - gear_weapon))
			:humanreadable  (
				("?weapon has ammo level 01.")
			)
		)

		(:predicate ammo_level_02
			:parameters     ((?weapon - gear_weapon))
			:definition     (ammo_level_02 (?weapon - gear_weapon))
			:primary_obj    ((?weapon - gear_weapon))
			:humanreadable  (
				("?weapon has ammo level 00.")
			)
		)

		(:predicate ammo_level_03
			:parameters     ((?weapon - gear_weapon))
			:definition     (ammo_level_03 (?weapon - gear_weapon))
			:primary_obj    ((?weapon - gear_weapon))
			:humanreadable  (
				("?weapon has ammo level 03.")
			)
		)

		(:predicate is_exposed
			:parameters     ((?sentient - sentient))
			:definition     (is_exposed (?sentient - sentient))
			:primary_obj    ((?sentient - sentient))
			:humanreadable  (
				("?sentient is exposed. They are vulnerable to attack!")
			)
		)

		(:predicate pilot_has_mech
			:parameters     ((?pilot - sentient))
			:definition     (pilot_has_mech (?pilot - sentient))
			:primary_obj    ((?pilot - sentient))
			:humanreadable  (
				("?pilot is in a mech suit.")
			)
		)

		(:predicate attached_to_structure
			:parameters     ((?gear - mech_gear) (?base - structure))
			:definition     (attached_to_structure (?gear - mech_gear) (?base - structure))
			:primary_obj    ((?gear - mech_gear))
			:humanreadable  (
				("?gear is mounted at ?base.")
				("?gear is attached to ?base.")
			)
		)

	)

		(:action alien_bite_gear
			:parameters     ((?alien - alien) (?gear - mech_gear) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(alien_biter ?alien)
									(alive ?alien)
									(at ?gear ?someloc)
									(not (gear_destroyed ?gear))
								)

			:effect
								(and
									(when
										(and
											(gear_damaged_heavy ?gear)
										)
									then
										(and
											(gear_destroyed ?gear)
											(not (gear_damaged_heavy ?gear))
										)
									)
									(when
										(and
											(gear_damaged_medium ?gear)
										)
									then
										(and
											(gear_damaged_heavy ?gear)
											(not (gear_damaged_medium ?gear))
										)
									)
									(when
										(and
											(gear_damaged_light ?gear)
										)
									then
										(and
											(gear_damaged_medium ?gear)
											(not (gear_damaged_light ?gear))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien bites ?gear at ?someloc.")
				("?alien gnaws at ?gear at ?someloc.")
			)
		)
		(:action alien_charges_gear
			:parameters     ((?alien - alien) (?gear - mech_gear) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?gear ?someloc)
									(alien_charger ?alien)
									(alive ?alien)
									(not (gear_destroyed ?gear))
								)

			:effect
								(and
									(when
										(and
											(gear_damaged_heavy ?gear)
										)
									then
										(and
											(gear_destroyed ?gear)
											(not (gear_damaged_heavy ?gear))
										)
									)
									(when
										(and
											(gear_damaged_medium ?gear)
										)
									then
										(and
											(gear_destroyed ?gear)
											(not (gear_damaged_medium ?gear))
										)
									)
									(when
										(and
											(gear_damaged_light ?gear)
										)
									then
										(and
											(gear_damaged_heavy ?gear)
											(not (gear_damaged_light ?gear))
										)
									)
									(when
										(and
											(gear_undamaged ?gear)
										)
									then
										(and
											(gear_damaged_heavy ?gear)
											(not (gear_undamaged ?gear))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien charges ?gear and damages it greatly, happened at ?someloc.")
			)
		)
		(:action alien_spits_gear
			:parameters     ((?alien - alien) (?gear - mech_gear) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?gear ?someloc)
									(alien_spitter ?alien)
									(not (gear_destroyed ?gear))
									(alive ?alien)
								)

			:effect
								(and
									(when
										(and
											(gear_damaged_heavy ?gear)
										)
									then
										(and
											(gear_disabled ?gear)
										)
									)
									(when
										(and
											(gear_damaged_medium ?gear)
										)
									then
										(and
											(gear_damaged_heavy ?gear)
											(not (gear_damaged_medium ?gear))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien sprays corrosive substance at ?gear, happened at ?someloc.")
				("?alien spits gunk at ?gear at ?someloc.")
			)
		)
		(:action alien_bites_mech
			:parameters     ((?alien - alien) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?mech ?someloc)
									(alive ?alien)
									(alien_biter ?alien)
									(not (mech_destroyed ?mech))
								)

			:effect
								(and
									(when
										(and
											(mech_damaged_95 ?mech)
										)
									then
										(and
											(mech_destroyed ?mech)
											(not (mech_damaged_95 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_80 ?mech)
										)
									then
										(and
											(mech_damaged_95 ?mech)
											(not (mech_damaged_80 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_60 ?mech)
										)
									then
										(and
											(mech_damaged_80 ?mech)
											(not (mech_damaged_60 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_40 ?mech)
										)
									then
										(and
											(mech_damaged_60 ?mech)
											(not (mech_damaged_40 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_20 ?mech)
										)
									then
										(and
											(mech_damaged_40 ?mech)
											(not (mech_damaged_20 ?mech))
										)
									)
									(when
										(and
											(mech_undamaged ?mech)
										)
									then
										(and
											(mech_damaged_20 ?mech)
											(not (mech_undamaged ?mech))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?mech suffers bite damage from ?alien at ?someloc.")
			)
		)
		(:action alien_spits_mech
			:parameters     ((?alien - alien) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?mech ?someloc)
									(alien_spitter ?alien)
									(alive ?alien)
									(not (mech_destroyed ?mech))
								)

			:effect
								(and
									(when
										(and
											(mech_damaged_95 ?mech)
										)
									then
										(and
											(mech_immobilized ?mech)
										)
									)
									(when
										(and
											(mech_damaged_80 ?mech)
										)
									then
										(and
											(mech_damaged_95 ?mech)
											(not (mech_damaged_80 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_60 ?mech)
										)
									then
										(and
											(mech_damaged_80 ?mech)
											(not (mech_damaged_60 ?mech))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?mech suffers corrosive chemical damage from ?alien at ?someloc.")
			)
		)
		(:action alien_spits_mech_disarms
			:parameters     ((?alien - alien) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?mech ?someloc)
									(alien_spitter ?alien)
									(not (mech_destroyed ?mech))
									(alive ?alien)
								)

			:effect
								(and
									(when
										(and
											(mech_damaged_80 ?mech)
										)
									then
										(and
											(mech_disarmed ?mech)
										)
									)
									(when
										(and
											(mech_damaged_95 ?mech)
										)
									then
										(and
											(mech_disarmed ?mech)
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien sprays corrosive chemicals at ?mech and hits it's weapon systems, happened at ?someloc.")
			)
		)
		(:action alien_charges_mech
			:parameters     ((?alien - alien) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?mech ?someloc)
									(alien_charger ?alien)
									(alive ?alien)
									(not (mech_destroyed ?mech))
								)

			:effect
								(and
									(when
										(and
											(mech_damaged_95 ?mech)
										)
									then
										(and
											(mech_destroyed ?mech)
											(not (mech_damaged_95 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_80 ?mech)
										)
									then
										(and
											(mech_damaged_95 ?mech)
											(not (mech_damaged_80 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_60 ?mech)
										)
									then
										(and
											(mech_damaged_80 ?mech)
											(not (mech_damaged_60 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_40 ?mech)
										)
									then
										(and
											(mech_damaged_60 ?mech)
											(not (mech_damaged_40 ?mech))
										)
									)
									(when
										(and
											(mech_damaged_20 ?mech)
										)
									then
										(and
											(mech_damaged_40 ?mech)
											(not (mech_damaged_20 ?mech))
										)
									)
									(when
										(and
											(mech_undamaged ?mech)
										)
									then
										(and
											(mech_damaged_20 ?mech)
											(not (mech_undamaged ?mech))
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?mech suffers blunt damage from ?alien's charge at ?someloc.")
			)
		)
		(:action alien_charges_mech_immobilize
			:parameters     ((?alien - alien) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?mech ?someloc)
									(alien_charger ?alien)
									(not (mech_destroyed ?mech))
									(alive ?alien)
								)

			:effect
								(and
									(when
										(and
											(mech_damaged_95 ?mech)
										)
									then
										(and
											(mech_immobilized ?mech)
										)
									)
									(when
										(and
											(mech_damaged_80 ?mech)
										)
									then
										(and
											(mech_immobilized ?mech)
										)
									)
									(when
										(and
											(mech_damaged_60 ?mech)
										)
									then
										(and
											(mech_immobilized ?mech)
										)
									)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien charges at ?mech, damaging it's mobility systems, happened at ?someloc.")
			)
		)
		(:action pilot_mounts_mech
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?mech ?someloc)
									(at ?pilot ?someloc)
									(alive ?pilot)
									(not (mech_destroyed ?mech))
								)

			:effect
								(and
									(pilot_mounted_mech ?pilot ?mech)
									(not (is_exposed ?pilot))
									(pilot_has_mech ?pilot)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot mounts ?mech at ?someloc.")
			)
		)
		(:action mech_equips_gear
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?gear - mech_gear) (?someloc - location))
			:precondition
								(and
									(at ?pilot ?someloc)
									(at ?mech ?someloc)
									(at ?gear ?someloc)
									(alive ?pilot)
									(not (attached_to_mech ?gear ?mech))
								)

			:effect
								(and
									(attached_to_mech ?gear ?mech)
									(not (gear_unattached ?gear))
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot equips ?gear to ?mech at ?someloc.")
			)
		)
		(:action mech_move
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(at ?pilot ?fromloc)
									(not (at ?pilot ?toloc))
									(pilot_mounted_mech ?pilot ?mech)
									(not (mech_destroyed ?mech))
									(not (mech_immobilized ?mech))
									(alive ?pilot)
									(adjacent ?fromloc ?toloc)
									(not (equals ?fromloc ?toloc))
								)

			:effect
								(and
									(not (at ?pilot ?fromloc))
									(at ?pilot ?toloc)
									(not (at ?mech ?fromloc))
									(at ?mech ?toloc)
									(forall
										(!gear - mech_gear)
											(when
												(and
													(attached_to_mech !gear ?mech)
												)
											then
												(and
													(not (at !gear ?fromloc))
													(at !gear ?toloc)
												)
											)
									)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot moves ?mech from ?fromloc to ?toloc.")
				("?pilot relocates ?mech ?fromloc to ?toloc.")
			)
		)
		(:action gun_reload
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?weapon - weapon_gun) (?ammo - gun_ammo) (?someloc - location))
			:precondition
								(and
									(alive ?pilot)
									(at ?pilot ?someloc)
									(at ?ammo ?someloc)
									(not (gear_destroyed ?weapon))
									(not (mech_destroyed ?mech))
									(not (mech_immobilized ?mech))
									(not (ammo_level_03 ?weapon))
									(not (attached_to_mech ?weapon ?mech))
								)

			:effect
								(and
									(when
										(and
											(ammo_level_00 ?weapon)
										)
									then
										(and
											(not (ammo_level_00 ?weapon))
											(ammo_level_03 ?weapon)
										)
									)
									(when
										(and
											(ammo_level_01 ?weapon)
										)
									then
										(and
											(not (ammo_level_00 ?weapon))
											(ammo_level_03 ?weapon)
										)
									)
									(when
										(and
											(ammo_level_02 ?weapon)
										)
									then
										(and
											(not (ammo_level_00 ?weapon))
											(ammo_level_03 ?weapon)
										)
									)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot reloads ?mech's ?weapon using ?ammo at ?someloc. Lock and load!")
				("?pilot reloads ?mech's ?weapon using ?ammo at ?someloc. Weapon ammo at full capacity.")
			)
		)
		(:action alien_attacks_farmer
			:parameters     ((?alien - alien) (?farmer - farmer) (?someloc - location))
			:precondition
								(and
									(at ?alien ?someloc)
									(at ?farmer ?someloc)
									(is_exposed ?farmer)
								)

			:effect
								(and
									(not (alive ?farmer))
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien attacks ?farmer at ?someloc. ?farmer did not survive.")
				("?farmer gets killed by ?alien at ?someloc.")
			)
		)
		(:action pilot_dismounts_mech
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(alive ?pilot)
									(at ?pilot ?someloc)
									(at ?mech ?someloc)
								)

			:effect
								(and
									(not (pilot_mounted_mech ?pilot ?mech))
									(is_exposed ?pilot)
									(not (pilot_has_mech ?pilot))
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot dismounts ?mech at ?someloc.")
			)
		)
		(:action basic_move
			:parameters     ((?creature - sentient) (?fromloc - location) (?toloc - location))
			:precondition
								(and
									(alive ?creature)
									(at ?creature ?fromloc)
									(not (at ?creature ?toloc))
									(not (pilot_has_mech ?creature))
									(adjacent ?fromloc ?toloc)
									(not (equals ?fromloc ?toloc))
								)

			:effect
								(and
									(not (at ?creature ?fromloc))
									(at ?creature ?toloc)
								)

			:agents         ((?creature))
			:humanreadable  (
				("?creature moves from ?fromloc to ?toloc.")
			)
		)
		(:action pilot_detonates_core
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(at ?pilot ?someloc)
									(at ?mech ?someloc)
									(alive ?pilot)
									(not (mech_destroyed ?mech))
									(pilot_mounted_mech ?pilot ?mech)
								)

			:effect
								(and
									(forall
										(!alien - alien_swarm)
											(when
												(and
													(at !alien ?someloc)
												)
											then
												(and
													(not (alive !alien))
												)
											)
									)
									(not (alive ?pilot))
									(mech_destroyed ?mech)
									(forall
										(!gear - mech_gear)
											(when
												(and
													(attached_to_mech !gear ?mech)
												)
											then
												(and
													(gear_destroyed !gear)
												)
											)
									)
									(forall
										(!alien_boss - alien_individual)
											(when
												(and
													(at !alien_boss ?someloc)
												)
											then
												(and
													(alien_damaged_80 !alien_boss)
													(not (alien_undamaged !alien_boss))
													(not (alien_damaged_20 !alien_boss))
													(not (alien_damaged_40 !alien_boss))
												)
											)
									)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot detonates ?mech core at ?someloc, causing massive damage to all surrounding aliens.")
			)
		)
		(:action drop_ammo
			:parameters     ((?operator - sentient) (?ammo - ammo) (?from_loc - location) (?to_loc - location))
			:precondition
								(and
									(at ?ammo ?from_loc)
									(not (at ?ammo ?to_loc))
								)

			:effect
								(and
									(not (at ?ammo ?from_loc))
									(at ?ammo ?to_loc)
								)

			:agents         ((?operator))
			:humanreadable  (
				("?operator requested transfer of ?ammo from ?from_loc to ?to_loc.")
			)
		)
		(:action mech_gun_attack_alienswarm
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?weapon - gear_weapon) (?alien_swarm - alien_swarm) (?someloc - location))
			:precondition
								(and
									(at ?pilot ?someloc)
									(pilot_mounted_mech ?pilot ?mech)
									(attached_to_mech ?weapon ?mech)
									(not (mech_destroyed ?mech))
									(not (mech_disarmed ?mech))
									(not (gear_destroyed ?weapon))
									(alive ?pilot)
									(alive ?alien_swarm)
									(at ?alien_swarm ?someloc)
									(not (ammo_level_00 ?weapon))
									(not (gear_disabled ?weapon))
								)

			:effect
								(and
									(when
										(and
											(ammo_level_01 ?weapon)
										)
									then
										(and
											(ammo_level_00 ?weapon)
											(not (ammo_level_01 ?weapon))
										)
									)
									(when
										(and
											(ammo_level_02 ?weapon)
										)
									then
										(and
											(ammo_level_01 ?weapon)
											(not (ammo_level_02 ?weapon))
										)
									)
									(when
										(and
											(ammo_level_03 ?weapon)
										)
									then
										(and
											(ammo_level_02 ?weapon)
											(not (ammo_level_03 ?weapon))
										)
									)
									(when
										(and
											(swarm_size_01 ?alien_swarm)
										)
									then
										(and
											(not (alive ?alien_swarm))
											(not (swarm_size_01 ?alien_swarm))
										)
									)
									(when
										(and
											(swarm_size_02 ?alien_swarm)
										)
									then
										(and
											(swarm_size_01 ?alien_swarm)
											(not (swarm_size_02 ?alien_swarm))
										)
									)
									(when
										(and
											(swarm_size_03 ?alien_swarm)
										)
									then
										(and
											(swarm_size_02 ?alien_swarm)
											(not (swarm_size_03 ?alien_swarm))
										)
									)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot attacks ?alien_swarm with ?mech's ?weapon at ?someloc.")
			)
		)
		(:action mech_gun_attack_alien
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?weapon - gear_weapon) (?alien - alien_individual) (?someloc - location))
			:precondition
								(and
									(at ?pilot ?someloc)
									(alive ?pilot)
									(pilot_mounted_mech ?pilot ?mech)
									(not (mech_destroyed ?mech))
									(not (mech_disarmed ?mech))
									(not (gear_destroyed ?weapon))
									(not (gear_disabled ?weapon))
									(not (ammo_level_00 ?weapon))
									(attached_to_mech ?weapon ?mech)
									(alive ?alien)
									(at ?alien ?someloc)
								)

			:effect
								(and
									(when
										(and
											(alien_damaged_80 ?alien)
										)
									then
										(and
											(not (alive ?alien))
											(not (alien_damaged_80 ?alien))
										)
									)
									(when
										(and
											(alien_damaged_60 ?alien)
										)
									then
										(and
											(alien_damaged_80 ?alien)
											(not (alien_damaged_60 ?alien))
										)
									)
									(when
										(and
											(alien_damaged_40 ?alien)
										)
									then
										(and
											(alien_damaged_60 ?alien)
											(not (alien_damaged_40 ?alien))
										)
									)
									(when
										(and
											(alien_damaged_20 ?alien)
										)
									then
										(and
											(alien_damaged_40 ?alien)
											(not (alien_damaged_20 ?alien))
										)
									)
									(when
										(and
											(alien_undamaged ?alien)
										)
									then
										(and
											(alien_damaged_20 ?alien)
											(not (alien_undamaged ?alien))
										)
									)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot attacks ?alien with ?mech's ?weapon at ?someloc.")
			)
		)
		(:action pilot_training
			:parameters     ((?pilot - farmer) (?mech - mech_suit) (?someloc - location))
			:precondition
								(and
									(not (pilot ?pilot))
									(at ?pilot ?someloc)
									(at ?mech ?someloc)
								)

			:effect
								(and
									(pilot ?pilot)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot learns how to operate ?mech at ?someloc.")
			)
		)
		(:action alien_evolves_biter
			:parameters     ((?some_alien - alien) (?some_location - location))
			:precondition
								(and
									(not (alien_biter ?some_alien))
									(at ?some_alien ?some_location)
								)

			:effect
								(and
									(alien_biter ?some_alien)
								)

			:agents         ((?some_alien))
			:humanreadable  (
				("?some_alien evolves and becomes a biter at ?some_location.")
			)
		)
		(:action alien_evolves_charger
			:parameters     ((?some_alien - alien) (?some_location - location))
			:precondition
								(and
									(at ?some_alien ?some_location)
									(not (alien_charger ?some_alien))
								)

			:effect
								(and
									(alien_charger ?some_alien)
								)

			:agents         ((?some_alien))
			:humanreadable  (
				("?some_alien evolves into a charger at ?some_location.")
			)
		)
		(:action alien_evolves_spitter
			:parameters     ((?some_alien - alien) (?some_location - location))
			:precondition
								(and
									(at ?some_alien ?some_location)
									(not (alien_spitter ?some_alien))
								)

			:effect
								(and
									(alien_spitter ?some_alien)
								)

			:agents         ((?some_alien))
			:humanreadable  (
				("?some_alien evolves into a spitter at ?some_location.")
			)
		)
		(:action alien_bites_gear_overwhelm
			:parameters     ((?alien - alien) (?gear - mech_gear) (?loc1 - location))
			:precondition
								(and
									(at ?alien ?loc1)
									(alive ?alien)
									(alien_biter ?alien)
									(not (gear_destroyed ?gear))
									(at ?gear ?loc1)
								)

			:effect
								(and
									(gear_destroyed ?gear)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien bites ?gear and destroys it at ?loc1.")
			)
		)
		(:action alien_bites_mech_overwhelm
			:parameters     ((?alien - alien) (?mech - mech_suit) (?loc1 - location))
			:precondition
								(and
									(at ?alien ?loc1)
									(alive ?alien)
									(alien_biter ?alien)
									(at ?mech ?loc1)
									(not (mech_destroyed ?mech))
								)

			:effect
								(and
									(forall
										(!pilot - sentient)
											(when
												(and
													(pilot_mounted_mech !pilot ?mech)
												)
											then
												(and
													(not (alive !pilot))
												)
											)
									)
									(mech_destroyed ?mech)
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien overwhelms ?mech with bites and destroys it at ?loc1.")
			)
		)
		(:action mech_kills_alien
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?gear - gear_weapon) (?alien - alien) (?loc1 - location))
			:precondition
								(and
									(pilot_mounted_mech ?pilot ?mech)
									(at ?pilot ?loc1)
									(alive ?pilot)
									(not (mech_destroyed ?mech))
									(not (mech_disarmed ?mech))
									(at ?mech ?loc1)
									(alive ?alien)
									(at ?alien ?loc1)
									(attached_to_mech ?gear ?mech)
									(not (ammo_level_00 ?gear))
									(not (gear_destroyed ?gear))
									(not (gear_disabled ?gear))
								)

			:effect
								(and
									(not (alive ?alien))
									(ammo_level_00 ?gear)
									(not (ammo_level_01 ?gear))
									(not (ammo_level_02 ?gear))
									(not (ammo_level_03 ?gear))
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot uses ?mech's ?gear to kill ?alien instantly at ?loc1.")
			)
		)
		(:action mech_salvages_gear
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?gear - mech_gear) (?loc1 - location))
			:precondition
								(and
									(at ?pilot ?loc1)
									(alive ?pilot)
									(pilot_mounted_mech ?pilot ?mech)
									(not (mech_destroyed ?mech))
									(not (gear_destroyed ?gear))
									(not (gear_unattached ?gear))
									(not (attached_to_mech ?gear ?mech))
								)

			:effect
								(and
									(forall
										(!othermech - mech_suit)
											(when
												(and
													(attached_to_mech ?gear !othermech)
												)
											then
												(and
													(not (attached_to_mech ?gear !othermech))
												)
											)
									)
									(attached_to_mech ?gear ?mech)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot salvages ?gear at ?loc1 and attaches it to ?mech.")
			)
		)
		(:action structure_remote_attacks_alien
			:parameters     ((?operator - sentient) (?structure - structure) (?weapon - gear_weapon) (?target - alien) (?loc1 - location))
			:precondition
								(and
									(at ?operator ?loc1)
									(alive ?operator)
									(at ?structure ?loc1)
									(attached_to_structure ?weapon ?structure)
									(alive ?target)
								)

			:effect
								(and
									(not (alive ?target))
								)

			:agents         ((?operator))
			:humanreadable  (
				("located at ?loc1, ?operator kills ?target using ?structure's ?weapon.")
			)
		)
		(:action mech_unequips_gear
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?gear - mech_gear) (?loc1 - location))
			:precondition
								(and
									(alive ?pilot)
									(at ?pilot ?loc1)
									(pilot_mounted_mech ?pilot ?mech)
									(attached_to_mech ?gear ?mech)
								)

			:effect
								(and
									(not (attached_to_mech ?gear ?mech))
									(at ?gear ?loc1)
									(gear_unattached ?gear)
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot disconnects ?gear from ?mech at ?loc1.")
			)
		)
		(:action structure_equips_gear
			:parameters     ((?operator - sentient) (?structure - structure) (?gear - mech_gear) (?loc1 - location))
			:precondition
								(and
									(at ?operator ?loc1)
									(alive ?operator)
									(at ?structure ?loc1)
									(at ?gear ?loc1)
									(not (attached_to_structure ?gear ?structure))
									(gear_unattached ?gear)
								)

			:effect
								(and
									(attached_to_structure ?gear ?structure)
									(not (gear_unattached ?gear))
								)

			:agents         ((?operator))
			:humanreadable  (
				("?operator attached ?gear to ?structure at ?loc1.")
				("?operator equips ?structure located at ?loc1 with ?gear.")
			)
		)
		(:action alien_kill_organic
			:parameters     ((?alien - alien) (?target - organic) (?loc1 - location))
			:precondition
								(and
									(alive ?alien)
									(at ?alien ?loc1)
									(at ?target ?loc1)
									(not (equals ?alien ?target))
									(alive ?target)
								)

			:effect
								(and
									(not (alive ?target))
								)

			:agents         ((?alien))
			:humanreadable  (
				("?alien murders ?target at ?loc1.")
				("?alien kills ?target at ?loc1.")
			)
		)
		(:action mech_kills_alien_generic
			:parameters     ((?pilot - sentient) (?mech - mech_suit) (?alien - alien) (?loc1 - location))
			:precondition
								(and
									(pilot_mounted_mech ?pilot ?mech)
									(not (mech_destroyed ?mech))
									(at ?pilot ?loc1)
									(alive ?pilot)
									(at ?mech ?loc1)
									(alive ?alien)
									(at ?alien ?loc1)
								)

			:effect
								(and
									(not (alive ?alien))
								)

			:agents         ((?pilot))
			:humanreadable  (
				("?pilot uses ?mech to kill ?alien at ?loc1.")
			)
		)
		(:action farmer_kills_alien
			:parameters     ((?defender - farmer) (?alien1 - alien) (?loc1 - location))
			:precondition
								(and
									(at ?defender ?loc1)
									(at ?alien1 ?loc1)
									(alive ?defender)
									(alive ?alien1)
								)

			:effect
								(and
									(not (alive ?alien1))
								)

			:agents         ((?defender))
			:humanreadable  (
				("?defender somehow killed ?alien1 at ?loc1.")
			)
		)
)
