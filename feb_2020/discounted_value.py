from optimal_policy import *

class discountedValue(optimalPolicy):
    
    def best_child_cost(self, node, factor=0.5):
        discounted_best_child_cost = factor * super().best_child_cost(node)

        return discounted_best_child_cost

graphs = iterate_graph_builder('tree_builder\\worlds')

my_policy = discountedValue(graphs['cubicles'])

print(my_policy.total_expected_cost('N4214308'))
    