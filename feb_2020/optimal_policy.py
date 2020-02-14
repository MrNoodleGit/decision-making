import os, networkx as nx, sys, pandas as pd
from graph_builder import *

os.getcwd() # Check current directory

def iterate_graph_builder(directory: str):
    '''
    Build graphs from all csv files within directory. 
    Returns a dictionary with key:value = maze_name:maze_graph
    '''
    world_names = os.listdir(directory) # List of all world names
    graphs = {}
    for world in world_names:
        graphs[world.replace('.csv', '')] = build_graph(directory + '\\' + world) # Store each graph as a value, 
        # keyed by the corresponding world name.
    
    return graphs

graphs = iterate_graph_builder('tree_builder\\worlds') # Initialize graphs within our programming environment

class optimalPolicy():
    def __init__(self, graph):
        self.graph = graph # A networkx graph of a maze
        
    def has_children(self, node):
        '''
        node: a node from a networkx graph
        Returns True if node has children; False otherwise.
        '''
        if self.graph.out_degree[node] > 0: # If node has more than 0 children, has_children returns True
            return True
        else:
            return False

    def get_children(self, node):
        '''
        Returns list of children for a node
        '''
        children = list(self.graph.successors(node))

        return children 


    def reward_probability(self, node):
        '''
        Calculate the probability that a reward is in a node using the total number of 
        unobserved squares before visiting the node.
        Returns a probability > 0 and <= 1
        '''
        num_observations = self.graph.nodes[node]['new_observations']
        num_unobserved_squares = self.graph.nodes[node]['new_observations'] + self.graph.nodes[node]['black_remains'] # Total number of
        # unobserved squares before visiting a node.

        # Probability given by number of observations to be made at node divided by number of possible reward locations.
        return num_observations / num_unobserved_squares
        

    def node_cost(self, node):
        '''
        node: a networkx node
        Returns the average distance that an agent must move to reach a 
        reward from node position if it becomes available at this node
        '''
        steps_from_root = self.graph.nodes[node]['steps_from_root']
        expected_steps = self.graph.nodes[node]['expected_steps']
        num_observations = self.graph.nodes[node]['new_observations']

        average_reward_distance = expected_steps / num_observations # 

        cost = steps_from_root + average_reward_distance

        return cost
        
    def total_expected_cost(self, node):
        '''
        '''
        
        # Create base case for recursion
        if self.has_children(node) is False:
            # Confirm that if we've reached the last
            # set of observations, the probability of finding the reward is 100%
            assert int(self.reward_probability(node)) == 1, f'Reward probability is {self.reward_probability(node)}'

            return self.node_cost(node)

        else:
            expected_cost = self.reward_probability(node) * self.node_cost(node) + (1 - self.reward_probability(node)) * \
            min((self.total_expected_cost(child) for child in self.get_children(node)))

            return expected_cost


my_policy = optimalPolicy(graphs['courtyard'])

print(my_policy.total_expected_cost('N3719219'))