import math
enemyStats = {"basic":{"defense":[1000, 100, 0.1], 
											 "attack" :[1000, 100, 0.1],
											 "knockbackAttack":[1000, 50, 0.1],
											 "knockbackDefense":[1000, 50, 0.1],
											 "health":[1, 0, 0],
											 "listenRad":[50, 0, 0],
											 "alertedListenRad":[150, 0, 0],
											 "sightRad":[200, 0, 0],
											 "alertedSightRad":[350, 0, 0],
											 "sightArc":[math.pi / 4, 0, 0],
											 "alertedSightArc":[math.pi / 3, 0, 0],
											 "preferredRange":[190, 0, 0],
											 "activateRange":[230, 0, 0],
											 "walkSpeed":[2, 0, 0],
											 "runSpeed":[3.5, 0, 0]
											 },
							"civilian":{"health":[1, 0, 0],
													"listenRad":[40, 0, 0],
											 "alertedListenRad":[100, 0, 0],
											 "sightRad":[200, 0, 0],
											 "alertedSightRad":[250, 0, 0],
											 "sightArc":[math.pi / 4, 0, 0],
											 "alertedSightArc":[math.pi / 3, 0, 0],
											 "preferredRange":[190, 0, 0],
											 "activateRange":[230, 0, 0],
											 "walkSpeed":[1, 0, 0],
											 "runSpeed":[2.5, 0, 0]
											 }}
											 
baseStats = {"defense":1000, 
						 "attack" :1000,
						 "knockbackAttack":1000,
						 "knockbackDefense":1000}
						 
baseEnemyStats = {"defense":[1000, 100, 0.1],
								 "attack" :[1000, 100, 0.1],
								 "knockbackAttack":[1000, 100, 0.1],
								 "knockbackDefense":[1000, 100, 0.1],
								 "bounty":[10, 5, 0.1]}