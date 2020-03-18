import os, networkx as nx, sys, pandas as pd, numpy as np, copy
from math import sqrt, inf, log
from random import randrange
from graph_builder import *
from cost_policy import *


class UCTSearch():
    def __init__(self, tree):
        self.tree = copy.deepcopy(tree)
        self.absolute_root_node = self.get_absolute_root_node()
        self.mcts_root_node = ''

        # Literature suggests using c=1/sqrt(2) for optimal behavior
        # if node values are normalized (between 0 and 1)
        self.exploration_constant = 1 / sqrt(2)
        self.terminal_nodes = self.get_terminal_nodes()
        self.iterations = 0
        
        # Initialize node statistics for MCTS used for selection, expansion, etc.
        nx.set_node_attributes(self.tree, 0, 'visit_count')
        nx.set_node_attributes(self.tree, 0, 'total_sim_reward')
        nx.set_node_attributes(self.tree, False, 'visited')
        
    def run(self, mcts_root_node):
        # Update the node being used as root to run MCTS
        self.mcts_root_node = mcts_root_node
        leaf_node = mcts_root_node

        while self.within_budget():
            reward = self.default_policy(leaf_node)
            self.backup(leaf_node, reward)
            leaf_node = self.tree_policy(mcts_root_node)
            
            self.iterations += 1
            
        self.iterations = 0

        # Return child with max average reward. Exploration constant set to
        # zero means we only care about exploitation component of UCT (average reward)
        return self.best_child(mcts_root_node, 0)

    def tree_policy(self, node):
        while self.num_children(node) != 0:
            if not self.fully_expanded(node):
                
                return self.expand(node)
            
            else:
                node = self.best_child(node, self.exploration_constant)
                
        return node
    
    def default_policy(self, leaf_node):
        self.tree.nodes[leaf_node]['visited'] = True

        current_node = leaf_node
        while not self.terminal(current_node):
            num_of_children = self.num_children(current_node)
            # Choose a child of current_node random (uniform distribution)
            current_node = self.get_children(current_node, index=randrange(num_of_children))
            
        return self.get_reward() # TODO Define get_reward
    
    def backup(self, node, reward):
        while True:
            self.tree.nodes[node]['visit_count'] += 1
            self.tree.nodes[node]['total_sim_reward'] += reward
            
            if node == self.mcts_root_node:
                break
            # Set node to current node's parent
            node = self.get_parents(node, 0)

            
            
    
    def best_child(self, node, exploration_constant):
        children = self.get_children(node)
        
        ucb_comparison_dict = {child: self.calculate_ucb_value(node, child, exploration_constant) for child in children}

        best_child = max(ucb_comparison_dict, key=lambda child: ucb_comparison_dict[child])

        if exploration_constant == 0:
            return best_child, ucb_comparison_dict

        return best_child
    
    def expand(self, node):
        unvisited_children = [child for child in self.get_children(node) if self.visited(child) is False]
        num_unvisited = len(unvisited_children)

        child_to_expand = unvisited_children[randrange(num_unvisited)]

        return child_to_expand

### Helper Methods ###
    def get_absolute_root_node(self):
        '''
        Returns the root node for self.tree
        '''
        absolute_root_node = [node for node, degree in self.tree.in_degree() if degree == 0]
        assert len(absolute_root_node) == 1, 'Tree has several root nodes.'

        # root_node should be a list with a node name. Return this name (string)
        return absolute_root_node[0]

    def terminal(self, node):
        '''
        Returns True if node is a terminal node, False otherwise.
        '''
        return node in self.terminal_nodes

    def get_terminal_nodes(self):
        '''
        Returns tuple of terminal nodes for self.tree
        '''
        terminal_nodes = tuple(v for v, d in self.tree.out_degree() if d == 0)
        
        return terminal_nodes
    
    def within_budget(self):
        '''
        Define computational budget that constrains number of MCTS iterations
        '''
        return self.iterations <= 10

    def num_children(self, node):
        num_of_children = len(list(self.tree.successors(node)))

        return num_of_children

    def num_parents(self, node):
        num_of_parents = len(list(self.tree.predecessors(node)))

        return num_of_parents

    def visited(self, node):
        return self.tree.nodes[node]['visited']

    def fully_expanded(self, node):
        '''
        Check if a node has been fully expanded. A node is fully expanded
            if all of its children have been visited. A node is visited if a 
            simulationhas been run from that node.
        Returns True if all node is fully expanded, False otherwise.
        '''
        children_visited_status = (self.visited(child) for child in self.get_children(node))
        
        # If fully expanded, all children will have 'visited' = True
        return False not in children_visited_status

    def get_children(self, node, index=None):
        '''
        Returns tuple of node's children. 
        If given an index, returns the child with that index in the list.
        '''
        if index is None:
            return tuple(self.tree.successors(node))

        else:
            return tuple(self.tree.successors(node))[index]

    def get_parents(self, node, index=None):
        '''
        Returns tuple of node's parents. 
        If given an index, returns the child with that index in the list.
        '''
        if index is None:
            return tuple(self.tree.predecessors(node))

        else:
            return tuple(self.tree.predecessors(node))[index]

    def calculate_ucb_value(self, node, child, exploration_constant):
        child_total_sim_reward = self.tree.nodes[child]['total_sim_reward']
        child_visit_count = self.tree.nodes[child]['visit_count']
        node_visit_count = self.tree.nodes[node]['visit_count']

        try:
            ucb_value = ((child_total_sim_reward / child_visit_count) + 
            (exploration_constant * sqrt((2 * log(node_visit_count)) / child_visit_count)))

        except ZeroDivisionError:
            return inf

        return ucb_value