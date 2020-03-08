import os, networkx as nx, sys, pandas as pd, numpy as np, copy
from graph_builder import *

# os.getcwd() # Check current directory

def iterate_graph_builder(directory: str):
    '''
    Build graphs from all csv files within directory. 
    Returns a dictionary with key:value as maze_name:maze_graph
    '''
    world_names = os.listdir(directory) # List of all world names
    graphs = {}
    # Store each graph as a value, keyed by the corresponding world name.
    for world in world_names:
        graphs[world.replace('.csv', '')] = build_graph(directory + '\\' + world)
    
    return graphs

class CostPolicy():
    def __init__(self, graph):
        '''
        Initialize the optimalPolicy object with a networkx maze graph.
        '''
        self.graph = graph
        
    def has_children(self, node):
        '''
        node: a node from a networkx graph
        Returns True if node has children; False otherwise.
        '''
        # graph.out_gree[node] gives number of node's children
        if self.graph.out_degree[node] > 0:
            return True
        else:
            return False

    def is_root_node(self, node):
        '''
        Determine if a node is the root of a decision tree.
        Input: Name of the node
        Returns True if node is a root; False otherwise.
        '''
        if int(self.graph.in_degree(node)) == 0:
            return True

        else:
            return False

    def get_children(self, node):
        '''
        Input: Name of the node
        Returns list of the node's children
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
        
        # Total number of unobserved squares before visiting a node.
        num_unobserved_squares = self.graph.nodes[node]['new_observations'] + \
        self.graph.nodes[node]['black_remains'] 

        # Probability given by number of observations to be made at node divided 
        # by number of possible reward locations.
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
    
    def best_child_cost(self, node):
        '''
        '''
        cost = min((self.total_expected_cost(child) for child in self.get_children(node)))

        return cost
        
    def total_expected_cost(self, node, discount_factor=1):
        '''
        Calculate the total expected cost of visiting a node. This is based on the 
        expected cost of the node in question plus the expected cost of its children, 
        so the calculation is recursive.

        node: Name of the node
        discount_factor: a value between 0 and 1 to discount best_child_cost. Default discount_factor is 1,
        corresponding to the optimal value policy.
        Returns 0 if the node is a root, node_cost(node) if the node is a leaf. 
        Otherwise, returns the total expected cost of the node.
        '''
        if self.is_root_node(node):
            return 0

        # Create base case for recursion.
        # Return the individual node cost if the node is a leaf.
        elif self.has_children(node) is False:
            # Confirm that if we've reached the last
            # set of observations, the probability of finding the reward is 100%
            assert int(self.reward_probability(node)) == 1, \
            f'Reward probability is {self.reward_probability(node)}'

            return self.node_cost(node)

        # Total cost = (probability of finding the reward at node * individual node cost) 
        # + (probability of finding the reward in node's children * total cost of best child)
        else:
            total_cost = (self.reward_probability(node) * self.node_cost(node)) + \
            (1 - self.reward_probability(node)) * discount_factor * self.best_child_cost(node)

            return total_cost