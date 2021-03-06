from unityagents import UnityEnvironment
import torch
from collections import deque
import numpy as np

import matplotlib.pyplot as plt

import random



from dqn_agent import Agent


def dqn(env, agent, n_episodes=10000, max_t=1000, eps_start=1.0, eps_end=0.01, eps_decay=0.999, train_mode=True,
        score_list_len=100, checkpoint_path="checkpoints/checkpoint.pth", score_required=13.0):
    """Deep Q-Learning.

    Params
    ======
        n_episodes (int): maximum number of training episodes
        max_t (int): maximum number of timesteps per episode
        eps_start (float): starting value of epsilon, for epsilon-greedy action selection
        eps_end (float): minimum value of epsilon
        eps_decay (float): multiplicative factor (per episode) for decreasing epsilon
    """
    scores = []                        # list containing scores from each episode
    scores_window = deque(maxlen=score_list_len)  # last 100 scores
    eps = eps_start                    # initialize epsilon

    brain_name = env.brain_names[0]
    for i_episode in range(1, n_episodes+1):
        env_info = env.reset(train_mode=train_mode)[brain_name] # reset the environment
        state = env_info.vector_observations[0]            # get the current state
        score = 0
        for t in range(max_t):
            if not train_mode:
                eps= 0.0
            action = agent.act(state, eps)
            env_info = env.step(action)[brain_name]        # send the action to the environment
            next_state = env_info.vector_observations[0]   # get the next state
            reward = env_info.rewards[0]                   # get the reward
            done = env_info.local_done[0]                  # see if episode has finished

            if train_mode:
                agent.step(state, action, reward, next_state, done)
            state = next_state
            score += reward
            if done:
                break

        scores_window.append(score)       # save most recent score
        scores.append(score)              # save most recent score
        if train_mode:
            eps = max(eps_end, eps_decay*eps) # decrease epsilon
        print('\rEpisode {}\tAverage Score: {:.2f} eps {:.2f}'.format(i_episode, np.mean(scores_window), eps), end="")
        if i_episode % score_list_len == 0:
            print('\rEpisode {}\tAverage Score: {:.2f}'.format(i_episode, np.mean(scores_window)))
        if np.mean(scores_window)>=score_required and train_mode:
            print('\nEnvironment solved in {:d} episodes!\tAverage Score: {:.2f}'.format(i_episode-score_list_len, np.mean(scores_window)))
            torch.save(agent.qnetwork_local.state_dict(), checkpoint_path)
            break

    return scores



if __name__ == '__main__':

    #env = UnityEnvironment(file_name="Banana_Linux_NoVis/Banana.x86")
    env = UnityEnvironment(file_name="Banana_Linux/Banana.x86")

    # get the default brain
    brain_name = env.brain_names[0]
    brain = env.brains[brain_name]

    # reset the environment
    env_info = env.reset(train_mode=True)[brain_name]

    # number of agents in the environment
    print('Number of agents:', len(env_info.agents))

    # number of actions
    action_size = brain.vector_action_space_size
    print('Number of actions:', action_size)

    # examine the state space
    state = env_info.vector_observations[0]
    print('States look like:', state)
    state_size = len(state)
    print('States have length:', state_size)

    # env_info = env.reset(train_mode=False)[brain_name] # reset the environment
    # state = env_info.vector_observations[0]            # get the current state
    # score = 0                                          # initialize the score
    # while True:
    #     action = np.random.randint(action_size)        # select an action
    #     env_info = env.step(action)[brain_name]        # send the action to the environment
    #     next_state = env_info.vector_observations[0]   # get the next state
    #     reward = env_info.rewards[0]                   # get the reward
    #     done = env_info.local_done[0]                  # see if episode has finished
    #     score += reward                                # update the score
    #     state = next_state                             # roll over the state to next time step
    #     if done:                                       # exit loop if episode finished
    #         break
    # print("Score: {}".format(score))

    agent = Agent(state_size=state_size, action_size=action_size, seed=0)
    scores = dqn(env, agent)
    scores_eval = dqn(env, agent,train_mode=False, n_episodes=100, score_list_len=100)

    #
    # agent_eval = Agent(state_size=state_size, action_size=action_size, seed=0)
    # agent_eval.qnetwork_local.load_state_dict(torch.load('checkpoints/checkpoint.pth'))
    # scores_eval_checkpoint = dqn(env, agent_eval,train_mode=False, n_episodes=100)

    env.close()

    # plot the scores
    # fig = plt.figure()
    # ax = fig.add_subplot(111)
    # plt.plot(np.arange(len(scores)), scores)
    # plt.ylabel('Score')
    # plt.xlabel('Episode #')
    # plt.show()