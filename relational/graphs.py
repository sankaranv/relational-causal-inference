import networkx as nx
import pandas as pd

from causal_structure import RelationalCausalStructure
from data import RelationalSkeleton
from utils import InstanceNode

def create_adj_mat_dict(structure: RelationalCausalStructure, skeleton: RelationalSkeleton) -> dict:
    """ Creates adjacency matrices based on the relational skeleton

    Args:
        structure (RelationalCausalStructure): 
        skeleton (RelationalSkeleton): 

    Returns:
        dict: contains an adjacency matrix (pd.DataFrame) for each relationship class
    """
    
    adj_mat_dict = {}
    for relation_name, entity_edge in structure.schema.relations.items():
        num_entity1 = len(skeleton.entity_instances[entity_edge[0]]["names"])
        num_entity2 = len(skeleton.entity_instances[entity_edge[1]]["names"])
        adj_mat = pd.DataFrame([[False] * num_entity2] * num_entity1)
        adj_mat.index = skeleton.entity_instances[entity_edge[0]]["names"]
        adj_mat.columns = skeleton.entity_instances[entity_edge[1]]["names"]
        for instance_edge in skeleton.relationship_instances[relation_name]:
            adj_mat.loc[instance_edge[0], instance_edge[1]] = True
        adj_mat_dict[relation_name] = adj_mat
    return adj_mat_dict

def get_node_name(instance: str, attribute: str) -> str:
    """ Returns node name for building ground graphs instance.attribute
        Naming convention is instance.attribute 

    Args:
        instance (str): instance name
        attribute (str): attribute name

    Returns:
        str: node name
    """
    return '.'.join([instance, attribute])

def create_ground_graph(structure: RelationalCausalStructure, skeleton: RelationalSkeleton) -> nx.DiGraph:
    """ Creates an abstract ground graph for the given relational dataset

    Args:
        structure (RelationalCausalStructure): contains schema and edges
        skeleton (RelationalSkeleton): contains all instances

    Returns:
        nx.DiGraph: the abstract ground graph
    """
    # Set up nodes in ground graph and save attribute values in each node
    # There will be one node for each (entity instance, attribute name) pair
    ground_graph = nx.DiGraph()
    for entity in skeleton.entity_instances:
        attributes = structure.schema.attribute_classes[entity]  
        for idx, instance_name in enumerate(skeleton.entity_instances[entity]["names"]):
            for attribute_name in attributes:
                node_name = get_node_name(instance_name,attribute_name)
                attribute_value = skeleton.entity_instances[entity][attribute_name][idx]
                ground_graph.add_node(node_name, val = attribute_value)

    # Set up self edges
    if "self" in structure.edges:
        edge_list = structure.edges["self"]
        for self_edge in edge_list:
            if self_edge.parent.entity != self_edge.child.entity:
                print("Edge is marked as a self-edge in skeleton but is between different entities")
                break
            else:
                for instance_name in skeleton.entity_instances[self_edge.parent.entity]["names"]:
                   parent_node_name = get_node_name(instance_name,self_edge.parent.attribute)
                   child_node_name = get_node_name(instance_name,self_edge.child.attribute)
                   ground_graph.add_edge(parent_node_name, child_node_name) 

    # Set up all other edges
    for relation_type, edge_list in skeleton.relationship_instances.items():
        for instance_edge in edge_list:
            # Add all edges in ground graph corresponding to each edge in the relational skeleton
            entity_0 = skeleton.get_instance_type(instance_edge[0])
            entity_1 = skeleton.get_instance_type(instance_edge[1])
            # Add edges between entities
            for relational_edge in structure.edges[relation_type]:
                if relational_edge.parent.entity == entity_0 and relational_edge.child.entity == entity_1:
                    parent_node_name = get_node_name(instance_edge[0],relational_edge.parent.attribute)
                    child_node_name = get_node_name(instance_edge[1],relational_edge.child.attribute)
                    ground_graph.add_edge(parent_node_name, child_node_name)
                # Don't forget to consider the opposite direction, relational edges are not necessarily directed
                if relational_edge.parent.entity == entity_1 and relational_edge.child.entity == entity_0:
                    parent_node_name = get_node_name(instance_edge[1],relational_edge.parent.attribute)
                    child_node_name = get_node_name(instance_edge[0],relational_edge.child.attribute)
                    ground_graph.add_edge(parent_node_name, child_node_name)

    return ground_graph

def create_subgraph_for_ITE(ground_graph: nx.DiGraph, treatment: InstanceNode, outcome: InstanceNode, cutoff = 10) -> nx.DiGraph:
    """ Obtain all nodes on the path between treatment and outcome in the abstract ground graph

    Args:
        ground_graph (nx.DiGraph): abstract ground graph
        treatment (InstanceNode): an (entity, attribute, instance) tuple of strings
        outcome (InstanceNode): an (entity, attribute, instance) tuple of strings
        cutoff (int, optional): max length of paths considered. Defaults to 10.

    Returns:
        nx.DiGraph: a subgraph containing all nodes on paths between treatment and outcome
    """
    source = get_node_name(treatment.instance, treatment.attribute)
    target = get_node_name(outcome.instance, outcome.attribute)
    subgraph = nx.DiGraph()
    if nx.has_path(ground_graph, source, target):
        for path in nx.all_simple_edge_paths(ground_graph, source, target, cutoff):
            for edge in path:
                subgraph.add_edge(*edge)
    else:
        print(f"No directed path from {source} to {target}")
    return subgraph