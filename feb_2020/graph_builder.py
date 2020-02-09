import pandas as pd
import networkx as nx

def build_graph(file_path):
    graph_data_frame = pd.read_csv(file_path, sep='\t') # Import map into pandas data frame
    graph_data_frame['PARENTID'].fillna('X', inplace=True) # Root nodes have no parent.

    G = nx.DiGraph(world=graph_data_frame['world'][0]) # Create networkx graph G and set graph attribute "world" to name of map
    edge_list = list(zip(graph_data_frame['PARENTID'], graph_data_frame['NID'])) # List of (parent, child) pairs
    edge_list.pop(0) # Remove edge leading to root node.
    G.add_edges_from(edge_list)

    name_dict = {node: name for node, name in
                          zip(graph_data_frame['NID'], graph_data_frame['NID'])
                          }
    node_location_dict = {node: location for node, location in
                          zip(graph_data_frame['NID'], graph_data_frame['nodeLocation'])
                          }
    depth_dict = {node: depth for node, depth in 
                  zip(graph_data_frame['NID'], graph_data_frame['depth'])
                          }
    new_observations_dict = {node: new_observations for node, new_observations in 
                             zip(graph_data_frame['NID'], graph_data_frame['N'])
                          }
    steps_from_root_dict = {node: steps for node, steps in 
                            zip(graph_data_frame['NID'], graph_data_frame['stepsFromRoot'])
                          }
    is_leaf_dict = {node: truth_value for node, truth_value in 
                    zip(graph_data_frame['NID'], graph_data_frame['isLeaf'])
                          }
#     path_value_dict = {node: value for node, value in 
#                        zip(graph_data_frame['NID'], graph_data_frame['node_value'])
#                           }
    node_ep_dict = {node: node_ep for node, node_ep in 
                    zip(graph_data_frame['NID'], graph_data_frame['nodeEP'])
                          }
    black_remains_dict = {node: black_remains for node, black_remains in 
                          zip(graph_data_frame['NID'], graph_data_frame['blackremains'])
                          }
    steps_from_parent_node_dict = {node: steps for node, steps in 
                          zip(graph_data_frame['NID'], graph_data_frame['S'])
                          }
    cell_distances_dict = {node: distances for node, distances in 
                          zip(graph_data_frame['NID'], graph_data_frame['cellDistances'])
                          }
    
    nx.set_node_attributes(G, name_dict, 'name')
    nx.set_node_attributes(G, node_location_dict, 'node_location')
    nx.set_node_attributes(G, depth_dict, 'depth')
    nx.set_node_attributes(G, new_observations_dict, 'new_observations')
    nx.set_node_attributes(G, steps_from_root_dict, 'steps_from_root')
    nx.set_node_attributes(G, is_leaf_dict, 'is_leaf')
#     nx.set_node_attributes(G, path_value_dict, 'path_value')
    nx.set_node_attributes(G, node_ep_dict, 'node_ep')
    nx.set_node_attributes(G, black_remains_dict, 'black_remains')
    nx.set_node_attributes(G, steps_from_parent_node_dict, 'steps_from_parent')
    nx.set_node_attributes(G, cell_distances_dict, 'cell_distances')

    path_from_parent_dict = {edge: path for edge, path in 
                             zip(edge_list, graph_data_frame['path_from_parent'][1:])
                            }
    steps_from_parent_edge_dict = {edge: steps for edge, steps in 
                             zip(edge_list, graph_data_frame['steps_from_parent'][1:])
                            }

    nx.set_edge_attributes(G, path_from_parent_dict, 'path_from_parent')
    nx.set_edge_attributes(G, steps_from_parent_edge_dict, 'weight') # Assign steps from parent to node as edge weight
    
    return G

