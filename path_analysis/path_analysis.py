#%% Change working directory from the workspace root to the ipynb file location. Turn this addition off with the DataScience.changeDirOnImportExport setting
# ms-python.python added
import os
try:
	os.chdir(os.path.join(os.getcwd(), 'path_analysis'))
	print(os.getcwd())
except:
	pass
#%% [markdown]
# ## Build all graphs from the available tables

#%%
import sys, os
sys.path.append('C:\\Users\\ronal\\Documents\\GitHub\\decision-making\\graph_builder') # Append path where graph_builder.py is saved
from graph_builder import *

file_names = os.listdir('treebuilderUpdated')
graphs = {}
for file in file_names:
    graphs[file.replace('.csv', '')] = build_graph('treebuilderUpdated\\' + file)

#%% [markdown]
# # We begin to write the path analysis program
#%% [markdown]
# ## Helper functions

#%%
# Helper function for analyze_path()
def parse_path_string(path_string):
    a = path_string.replace('p','')
    b = a.split(';')
    b.remove('')
#     e = [tuple(int(s) for s in i.split(',')) for i in d]         Useful for converting strings of tuples in real tuples
    
    return b


#%%
# Helper function for analyze_path(). Returns the root node for a graph.
def root_node(graph):
    root = [v for v, d in graph.in_degree() if d == 0][0]
    return root


#%%
def leaf_nodes(graph):
    leaves = [v for v, d in graph.out_degree() if d == 0]
    return leaves


#%%
# Helper function for analyze_path()
def value_calculation(graph, node, steps_so_far, prior_prob):
    new_observations = graph.nodes[node]['new_observations']
    ep = graph.nodes[node]['node_ep']
    value = ((steps_so_far * new_observations) + ep) * prior_prob
    
    return value


#%%
# Helper function for analyze_path(). Returns the node in successors which corresponds to the input_location if it is found. Returns False otherwise.
def location_in_successors(graph, input_location, current_node):
    node_location_dict = (nx.get_node_attributes(graph, 'node_location'))
    successor_list = list(graph.successors(current_node))
    
    for successor in successor_list:
        if node_location_dict[successor] == input_location:
            return successor
        
    else:
        return False


#%%
def num_successors(graph, node):
    num_of_successors = len(list(graph.successors(node)))
    
    return num_of_successors


#%%
def get_successors(graph, node, index=None): # Returns list of successors. If given an index, returns the successor with that index in the list.
    if index is None:
        return list(graph.successors(node))
    
    else:
        return list(graph.successors(node))[index]


#%%
def all_node_paths(graph):
    all_paths = []
    
    for path in nx.all_simple_paths(graph, root_node(graph), leaf_nodes(graph)):
        all_paths.append(path)
        
    return all_paths


#%%
def possible_subject_paths(graph, subject_sequence): # Input list of nodes subject visited. Returns possible paths that subject could have taken to reach leaf nodes.
                                            # Use if last node in subject_sequence is not in leaf_nodes().
    subject_set = set(subject_sequence)
    num_common_nodes = [] # Number of nodes that each sequence in all_node_paths() has in common with subject_sequence
    for path in all_node_paths(graph):
        num_common_nodes.append(len(set(path) & subject_set))

#     print(num_common_nodes)

    similarity_degree = max(num_common_nodes)

    possible_subject_paths = [path for idx, path in enumerate(all_node_paths(graph)) if num_common_nodes[idx] == similarity_degree]
    
    
    return possible_subject_paths


#%%
def generic_path_value(graph, path): # Returns (generic) value of the node path (as defined by the last node in the path).
    last_node = path[-1]
    
    generic_path_value = graph.nodes[last_node]['node_value']
    
    return generic_path_value
    


#%%
def extra_node_lists(graph, subject_sequence): # Input list of nodes subject visited. Returns list of sequences of remaining nodes for each possible subject path.
    _possible_subject_paths = possible_subject_paths(graph, subject_sequence)
    num_possible_paths = len(_possible_subject_paths)
    extra_node_lists = [[node for node in _possible_subject_paths[i] if node not in subject_sequence] for i in range(num_possible_paths)]
    
    return extra_node_lists


#%%
def prior_prob(graph):
    _root_node = root_node(graph)
    total_black_squares = graph.nodes[_root_node]['black_remains']
    prior_prob = 1/total_black_squares
    
    return prior_prob


#%%
def valid_location(graph, step, visited_locations, current_node, previous_node):
    if previous_node == '':
        return
    
    successors = get_successors(graph, current_node)
    previous_successors = get_successors(graph, previous_node)
    
    node_location_dict = nx.get_node_attributes(graph, 'node_location')
    
    successor_locations = [node_location_dict[k] for k in node_location_dict if k in successors] # Successor locations for current node
    previous_successor_locations = [node_location_dict[k] for k in node_location_dict if k in previous_successors] # Successor locations for previous node
    
    node_locations = list(node_location_dict.values())
    
    valid_locations = visited_locations.copy()

    valid_locations.update(successor_locations)
    valid_locations.update(previous_successor_locations)
    
    
    if step in node_locations:
        if step in valid_locations:
            pass
        else:
            return False


#%%
def alt_node_paths(graph, chosen_path):
    _all_node_paths = all_node_paths(graph)
    alt_node_paths = _all_node_paths.copy()
    alt_node_paths.remove(chosen_path)
    
    path_value_dict = {','.join(path):generic_path_value(graph, path) for path in alt_node_paths} # Keys are a string of nodes seperated by commas. Use list.split() method to convert into list.
    
    return path_value_dict
    
    

