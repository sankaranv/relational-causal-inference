import json
from utils import Node, Edge
from schema import RelationalSchema

class RelationalCausalStructure:
    """
    Defines a causal model structure over a relational schema
    """
    def __init__(self, schema, edges = None) -> None:
        
        # Store the relational schema
        self.schema = schema

        # Create node set from schema
        self.nodes = set()
        for entity in self.schema.entity_classes:
            for attribute in self.schema.attribute_classes[entity]:
                self.nodes.add(Node(entity, attribute))

        self.edges = {} if edges is None else edges
        self.parents = {}
        self.incoming_edges = self.create_incoming_edges_dict()

    def add_edge(self, relation, node_from, node_to):
        """Adds edge to the relational causal structure

        Args:
            relation (str): a relation in the schema
            node_from (Node): named tuple with the form (entity, attribute)
            node_to (Node): named tuple with the form (entity, attribute)
        """

        # Convert tuples to named tuples if needed
        if isinstance(node_from, tuple):
            node_from = Node(*node_from)
        if isinstance(node_to, tuple):
            node_to = Node(*node_to)

        # Check if relation, entities, and attributes are in the schema
        if relation.lower() != "self" and relation not in self.schema.relationship_classes:
            print(f"Relation {relation} not in schema")
        elif node_from.entity not in self.schema.entity_classes:
            print(f"Entity {node_from.entity} not in schema")
        elif node_to.entity not in self.schema.entity_classes:
            print(f"Entity {node_to.entity} not in schema")
        elif node_from.attribute not in self.schema.attribute_classes[node_from.entity]:
            print(f"Attribute {node_from.attribute} of entity {node_from.entity} not in schema")
        elif node_to.attribute not in self.schema.attribute_classes[node_to.entity]:
            print(f"Attribute {node_to.attribute} of entity {node_to.entity} not in schema")

        # Check if relations are valid
        elif relation.lower() == "self" and node_from.entity != node_to.entity:
            print(f"Self relation between {node_from.entity} and {node_to.entity} is not possible")
        elif node_from.entity not in self.schema.relations[relation] or node_to.entity not in self.schema.relationships[relation]:
            print(f"Relation {relation} not valid between {node_from.entity} and {node_to.entity}")

        else:

            # Add edge to the edge list
            if relation not in self.edges:
                self.edges[relation] = set()
            self.edges[relation].add(Edge(node_from, node_to))

            # Update the list of parents
            if node_to not in self.parents:
                self.parents[node_to] = set()
            if node_from not in self.parents:
                self.parents[node_from] = set()
            self.parents[node_to].add(node_from)

    def load_edges_from_file(self, path_to_json):
        """Loads edge set from a JSON file

        Args:
            path_to_json (str): location of the JSON file
        """
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
        """Saves edge set to a JSON file

        Args:
            path_to_json (str): location of the JSON file
        """

        # Convert sets to lists for JSON serialization
        edges = {}
        for relation, edge_list in self.edges.items():
            edges[relation] = []
            for edge in edge_list:
                edges[relation].append([list(edge.parent), list(edge.child)])

        with open(path_to_json, 'w') as f:
            json.dump(edges, f, indent=4)

    def create_incoming_edges_dict(self):
        """ Collect the list of incoming edges to each attribute of each entity

        Returns:
            dict: key is [entity_name][attribute_name] and value is a list of (relation, edge) tuples
        """
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
        """ 
        Get the list of incoming edges to an attribute of an entity
        """
        return self.incoming_edges[entity_name][attribute_name]

if __name__ == "__main__":
    schema = RelationalSchema()
    schema.load_from_file('example/covid_schema.json')
    structure = RelationalCausalStructure(schema)

    # Create structure from COVID example in dissertation draft
    structure.add_edge("self", ("town", "policy"), ("town", "prevalence"))
    structure.add_edge("contains", ("state", "policy"), ("town", "policy"))
    structure.add_edge("contains", ("state", "policy"), ("town", "prevalence"))
    structure.add_edge("resides", ("town", "policy"), ("business", "occupancy"))
    structure.add_edge("resides", ("business", "occupancy"), ("town", "prevalence"))
    
    # Check parents
    for node in structure.parents:
        print(tuple(node), list([tuple(x) for x in structure.parents[node]]))

    # Save to file
    structure.save_edges_to_file('example/covid_structure.json')
