import json
from utils import Node, Edge

class RelationalCausalStructure:
    """
    Relational Causal Structure
    """
    def __init__(self, schema, edges = None) -> None:
        self.schema = schema
        self.edges = {} if edges is None else edges
        self.nodes = set()
        self.parents = {}
        self.incoming_edges = self.create_incoming_edges_dict()

    def add_edge(self, relation, node_from, node_to):
        pass

    def load_edges_from_file(self, path_to_json):
        with open(path_to_json, 'r') as f:
            self.edges = json.load(f)
        for relation in self.edges:
            for idx, edge_list in enumerate(self.edges[relation]):
                # Convert list representation of node from JSON to named tuple
                self.edges[relation][idx] = [Node(*node) for node in self.edges[relation][idx]]
                # Add nodes to node list
                self.nodes.update(self.edges[relation][idx])   
                # Convert list representation of edge to named tuple
                self.edges[relation][idx] = Edge(*self.edges[relation][idx])
                # Update parents dict
                edge = self.edges[relation][idx]
                if edge.child not in self.parents:
                    self.parents[edge.child] = [edge.parent]
                else:
                    self.parents[edge.child].append(edge.parent)
                if edge.parent not in self.parents:
                    self.parents[edge.parent] = []

    def save_edges_to_file(self, path_to_json):
        with open(path_to_json, 'w') as f:
            json.dump(self.edges, f)

    def create_incoming_edges_dict(self):
        # Key is [entity_name][attribute_name] and value is a list of (relation, edge) tuples
        incoming_edges = {}
        for entity, attributes in self.schema.attribute_classes.items():
            attribute_dict = {}
            for attribute in attributes:
                attribute_dict[attribute] = []
            incoming_edges[entity] = attribute_dict
        
        for relation, edge_list in self.edges.items():
            for edge in edge_list:
                incoming_edges[edge.child.entity][edge.child.attribute].append((relation, edge))
        return incoming_edges

    def get_incoming_edges(self, entity_name, attribute_name):
        return self.incoming_edges[entity_name][attribute_name]