
import networkx as nx
import collections
import os
import csv

Node = collections.namedtuple("Node", ["id", "label", "country"])
Edge = collections.namedtuple("Edge", ["source", "target", "weight"])


def get_all_nodes_and_labels(nodes):
    list_of_nodes = set()
    for line in nodes:
        line_str = line.strip("\n").split(",")
        node = Node(id=line_str[0], label=line_str[1], country=line_str[3])
        list_of_nodes.add(node)
    return list_of_nodes


def get_all_edges(edge_list, use_num_players):
    all_edges = set()
    for edge_line in edge_list:
        edge_line_str = edge_line.strip("\n").split(",")
        if use_num_players:
            weight_index = 7
        else:
            weight_index = 8
        edge = Edge(source=edge_line_str[0], target=edge_line_str[1], weight=edge_line_str[weight_index])
        all_edges.add(edge)
    return all_edges


def make_node_country_dict(nodes):
    node_country = {}
    for node in nodes:
        node_country[node.id] = node.country
    return node_country


def calculate_intc_for_country(country, nodes_dict, edges):
    country_indegree_sum = 0
    internal_sum = 0
    for edge in edges:
        source_country = nodes_dict[edge.source]
        target_country = nodes_dict[edge.target]
        if target_country == country:
            #update weighted in-degree sum for country
            country_indegree_sum += float(edge.weight)
            #update sum of internal transfers for country
            if source_country == country:
                internal_sum += float(edge.weight)
    return [internal_sum/country_indegree_sum, internal_sum, country_indegree_sum]


def calculate_rita_for_country(country, nodes_dict, edges):
    sum_all_edges = 0
    internal_sum = 0
    for edge in edges:
        source_country = nodes_dict[edge.source]
        target_country = nodes_dict[edge.target]
        sum_all_edges += float(edge.weight)
        #if source and target are the country we are interested in, then update internal sum
        if target_country == country and source_country == country:
            internal_sum += float(edge.weight)
    return [internal_sum/sum_all_edges, internal_sum]


def calculate_intc(countries, node_country_map, edges):
    dictionary_of_results = {}
    for each_country in countries:
        dictionary_of_results[each_country] = calculate_intc_for_country(each_country, node_country_map, edges)
    return dictionary_of_results


def calculate_rita(countries, node_country_map, edges):
    dictionary_of_results = {}
    for each_country in countries:
        dictionary_of_results[each_country] = calculate_rita_for_country(each_country, node_country_map, edges)
    return dictionary_of_results


def make_graph(nodes, edge_list):
    G = nx.DiGraph()
    for node in nodes:
        G.add_node(node.id, country=node.country)
    for edge in edge_list:
        G.add_edge(u_of_edge=edge.source, v_of_edge=edge.target, weight=float(edge.weight))
    return G

def write_intc_num_players(results):
    file_path = "../results/intc_num_players.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
        headings = ["country", "intc_value", "total_num_transfers_within_country",
                    "total_num_transfers_by_nodes_in_country"]
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headings)
        for result in results:
            row_data = [result]
            for value in results[result]:
                row_data.append(str(value))
            writer.writerow(row_data)


def write_rita_num_players(results):
    file_path = "../results/rita_num_players.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
        headings = ["country", "rita_value", "total_num_transfers_within_country"]
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headings)
        for result in results:
            row_data = [result]
            for value in results[result]:
                row_data.append(str(value))
            writer.writerow(row_data)


def write_intc_total_amount(results):
    file_path = "../results/intc_total_amount.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
        headings = ["country", "intc_value", "total_normalised_amount_within_country",
                    "total_in_degree_all_nodes_in_country"]
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headings)
        for result in results:
            row_data = [result]
            for value in results[result]:
                row_data.append(str(value))
            writer.writerow(row_data)


def write_rita_total_amount(results):
    file_path = "../results/rita_total_amount.csv"
    if os.path.exists(file_path):
        os.remove(file_path)
    with open(file_path, 'w', newline='\n', encoding='utf-8') as file:
        headings = ["country", "rita_value", "total_normalised_amount_spent_within_country"]
        writer = csv.writer(file, delimiter=',')
        writer.writerow(headings)
        for result in results:
            row_data = [result]
            for value in results[result]:
                row_data.append(str(value))
            writer.writerow(row_data)

germany = "Germany"
england = "England"
france = "France"
italy = "Italy"
spain = "Spain"
portugal = "Portugal"
belgium = "Belgium"
russia = "Russia"
ukraine = "Ukraine"
netherlands = "Netherlands"
turkey = "Turkey"
austria = "Austria"
greece = "Greece"
croatia = "Croatia"
czech_republic = "Czech Republic"
countries = [germany, england, france, italy, spain, portugal, belgium, russia, ukraine, netherlands,
             turkey, austria, greece, croatia, czech_republic]


file_nodes = open("../data/non_loan_num_players_degree_data_vs_normalized_amount_degree_data.csv", "r", encoding="utf-8")
file_edges = open("../data/non_loan_num_players_degree_data_vs_normalized_amount_degree_data_edges_table.csv", "r", encoding="utf-8")
node_data = file_nodes.readlines()
edge_data = file_edges.readlines()
all_nodes = get_all_nodes_and_labels(node_data[1:]) #ignore first line of file
nodes_country_dict = make_node_country_dict(all_nodes) #map each node to its country


all_edges_num_players = get_all_edges(edge_data[1:], use_num_players=True)
all_edges_amount = get_all_edges(edge_data[1:], use_num_players=False) #use amounts as weight
num_players_intra_national_trade_coefficient_vals = calculate_intc(countries, nodes_country_dict, all_edges_num_players)
num_players_relative_internal_trade_activity_vals = calculate_rita(countries, nodes_country_dict, all_edges_num_players)
normalised_amount_intra_national_trade_coeffient_vals = calculate_intc(countries, nodes_country_dict, all_edges_amount)
normalised_amount_relative_internal_trade_activity_vals = calculate_rita(countries, nodes_country_dict, all_edges_amount)
G_num_players = make_graph(all_nodes, all_edges_num_players)
G_amount = make_graph(all_nodes, all_edges_amount)
write_intc_num_players(num_players_intra_national_trade_coefficient_vals)
write_rita_num_players(num_players_relative_internal_trade_activity_vals)
write_intc_total_amount(normalised_amount_intra_national_trade_coeffient_vals)
write_rita_total_amount(normalised_amount_relative_internal_trade_activity_vals)
print("===============printing INTC values num_players================")
for country in num_players_intra_national_trade_coefficient_vals:
    print(country, num_players_intra_national_trade_coefficient_vals[country])
print("==========printing RITA values num players==============")
for country in num_players_relative_internal_trade_activity_vals:
    print(country, num_players_relative_internal_trade_activity_vals[country])
print("============printing INTC values money===============")
for country in normalised_amount_intra_national_trade_coeffient_vals:
    print(country, normalised_amount_intra_national_trade_coeffient_vals[country])
print("=================printing RITA values money=============")
for country in normalised_amount_relative_internal_trade_activity_vals:
    print(country, normalised_amount_relative_internal_trade_activity_vals[country])

print(len(G_amount.nodes))
print(len(G_amount.edges))
print(len(G_num_players.nodes))
print(len(G_num_players.edges))
print(nx.attribute_assortativity_coefficient(G_num_players, attribute="country"))
