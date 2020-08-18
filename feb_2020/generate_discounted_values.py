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



def generate_discounted_values(data_frame, discount_factors:iter):
    '''
    '''
    # Generate a sorted data frame with relevant node data
    node_df = data_frame

    last_world = ''

    for factor in discount_factors:
        new_value_column = []
        # row[0] == 'world' and row[2] == 'child'
        for row in node_df.itertuples(index=False):
            if row[0] == 'tworooms3':
                continue
            # if the current world matches the last world, use the same CostPolicy instance
            elif row[0] == last_world:
                continue
            else:
                discount_policy = CostPolicy(graphs[row[0]])
            
            node_value = discount_policy.total_expected_cost(row[2], factor)
            new_value_column.append(round(node_value, 3))
        
        node_df[f'dv_{round(factor, 2)}'] = new_value_column

    return node_df

data_frame = import_data_file('data\\treeNodePolicyE1E2Attrib.csv').sort_values(by=['world'])

graphs = iterate_graph_builder('tree_builder\\worlds_2')

number_of_values = 100
discounted_values_df = generate_discounted_values(data_frame, np.linspace(0, 0.99, num=number_of_values))

output_filepath = f'output//discounted_values_from_root_zero_gamma.csv'
discounted_values_df.to_csv(output_filepath, sep='\t', index=False)