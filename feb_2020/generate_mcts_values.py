from mcts_v2 import *

class MCTSCostPolicy(CostPolicy):
    def node_cost(self, node):
        '''
        node: a networkx node
        Returns the average distance that an agent must move to reach a 
        reward from node position if it becomes available at this node
        '''
        steps_from_root = self.tree.nodes[node]['steps_from_root']
        # Use sampled cell distances to calculate node cost
        expected_steps = self.calculate_expected_steps(node)

        num_observations = self.tree.nodes[node]['new_observations']

        average_reward_distance = expected_steps / num_observations # 

        cost = steps_from_root + average_reward_distance

        return cost

    def calculate_expected_steps(self, node):
        '''
        To calculate expected steps from 'sampled_cell_distances', we get the average
        of the sampled distances and multiply by the number of cells in the node.
        '''
        try:
            samples_strings = self.tree.nodes[node]['sampled_cell_distances'].split(',')
        except:
            raise RuntimeError(f'{node}')
        samples = [int(sample) for sample in samples_strings]

        num_cells = int(self.tree.nodes[node]['new_observations'])
        num_samples = len(samples)

        expected_steps = (sum(samples) / num_samples) * num_cells

        return expected_steps

class SampleCellDistances(UCTSearch):
    def __init__(self):
        super().__init__()
        self.total_num_cells = 0

    def default_policy(self, leaf_node): # DONE
        self.tree.nodes[leaf_node]['visited'] = True

        current_node = leaf_node

        sim_nodes = []
        while not self.terminal(current_node):
            num_of_children = self.num_children(current_node)
            assert num_of_children != 0, f'{current_node} has no children'
            # Choose a child of current_node random (uniform distribution)
            current_node = self.get_children(current_node, index=randrange(num_of_children))
            
            # Randomly sample from current_node's 'cell_distances'
            self.sample_cell_distances(current_node)

            # Add current_node to record of nodes traversed in the simulation
            sim_nodes.append(current_node)
        print(sim_nodes)
        return self.get_reward(current_node, sim_nodes)

    def get_reward(self, current_node, node_list): #TODO Redefine get_reward
        cost_policy = MCTSCostPolicy(self.tree)

        if len(node_list) == 0:
            print('terminal node')
            reward = 1 / cost_policy.total_expected_cost(current_node)

            return reward
        else:
            print('nonterminal node')
            value_list = [cost_policy.total_expected_cost(node) for node in node_list]
            reward = 1 / sum(value_list)

            return reward
    ### Helper methods ###
    
    def sample_cell_distances(self, node):
        '''
        Samples a random value from 'cell_distances' attribute of node and 
            updates 'sampled_cell_distances' attribute
        Returns None
        '''
        cell_distances = self.tree.nodes[node]['cell_distances'].split(',')
        index = randrange(len(cell_distances))

        sampled_value = cell_distances[index]

        try:
            samples = self.tree.nodes[node]['sampled_cell_distances'].split(',')

        except KeyError:
            samples = []

        samples.append(sampled_value)

        self.tree.nodes[node]['sampled_cell_distances'] = ','.join(samples)

        return None
    
    def update_num_cells(self, value):
        '''
        Increases self.total_num_cells by value
        '''
        self.total_num_cells += int(value)

        return None

if __name__ == "__main__":
    all_graphs = iterate_graph_builder('tree_builder\\worlds')

    courtyard_graph = all_graphs['courtyard']

    my_sampler = SampleCellDistances(courtyard_graph)

    print(my_sampler.run(my_sampler.absolute_root_node))