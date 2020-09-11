'''
This agent places a bomb and runs away
'''

def agent(state, done, bombs, turn, player):

	import random

	########################
	###    VARIABLES     ###
	########################

    # store some useful information about our environment
	rows = state.shape[0]
	cols = state.shape[1]

	# a useful dictionary for our actions
	actions = ['none','left','right','up','down','bomb']
	action_id = [0,1,2,3,4,5]
	d_actions = dict(zip(actions,action_id))

	# we need to keep track of different values of the 
	# environment state based on which agent we are
	if player.number == 0:
		player_id = 1
		player_on_bomb_id = 6
	else:
		player_id = 2
		player_on_bomb_id = 7

	########################
	###     HELPERS      ###
	########################

	def get_surrounding_tiles(state, position):
		'''
		return a position's surrounding 4 tiles
		'''

		# find all the surrounding tiles
		tile_up = (position[0]-1,position[1])
		tile_down = (position[0]+1,position[1])
		tile_left = (position[0],position[1]-1)
		tile_right = (position[0],position[1]+1)

		# combine these into a list
		surrounding_tiles = [tile_up, tile_down, tile_left, tile_right]

		# used to store tiles we can't move to
		# (ones that cross the borders of the map, and holes)
		tiles_to_remove = [] 

		# loop through surrounding tiles
		for tile in surrounding_tiles:
			if (tile[0] < 0 or tile[1] < 0 or tile[0] >= rows or tile[1] >= cols or 
				state[tile] == 4):
				# add illegal tiles to our list
				tiles_to_remove.append(tile)

		# loop through the tiles we're going to exclude
		# and remove them from our original list of tiles
		for tile in tiles_to_remove:
			surrounding_tiles.remove(tile)

		return surrounding_tiles

	def get_empty_tiles(list_of_tiles):
		'''
		from a list of tiles, return the ones where we can move to
		'''

		# make a list where we'll store our empty tiles
		empty_tiles = []
		for tile in list_of_tiles:
			if state[tile] == 0:
				# that tile is empty, so add it to the list
				empty_tiles.append(tile)

		return empty_tiles

	def get_safe_tiles(list_of_tiles, bomb_pos):
		'''
		from a list of tiles, return ones which are guaranteed safe to move to
		'''

		# make a list where we'll store our safe tiles 
		safe_tiles = []

		# loop the tiles
		for tile in list_of_tiles:
			diff = tuple(x-y for x, y in zip(tile, bomb_pos))
			if diff in [(0,1),(1,0),(0,-1),(-1,0),(0,0)]:
				# this tile is adjacent to a bomb
				pass
			else:
				# otherwise, the tile should be safe
				safe_tiles.append(tile)

		return safe_tiles

	def move_to_tile(position, tile):
		'''
		given an adjacent tile location, move your agent to that tile
		'''

		# see where the tile is relative to our current location
		diff = tuple(x-y for x, y in zip(position, tile))

		# return the action that moves in the direction of the tile
		if diff == (0,1):
			action = d_actions['left']
		elif diff == (1,0):
			action = d_actions['up']
		elif diff == (0,-1):
			action = d_actions['right']
		elif diff == (-1,0):
			action = d_actions['down']

		return action

	########################
	###      AGENT       ###
	########################

	if player.bombs:
		# this means we've got a bomb on the map
		# so let's run away

		# get the bomb's position
		# note that the bombs are stored in a list owned by the player/agent
		bomb_pos = player.bombs[0].position

		# get a list of our surrounding tiles
		surrounding_tiles = get_surrounding_tiles(state, player.position)

		# get a list of the available tiles we can actually move to
		empty_tiles = get_empty_tiles(surrounding_tiles)

		# get a list of the safe tiles we should move to
		safe_tiles = get_safe_tiles(empty_tiles, bomb_pos)

		# check if we're on a bomb
		if state[player.position] == player_on_bomb_id:
			# we're on a bomb
			# let's move to an empty slot
			if empty_tiles:
				random_tile = random.choice(empty_tiles)
				action = move_to_tile(player.position, random_tile)
				#print(random_tile)
				#print(action)
				#input()
			else:
				# there aren't any empty tiles to go to
				# we're probably done for.
				action = d_actions['none']
		else:
			# we're not on a bomb
			# check if we're next to a bomb
			for tile in surrounding_tiles:
				if (tile[0] == bomb_pos[0]) and (tile[1] == bomb_pos[1]):
					# we're next to a bomb
					# move to a random safe tile (if there are any)
					if safe_tiles:
						random_tile = random.choice(safe_tiles)
						action = move_to_tile(player.position, random_tile)
						break
					else:
						# there isn't a guaranteed safe tile near us
						# choose a move at random
						action = d_actions[random.choice(actions)]
						break
			else:
				# there isn't a bomb nearby
				# we're probably safe so lets stay here
				action = d_actions['none']

	else:
		# no bombs in play, take a random action
		action = d_actions[random.choice(actions)]

	name = "flee bot"
	return action, name


