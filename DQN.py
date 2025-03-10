import math
import random
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from collections import namedtuple, deque
from itertools import count
from tetris import *
from AI import *

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

from dataclasses import dataclass


@dataclass
class HyperParams:
    BATCH_SIZE: int = 512
    GAMMA: float = 0.95
    EPS_START: float = 0.9
    EPS_END: float = 0.05
    EPS_DECAY: int = 1000
    TAU: float = 0.005
    LR: float = 1e-3

Transition = namedtuple("Transition", ("state", "action", "next_state", "reward"))

class TetrisWrapper:
    '''
    Wrapper for Tetris
    '''
    board_height = 20
    board_width = 10
    figure_types = 7

    def __init__(self):
        self.action_space_n = 4*self.board_width # 4 rotations for each column
        self.action_space = []
        for rotation in range(4):
            for x in range(self.board_width):
                self.action_space.append((rotation, x))

        # Create action space (using all placements) (not currently using this implementation)
        # self.action_space = []
        # for figure in Figure.figures:
        #     self.action_space.append(get_legal_placements(Tetris(height=TetrisWrapper.board_height, width=TetrisWrapper.board_width), figure))
        # self.action_space_n = 4*self.board_width # 4 rotations for each column, max for each figure

        self.reset()
        self.state_space_n = len(TetrisWrapper._flatten_state(self.tetris))

    def reset(self) -> Tuple[np.array, dict]:
        self.tetris = Tetris(height=20, width=10)
        self.tetris.new_figure()
        return TetrisWrapper._flatten_state(self.tetris), {}

    def _flatten_state(tetris:Tetris) -> np.array:
        '''Encode state as field and current figure'''
        state = np.array(tetris.field).astype(np.float32).flatten()
        # TODO: use more than one figure to encode state
        current_figure = np.zeros(TetrisWrapper.figure_types)
        current_figure[tetris.figure.type] = 1
        return np.concatenate([state, current_figure.flatten()])

    def dqn_evaluate_state(self, tetris:Tetris) -> float:
        return tetris.score*100

    def step(self, action: int):
        """
        Returns:
            tuple: A tuple containing the next state, reward, done flag, truncated flag and additional info.
        """
        truncated = False
        rotation, x = self.action_space[action]

        self.tetris = simulate_placement(self.tetris, self.tetris.figure, rotation, x)
        reward = self.dqn_evaluate_state(self.tetris)

        # Check if game is over
        done = self.tetris.state == "gameover"
        truncated = self.tetris.score > 100

        return TetrisWrapper._flatten_state(self.tetris), reward, done, truncated, {}


