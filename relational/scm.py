from causal_structure import RelationalCausalStructure
from schema import RelationalSchema
from typing import Any
from copy import deepcopy

class RelationalSCM:

    def __init__(self, structure: RelationalCausalStructure) -> None:

        # Save relational causal structure
        self.structure = structure

        # Create set of symbols (strings) for each node in structure
        self.observed_nodes = set([self.get_name_from_node(node) for node in structure.nodes])

        # Add unobserved noise terms for each node in structure
        self.unobserved_nodes = set([f"noise_{self.get_name_from_node(node)}" for node in structure.nodes])

        # Create set of equations for each node as a function of its parents and an exogenous noise term
        self.functions = {}
        for node in structure.nodes:
            node_parents = set([self.get_name_from_node(parent) for parent in structure.parents[node]])
            node_parents.add(f"noise_{self.get_name_from_node(node)}")
            self.functions[self.get_name_from_node(node)] = node_parents
    
    def get_name_from_node(self, node):
        """Returns a string of the form entity_attribute from node tuples

        Args:
            node (Node): named tuple with the form (entity, attribute)

        Returns:
            str: name of the node
        """
        return f"{node.entity}_{node.attribute}"

    def intervene(self, node_name: str, value: float):
        """ Return a new SCM with the given node set to the given value and all parents removed

        Args:
            node (str): name of the node to intervene on, which will be an attribute of an entity
            value (float): value to set the node to
        """

        intervened_scm = deepcopy(self)

        # Remove the exogenous noise term for the given node
        intervened_scm.unobserved_nodes.remove(f"noise_{node_name}")

        # Remove all parents of the given node and only assign the given value
        intervened_scm.functions[node_name] = set([value])

        return intervened_scm

    def intervene_(self, node_name: str, value: float):
        """ Intervene in place on the given SCM

        Args:
            node (str): name of the node to intervene on, which will be an attribute of an entity
            value (float): value to set the node to
        """

        # Remove the exogenous noise term for the given node
        self.unobserved_nodes.remove(f"noise_{node_name}")

        # Remove all parents of the given node and only assign the given value
        self.functions[node_name] = set([value])

if __name__ == "__main__":

    # Load schema and structure
    schema = RelationalSchema()
    schema.load_from_file('example/covid_schema.json')
    structure = RelationalCausalStructure(schema)
    structure.load_edges_from_file('example/covid_structure.json')

    # Create SCM
    scm = RelationalSCM(structure)
    intervened_scm = scm.intervene("town_policy", 10)
    print(intervened_scm.functions)
    intervened_scm.intervene_("town_prevalence", 20)