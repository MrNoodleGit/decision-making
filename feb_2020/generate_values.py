from cost_policy import *

def import_data_file(file):
    '''
    Create a pandas data frame containing information from file. 
    file: A csv file containing world names, node names, and their corresponding values.
    Could be treeNodePolicy.csv, for example.
    Returns: A pandas data frame containing only the necessary columns from file.

    '''
    data_frame = pd.read_csv(file, sep='\t')

    return data_frame



def generate_discounted_values(discount_factors:iter):
    '''
    '''
    # Generate a sorted data frame with relevant node data
    node_df = import_data_file('data//treeNodePolicy.csv').sort_values(by=['world'])

    last_world = ''

    for factor in discount_factors:
        new_value_column = []
        # row[0] == 'world' and row[2] == 'child'
        for row in node_df.itertuples(index=False):
            # if the current world matches the last world, use the same costPolicy instance
            if row[0] == last_world:
                continue
            else:
                discount_policy = costPolicy(graphs[row[0]])
            
            node_value = discount_policy.total_expected_cost(row[2], factor)
            new_value_column.append(round(node_value, 3))
        
        node_df[f'dv_{round(factor, 2)}'] = new_value_column

    return node_df

graphs = iterate_graph_builder('tree_builder\\worlds')

discounted_values_df = generate_discounted_values(np.arange(0.5, 1, 0.05))

discounted_values_df.to_csv('output//discounted_node_policy.csv', sep='\t')