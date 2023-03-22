from relational.causal_structure import RelationalCausalStructure
from relational.schema import RelationalSchema
from typing import Any
from copy import deepcopy
import json

class RelationalSCM:

    def __init__(self) -> None:

        self.observed_nodes = set()
        self.unobserved_nodes = set()
        self.functions = {}

    def load(self, path_to_json: str):
        """Load an SCM from file

        Args:
            path_to_json (str): path to the JSON file
        """
        with open(path_to_json) as f:
            scm = json.load(f)
            self.observed_nodes = set(scm["observed_nodes"])
            self.unobserved_nodes = set(scm["unobserved_nodes"])
            self.functions = {}
            for node, parents in scm["functions"]:
                self.functions[node] = set(parents)

    def load_structure(self, structure: RelationalCausalStructure):
        """ Build a relational SCM from a given relational causal structure

        Args:
            structure (RelationalCausalStructure): causal structure to load
        """

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

    def save(self, path_to_json: str):
        """ Save the SCM to a json file

        Args:
            path_to_json (str): path to the json file
        """
        scm_dict = {}
        scm_dict["observed_nodes"] = list(self.observed_nodes)
        scm_dict["unobserved_nodes"] = list(self.unobserved_nodes)
        scm_functions = {}
        for node, parents in self.functions.items():
            scm_functions[node] = list(parents)
        scm_dict["functions"] = scm_functions

        with open(path_to_json, 'w') as f:
            json.dump(scm_dict, f, indent=4)