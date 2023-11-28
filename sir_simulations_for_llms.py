# -*- coding: utf-8 -*-
"""SIR simulations for LLMs.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DBcAgExEUVM628rEBGVZ79Sb4x9aq-JE
"""

# !pip install networkx
# !pip install ndlib
# !pip install torch_geometric

import networkx as nx
import ndlib
import ndlib.models.epidemics as ep
import ndlib.models.ModelConfig as mc
from time import time
import matplotlib.pyplot as plt
import torch_geometric.datasets as ds
import random
from torch_geometric.datasets import Planetoid
import json
from networkx.readwrite import json_graph
import numpy as np

def toEdgeList(G):
    # Write to Edge List
    nx.write_weighted_edgelist(G, "weighted_edge_list.txt")

def toAdjMatrix(G):
    # Get adjacency matrix as a SciPy sparse matrix
    adj_matrix_sparse = nx.adjacency_matrix(G)

    # Convert to a dense matrix (NumPy array)
    adj_matrix_dense = adj_matrix_sparse.todense()

    # Print the dense adjacency matrix
    print(adj_matrix_dense)

    # Optionally, save this to a file
    with open('adjacency_matrix.txt', 'w') as f:
        np.savetxt(f, adj_matrix_dense, fmt='%d')

    
def toJSON(G):
    # Convert to JSON data
    data = json_graph.node_link_data(G)
    
    # Convert JSON object to a string
    json_data = json.dumps(data, indent=4)
    
    # Print JSON string
    print(json_data)
    
    # Or save to a file
    with open('graph.json', 'w') as f:
        json.dump(data, f, indent=4)

    
def connSW(beta=None):
    # Randomize size between 1000 and 1500
    n = random.randint(1000, 1500) # The number of nodes
    k = 10  # Number of nearest neighbors in the ring topology
    p = 0.1 # The probability of rewiring each edge

    G = nx.connected_watts_strogatz_graph(n, k, p)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40, 80)
        weight = round(weight / 100, 2)
        if beta:
            weight = beta
        G[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    toJSON(G)
    toAdjMatrix(G)
    
    return G, config

def BA():
    g = nx.barabasi_albert_graph(1000, 5)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        g[a][b]['weight'] = weight
        config.add_edge_configuration("threshold", (a, b), weight)

    return g, config

def ER():

    g = nx.erdos_renyi_graph(5000, 0.002)

    while nx.is_connected(g) == False:
        g = nx.erdos_renyi_graph(5000, 0.002)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def CiteSeer():
    dataset = Planetoid(root='./Planetoid', name='CiteSeer')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def PubMed():
    dataset = Planetoid(root='./Planetoid', name='PubMed')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def Cora():
    dataset = Planetoid(root='./Planetoid', name='Cora')  # Cora, CiteSeer, PubMed
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)

    c = max(nx.connected_components(G), key=len)
    g = G.subgraph(c).copy()
    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(40,80)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def photo():

    dataset = ds.Amazon(root='./geo', name = 'Photo')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def coms():

    dataset = ds.Amazon(root='./geo', name = 'Computers')
    data = dataset[0]
    edges = (data.edge_index.numpy()).T.tolist()
    G = nx.from_edgelist(edges)
    g = nx.convert_node_labels_to_integers(G, first_label=0, ordering='default', label_attribute=None)

    config = mc.Configuration()

    for a, b in g.edges():
        weight = random.randrange(5,20)
        weight = round(weight / 100, 2)
        config.add_edge_configuration("threshold", (a, b), weight)
        g[a][b]['weight'] = weight

    return g, config

def run_and_save_sir_model(graph_func, graph_name, run_number, graph_args=[], beta=0.1, gamma=0.1, steps=10):
    G, config = graph_func(*graph_args)

    # Model selection
    model = ep.SIRModel(G)

    # Model Configuration
    config = mc.Configuration()
    config.add_model_parameter('beta', beta)
    config.add_model_parameter('gamma', gamma)

    # Set the initial infected node using a fixed seed for consistency
    random.seed(42)  # Fixed seed
    # Select the node with the highest degree
    initial_infected = max(G, key=G.degree)
    config.add_model_initial_configuration("Infected", [initial_infected])

    model.set_initial_status(config)

    # Simulation execution
    iterations = model.iteration_bunch(steps)

    # Write only infected nodes at each iteration to a file
    with open(f'infected_nodes_{graph_name}_run{run_number}.txt', 'w') as file:
        file.write(f"{graph_name} run {run_number} - Infected nodes per iteration:\n")
        for iteration in iterations:
            infected_nodes = [node for node, status in iteration['status'].items() if status == 1]
            file.write(f"Iteration {iteration['iteration']} - Infected nodes: {infected_nodes}\n")

    # Write iterations to a file
    with open(f'iterations_{graph_name}_run{run_number}.txt', 'w') as file:
        file.write(f"{graph_name} iterations:\n")
        for iteration in iterations:
            file.write(str(iteration) + "\n")

    # Update the graph with the status from the last iteration
    for i, node_status in model.status.items():
        G.nodes[i]['status'] = node_status

    # Node colors based on status
    status_colors = {0: 'green', 1: 'red', 2: 'blue'}
    colors = [status_colors[node[1]['status']] for node in G.nodes(data=True)]

    # Draw the graph
    pos = nx.spring_layout(G)
    nx.draw(G, pos, node_color=colors, with_labels=False, node_size=20)

    # Save the plot with run number in the filename
    plt.savefig(f'graph_infected_state_{graph_name}_run{run_number}.png', format='PNG')
    plt.close()

# List of graph functions, their names, and specific arguments
graphs = [
    (connSW, "connSW", [0.1]),  # connSW requires beta value
    # (BA, "BA", []),
    # (ER, "ER", []),
    # (CiteSeer, "CiteSeer", []),
    # (PubMed, "PubMed", []),
    # (Cora, "Cora", []),
    # (photo, "photo", []),
    # (coms, "coms", [])
]

# Run and save for each graph type 20 times
for graph_func, graph_name, graph_args in graphs:
    for run_number in range(1, 21):  # Run 20 times
        run_and_save_sir_model(graph_func, graph_name, run_number, graph_args)
