'''
RANDOM AGENT
'''

import random

def agent(state, done, bombs, turn, player):

	name = "random bot"
	actions = [0,1,2,3,4,5]
	action = random.choice(actions)
	return action, name