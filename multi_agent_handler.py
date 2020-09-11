from bm_multi_env import *
import numpy as np
import lookahead_agent
import random_agent
import flee_agent
import random
import os
from time import sleep

# create the bomberman environment
env = Game(5,7)

os.system('cls')
sleep(0.5)

# set play time
num_episodes = 10
max_turns = 200

# set agents in play
# available: lookahead_agent, random_agent, flee_agent
agent1 = flee_agent
agent2 = lookahead_agent

for i in range(num_episodes):
	turn = 0
	# initialize the map & players
	state, players = env.reset()
	# initialize variables
	done = False
	rewards = [0,0] # reward received per turn
	total_rewards = [0,0] # cumulative rewards received
	bomb_timer = env.MAX_TIMER
	bomb_list = [] # a list of bomb objects in play and their properties

	# until game ends
	while not done:

		os.system('cls')

		# get player one's action
		p1_action, p1_bot = agent1.agent(state, done, bomb_list, turn, player=players[0])
		# get player two's action
		p2_action, p2_bot = agent2.agent(state, done, bomb_list, turn, player=players[1])

		# perform action
		actions = [p1_action, p2_action]
		state, done, players, bomb_list = env.step(actions)

		print(f"\n {p1_bot} vs. {p2_bot}")

		# render the game
		env.render(True)

		print(state)
		input() 

		print(f"\n Turn: {turn}")
		print(" --------------------")
		print(f" Player 1 score: {players[0].score}")
		print(" --------------------")
		print(f" Player 2 score: {players[1].score}")
		print(" --------------------")

		if done:
			if players[0].score > players[1].score:
				print(f" Game over. {p1_bot} wins.")
			elif players[0].score < players[1].score:
				print(f" Game over. {p2_bot} wins.")
			else:
				print("Game over. It's a tie.")
			sleep(3)
			break

		turn +=1

		sleep(0.2)