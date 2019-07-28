import networkx as nx
from random import randrange
from math import sqrt, log, inf

import sys, os
working_directory = 'C:\\Users\\ronal\\Documents\\GitHub\\decision-making\\'
# Append path where graph_builder.py is saved
sys.path.append(working_directory + 'graph_builder')
from graph_builder import *

file_names = os.listdir(working_directory + 'path_analysis\\treebuilderUpdated')
graphs = {}
for file in file_names:
    graphs[file.replace('.csv', '')] = build_graph(
        working_directory + 'path_analysis\\treebuilderUpdated\\' + file)

class UCTSearch():
    def __init__(self, tree):
        self.tree = tree.copy()
        self.exploration_constant = 1 / sqrt(2)
        self.terminal_nodes = self.tree_terminal_nodes(self.tree)
        self.set_terminal_values(self.terminal_nodes)
        
        # Initialize node statistics
        nx.set_node_attributes(self.tree, 0, 'visit_count')
        nx.set_node_attributes(self.tree, 0, 'total_sim_reward')
        nx.set_node_attributes(self.tree, False, 'visited')
        
    def run(self, root_node, iterations): # DONE
        i = 0
        leaf_node = root_node

        while i < iterations:
            reward = self.default_policy(leaf_node)
            self.backup(leaf_node, reward)
            leaf_node = self.tree_policy(root_node)
            
            i += 1
            
        return self.best_child(root_node, 0)
        
    def tree_policy(self, node): # DONE
        while self.num_successors(node) != 0:
            if self.fully_expanded(node) is False:
                
                return self.expand(node)
            
            else:
                node = self.best_child(node, self.exploration_constant)
                
        return node
    
    def default_policy(self, leaf_node): # DONE
        sim_node = leaf_node
        self.tree.nodes[sim_node]['visited'] = True
        
        while self.terminal(sim_node) is False:
            num_of_successors = self.num_successors(sim_node)
            sim_node = self.get_successors(sim_node, index=randrange(num_of_successors))
            
        return self.get_terminal_value(sim_node)
    
    def backup(self, node, reward): # DONE
        while True:
            self.tree.nodes[node]['visit_count'] += 1
            self.tree.nodes[node]['total_sim_reward'] += reward
            
            if self.num_predecessors(node) == 0:
                break
                
            node = self.get_predecessors(node, 0)
            
    
    def best_child(self, node, exploration_constant): # DONE
        children = self.get_successors(node)
        
        ucb_comparison_dict = {child: self.ucb(node, child, exploration_constant) for child in children}

        best_child = max(ucb_comparison_dict, key=lambda x: ucb_comparison_dict[x])

        if exploration_constant == 0:
            return best_child, ucb_comparison_dict

        return best_child
    
    def expand(self, node):# DONE
        unvisited_children = [child for child in self.get_successors(node) if self.visited(child) is False]
        num_unvisited = len(unvisited_children)

        child_to_expand = unvisited_children[randrange(num_unvisited)]

        return child_to_expand
    
    
    
    #############################################################
    ## HELPER METHODS
    def num_successors(self, node):
        num_of_successors = len(list(self.tree.successors(node)))

        return num_of_successors
    
    def get_successors(self, node, index=None):
        '''Returns list of successors. If given an index, 
        returns the successor with that index in the list.'''
        if index is None:
            return list(self.tree.successors(node))

        else:
            return list(self.tree.successors(node))[index]
        
    def num_predecessors(self, node):
        num_of_predecessors = len(list(self.tree.predecessors(node)))

        return num_of_predecessors
        
    def get_predecessors(self, node, index=None):
        '''Returns list of predecessors. If given an index, 
        returns the predecessor with that index in the list.'''
        if index is None:
            return list(self.tree.predecessors(node))

        else:
            return list(self.tree.predecessors(node))[index]
        
    def get_terminal_value(self, terminal_node):
    
        terminal_value = self.tree.nodes[terminal_node]['terminal_value']

        return terminal_value

    def get_path_value(self, node):
    
        path_value = self.tree.nodes[node]['path_value']

        return path_value
    
    def terminal(self, node):
        if self.tree.out_degree(node) == 0:
            return True
        else:
            return False
    
    def fully_expanded(self, node):
        children_visited_status = (self.visited(child) for child in self.get_successors(node))
        
        if False in children_visited_status:
            return False
        
        else:
            return True

    def visited(self, node):
        if self.tree.nodes[node]['visited'] is True:
            return True

        else:
            return False
    
    def ucb(self, node, child, exploration_constant):
        child_total_sim_reward = self.tree.nodes[child]['total_sim_reward']
        child_visit_count = self.tree.nodes[child]['visit_count']
        node_visit_count = self.tree.nodes[node]['visit_count']

        try:
            ucb_value = ((child_total_sim_reward / child_visit_count) + 
            (exploration_constant * sqrt((2 * log(node_visit_count)) / child_visit_count)))

        except ZeroDivisionError:
            return inf

        return ucb_value

    def tree_terminal_nodes(self, tree):
        terminal_nodes = [v for v, d in tree.out_degree() if d == 0]
        
        return terminal_nodes

    def normalize_value(self, value, value_list):
        
        normalized_value = value / sum(value_list)

        return normalized_value

    def set_terminal_values(self, terminal_nodes):
        '''Inverts path_value of every terminal node 
        (since lower path_value is better, but MCTS optimizes for max in UCT equation)
        and normalizes each terminal value over sum of all terminal values'''

        inverted_terminal_values = {
            node: 1 / self.get_path_value(node) for node in terminal_nodes
        }

        s = sum(inverted_terminal_values.values())

        for node in inverted_terminal_values:
            self.tree.nodes[node]['terminal_value'] = inverted_terminal_values[node] / s

        
        