class DQN(nn.Module):
    def __init__(self, n_observations, n_actions):
        """
        Initializes the DQN model.

        Args:
            n_observations (int): The size of the input observation space.
            n_actions (int): The number of possible actions.
        """
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(n_observations, 128)
        self.fc2 = nn.Linear(128, 128)
        self.fc3 = nn.Linear(128, n_actions)

    def forward(self, x):
        """
        Forward pass of the DQN model.

        Args:
            x (torch.Tensor): The input tensor.

        Returns:
            torch.Tensor: The output tensor.
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)
        return x


class ReplayMemory:
    """
    Replay memory to store transitions.
    """

    def __init__(self, capacity: int):
        """Initialize the replay memory.

        Args:
            capacity (int): The maximum number of transitions to store.
        """
        # create a deque to store the transitions
        self.memory = deque(maxlen=capacity)

    def push(self, *args):
        """Save a transition"""
        # append a transition to the memory
        # if the memory is full, remove the oldest transition
        self.memory.append(Transition(*args))

    def sample(self, batch_size):
        """
        Sample a batch of transitions.

        Args:
            batch_size: The number of transitions to sample.

        Returns:
            list: A list of sampled transitions.
        """
        # randomly sample a batch of transitions
        return random.sample(self.memory, batch_size)

    def __len__(self):
        return len(self.memory)


class DQNTrainer:
    def __init__(
        self,
        env: TetrisWrapper,
        memory: ReplayMemory,
        device: torch.device,
        params: HyperParams,
        max_steps_per_episode: int = 500,
        num_episodes: int = 50,
    ) -> None:
        """
        Initializes the DQNTrainer with the required components to train a DQN agent.
        """
        self.env = env
        self.policy_net = DQN(env.state_space_n, env.action_space_n).to(device)
        self.target_net = DQN(env.state_space_n, env.action_space_n).to(device)
        self.target_net.load_state_dict(self.policy_net.state_dict())
        self.target_net.eval()
        self.optimizer = optim.Adam(self.policy_net.parameters(), lr=params.LR)
        self.memory = memory
        self.device = device
        self.params = params
        self.max_steps_per_episode = max_steps_per_episode
        self.num_episodes = num_episodes

        # Track rewards per episode
        self.episode_rewards = []
        # Count the number of steps
        self.steps_done = 0

    def select_action(self, state_tensor: torch.Tensor) -> torch.Tensor:
        """
        Selects an action using an epsilon-greedy policy based on current Q-network.
        """
        # Compute epsilon threshold
        sample = random.random()
        eps_threshold = self.params.EPS_END + (self.params.EPS_START - self.params.EPS_END) * \
                        math.exp(-1. * self.steps_done / self.params.EPS_DECAY)
        # Update steps
        self.steps_done += 1

        tetris = self.env.tetris
        valid_rotations = list(range(len(Figure.figures[tetris.figure.type])))

        # Exploit or explore
        if sample > eps_threshold:
            with torch.no_grad():
                # Get Q-values for all actions
                q_values = self.policy_net(state_tensor)
                
                # Mask invalid rotations by setting their Q-values very low
                # print("q_values for the current state: ", q_values)
                # print(q_values[:])
                # print(q_values[:,[r for r in range(self.env.action_space_n) if r not in valid_rotations]])
                for i in range(self.env.action_space_n):
                    if self.env.action_space[i][0] not in valid_rotations:
                        q_values[:,i] = -float('inf')
                    else:
                        # Check valid x bounds
                        min_x = min([j for i in range(4) for j in range(4) if i*4 + j in tetris.figure.image()])
                        max_x = max([j for i in range(4) for j in range(4) if i*4 + j in tetris.figure.image()])

                        min_allowed_x = -min_x
                        max_allowed_x = tetris.width - max_x - 2
                        if self.env.action_space[i][1] < min_allowed_x or self.env.action_space[i][1] > max_allowed_x:
                            q_values[:,i] = -float('inf')

                # Choose best action from valid options
                return q_values.max(1).indices.view(1, 1)

                # return self.policy_net(state_tensor).max(1).indices.view(1, 1) # provided
        else:
            # Choose random action
            action_taken = random.choice([(r,x) for r,x in self.env.action_space if r in valid_rotations]) # chose from valid actions
            action_idx = self.env.action_space.index(action_taken)
            return torch.tensor(
                [[action_idx]],
                device=self.device,
                dtype=torch.long,
            )

    def train(self) -> None:
        for _ in range(self.num_episodes):
            obs, info = self.env.reset()
            state = torch.tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            episode_reward = 0.0

            for _ in range(self.max_steps_per_episode):
                # Select an action using self.select_action()
                action = self.select_action(state)

                # Execute the action in the environment to get observation, reward, termination, and truncation signals.
                obs, reward, done, truncated, _ = self.env.step(action.item())

                # Convert observations to tensor (if not terminal) to form next_state.
                next_state = None if done else torch.tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)

                # Save the transition in replay memory using self.memory.push().
                self.memory.push(state, action, next_state, torch.tensor([reward], device=self.device))

                # Advance state to next_state.
                state = next_state

                # Run optimization step (self.optimize_model()).
                self.optimize_model()

                # Perform soft update (self.soft_update()).
                self.soft_update()

                # Accumulate the reward for the episode.
                episode_reward += reward

                # Break the loop when a terminal or truncated state is reached.
                if done or truncated:
                    break

            # Tracking episode reward and plotting rewards.
            self.episode_rewards.append(episode_reward)

        print("Training complete")
        # Save model
        torch.save(self.policy_net.state_dict(), "tetris_dqn_model.pth")
    

    def soft_update(self) -> None:
        """
        Soft update of target network parameters.
        """
        # Retrieve the state dictionaries for both target_net and policy_net
        target_net_state_dict = self.target_net.state_dict()
        policy_net_state_dict = self.policy_net.state_dict()

        # For each parameter in the state dictionary:
        # target_param = tau * policy_param + (1 - tau) * target_param
        tau = self.params.TAU
        for key in target_net_state_dict:
            target_net_state_dict[key] = tau * policy_net_state_dict[key] + (1 - tau) * target_net_state_dict[key]

        # Load the updated state dictionary into target_net
        self.target_net.load_state_dict(target_net_state_dict)    

    def optimize_model(self) -> None:
        """
        Performs one gradient descent update on the policy network using a random minibatch sampled from replay memory.
        """
        # STEP 1: Check if there's enough data in replay memory; if not, simply return.
        # Check memory size (e.g., if len(self.memory) < self.params.BATCH_SIZE: return)
        if len(self.memory) < self.params.BATCH_SIZE:
            return

        # STEP 2: Sample a minibatch of transitions from replay memory.
        # Sample a batch of transitions from self.memory
        transitions = self.memory.sample(self.params.BATCH_SIZE)
        batch = Transition(*zip(*transitions))

        # STEP 3: Unpack transitions into batches for state, action, reward, and next_state.
        # Unpack the sampled transitions into batches
        state_batch = torch.cat(batch.state)
        action_batch = torch.cat(batch.action)
        reward_batch = torch.cat(batch.reward)
        non_final_next_states = torch.cat([s for s in batch.next_state if s is not None])

        # STEP 4: Prepare masks and tensors:
        # - Create a mask for non-terminal transitions.
        # - Concatenate non-terminal next states into a single tensor.
        # Create a boolean mask for non-final states and form the non_final_next_states tensor
        non_final_mask = torch.tensor(tuple(map(lambda s: s is not None, batch.next_state)), device=self.device, dtype=torch.bool)

        # STEP 5: Calculate current Q-values:
        # - Pass the state batch through the policy network.
        # - Gather Q-values corresponding to the taken actions.
        # Pass state_batch through self.policy_net and use gather to obtain state_action_values
        state_action_values = self.policy_net(state_batch).gather(1, action_batch)

        # STEP 6: Compute next state Q-values for non-terminal states:
        # - For non-terminal states, compute the maximum Q-value with the target network.
        # - For terminal states, the Q-value is 0.
        # Compute next_state_values using self.target_net on non_final_next_states
        next_state_values = torch.zeros(self.params.BATCH_SIZE, device=self.device)
        next_state_values[non_final_mask] = self.target_net(non_final_next_states).max(1)[0].detach()

        # STEP 7: Compute the target Q-values using the Bellman equation:
        # target = reward + gamma * next_state_value
        # Compute expected_state_action_values using self.params.GAMMA and the reward_batch
        expected_state_action_values = (next_state_values * self.params.GAMMA) + reward_batch

        # STEP 8: Compute loss using Smooth L1 (Huber) loss:
        # Compute the loss between state_action_values and expected_state_action_values
        loss = F.smooth_l1_loss(state_action_values, expected_state_action_values.unsqueeze(1))

        # STEP 9: Optimize the model:
        # - Zero the gradients.
        # - Backpropagate the loss.
        # - Optionally clip the gradients.
        # - Perform a step with the optimizer.
        # Zero gradients, perform backpropagation (loss.backward()), optionally clip gradients, and then call self.optimizer.step()
        self.optimizer.zero_grad()
        loss.backward()
        for param in self.policy_net.parameters():
            param.grad.data.clamp_(-1, 1)
        self.optimizer.step()


if __name__ == "__main__":
    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Initialize environment
    env = TetrisWrapper()

    # Initialize replay memory
    memory = ReplayMemory(10000)

    # Initialize hyperparameters
    params = HyperParams()

    # Initialize DQNTrainer
    trainer = DQNTrainer(env, memory, device, params, max_steps_per_episode=500, num_episodes=1500)

    # Train the agent
    trainer.train()

    # Plot the rewards
    plt.plot(trainer.episode_rewards)
    plt.title("Episode Rewards")
    plt.xlabel("Episode")
    plt.ylabel("Reward")
    plt.savefig("dqn_rewards.jpg")
    plt.show()
