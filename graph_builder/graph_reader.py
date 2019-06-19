# graphReader.py
# Reads graphml files that were created in Cytoscape
# Make sure attribute names from graph correspond to the strings below
# Requires networkx module


def readGraph(file_name):
    
    G = nx.read_graphml(file_name)

    relabel = {}
    for node in G.nodes:
        relabel[node] = G.nodes[node]['name']

    H = nx.relabel_nodes(G,relabel)

    for node in H.nodes:
        del H.nodes[node]['SUID']
        del H.nodes[node]['shared name']
        del H.nodes[node]['selected']

    my_edges = list(H.edges())

    for edge in H.edges:
        del H.edges[edge]['SUID']
        del H.edges[edge]['shared name']
        del H.edges[edge]['shared interaction']
        del H.edges[edge]['selected']

    for edge in H.edges:
        H.edges[edge]['weight'] = H.edges[edge]['steps_from_parent']
        
    return H