#%% [markdown]
# ## Path analysis function

#%%



#%%
def analyze_path(graph, path): # Takes path string as input.
    PRIOR_PROB = prior_prob(graph)
    steps_so_far = 0

    current_node = root_node(graph)
    previous_node = ''
    node_sequence = [root_node(graph)]
    path_value = 0
    input_path = parse_path_string(path)
    LEAF_NODES = leaf_nodes(graph)
    
    all_visited_locations = {'(0,0)'} # First visited location is subject's starting position.

    for step in input_path[1:]:
        if valid_location(graph, step, all_visited_locations, current_node, previous_node) is False:
            return ['ERROR_PATH', step, current_node]
        else:
            if location_in_successors(graph, step, current_node) is not False:
                previous_node = current_node
                current_node = location_in_successors(graph, step, current_node)
                node_sequence.append(current_node)
                steps_so_far += 1
                current_node_value = value_calculation(graph, current_node, steps_so_far, PRIOR_PROB)
                graph.nodes[current_node]['node_value'] = current_node_value
                path_value += current_node_value
            else:
                steps_so_far += 1
            all_visited_locations.add(step)
    
    empirical_path_value = path_value # Saves path value at the last node the subject visited in experiment
    empirical_path = node_sequence # Saves sequence of nodes subject visited in experiment
    empirical_last_node = current_node
    
#     print('empirical path is', empirical_path)
#     print('empirical step number is', steps_so_far)
#     print('empirical pathvalue is', empirical_path_value)
#     print('empirical last node is', empirical_last_node)
    
#     #####################################################################################
    _extra_node_lists = extra_node_lists(graph, empirical_path)
    path_comparison_dict = {}
    
    for node_list in _extra_node_lists:
        node_sequence = empirical_path
        path_value = empirical_path_value
        current_node = empirical_last_node
        
        while True:
            try: 
                next_node = node_list.pop(0)
                steps_so_far += graph.succ[current_node][next_node]['steps_from_parent']                
                current_node = next_node
                node_sequence.append(current_node)
                path_value += value_calculation(graph, current_node, steps_so_far, PRIOR_PROB)
            except IndexError:
                path_comparison_dict[','.join(node_sequence)] = path_value
                break
                
    final_path_string = min(path_comparison_dict, key = lambda k: path_comparison_dict[k]) # If the subject did not reach a leaf, this is the path we assume the subject would have taken (the optimal choice).
    final_path = final_path_string.split(',')
    final_path_value = path_comparison_dict[final_path_string]
#     print('The chosen node path is', final_path, 'with value', final_path_value) # We only care about the value of the paths, so it does not matter if more than one path has the same value.
    alt_path_values = sorted(list(alt_node_paths(graph, final_path).values()))
#     print('The alternative values are ', alt_path_values)
    all_values = [str(round(final_path_value, 3))]
    all_values.extend([str(round(num, 3)) for num in alt_path_values])

    output = [final_path_string, round(final_path_value, 3)]
    output.append(';'.join(all_values))
    
    return output
    
#   print(node_sequence)
#   print(path_comparison_dict)
    

#%% [markdown]
# ## Analyze experimental data

#%%
import pandas as pd

experiment_data_frame = pd.read_csv('squareLabelsWithRT_E2.csv', sep='\t')

previous_subject = ''
previous_world = ''
previous_path = ''
# previous_index = 0
input_data = []

# i = 0
for row in experiment_data_frame.itertuples():
    if previous_subject != row[1]:
        input_data.append([previous_subject, previous_world, previous_path])
    
#     previous_index = index + 2
    previous_subject = row[1]
    previous_world = row[2]
    previous_path = row[3]
    
input_data.append( # Add last row of the data frame manually, since algorithm above misses it
                  [experiment_data_frame.iloc[-1]['subject'], 
                   experiment_data_frame.iloc[-1]['world'], 
                   experiment_data_frame.iloc[-1]['squarepath']
                  ]
                 )    
    
#     if i == 2000:
#         break
#     i += 1
    
input_data.pop(0)


#%%
from copy import deepcopy

num_error_paths = 0
output_data = deepcopy(input_data)

for row in output_data: # Analyze path that each subject followed
    graph_name = row[1]
    input_path = row[2]
    path_analysis = analyze_path(graphs[graph_name], input_path)
    row.extend(path_analysis)
    
    if path_analysis[0] == 'ERROR_PATH':
        num_error_paths += 1

print(f'{len(output_data)} paths analyzed')
print(f'There are {num_error_paths} error paths')


#%%
# Export path analysis as csv
import csv

column_titles = ['subject', 'world', 'square_path', 'chosen_node_path', 'chosen_value', 'all_values'] # The first item in the column 'all_values' is the chosen value

with open('anaylzed_subject_data.csv', 'w') as file:
    file_writer = csv.writer(file, delimiter='\t')
    file_writer.writerow(column_titles)
    
    for row in output_data:
        file_writer.writerow(row)


#%%
error_data = []
for row in output_data:
    if row[3] == 'ERROR_PATH':
        error_data.append(row)


#%%
# Export error data
import csv

column_titles = ['subject', 'world', 'square_path', 'path_type', 'error_step', 'error_node']

with open('error_data.csv', 'w') as file:
    file_writer = csv.writer(file, delimiter='\t')
    file_writer.writerow(column_titles)
    
    for row in error_data:
        file_writer.writerow(row)

