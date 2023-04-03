from relational import *
import pyro
import funsor
import funsor.torch.distributions as dist
import funsor.ops as ops

# Funsor is just an alt backend to Pyro anyway
# In parallel, try writing a Pyro model that could benefit from symbolic reductions with Funsor - e.g. linear Gaussians
# Confirm that there is a real speedup that funsor is doing - so we know their symbolic reduction stuff is actually happening
# That will make it way easier to compile the relational model, since the built-in backend for Pyro is nicer to work with
# Compiler - probably just generating pyro functions from relational schemas and structures
# For example, you don't need to manually write every sample statement, just traverse the graph and add one every time you hit a new node
# A -> B -> C where each node is Gaussian, then try to marginalize B - funsor should be able to do this - then inspect the Tensor and try to figure out what it is

def relational_linear_gaussian_model(scm: RelationalSCM, num_instances: dict):
    """ Build a funsor model from the relational SCM

    Args:
        scm (RelationalSCM): relational SCM containing a set of structural functions
    """
    for node, parents in scm.functions.items():
        raise NotImplementedError

def parse_name(name):
    """Parse a name of the form entity_attribute into a tuple (entity, attribute)

    Args:
        name (str): name of the node

    Returns:
        str: type of node, either "var" or "noise"
        tuple: (entity, attribute)
    """
    split_name = tuple(name.split('.'))
    if len(split_name > 3) or len(split_name < 2):
        raise Exception("Invalid node name {name}")
    elif len(split_name) == 3 and split_name[0] != 'noise':
        return "noise", (split_name[1], split_name[2])
    else:
        return "var", split_name

if __name__ == "__main__":

    # Can improve API so that schema and structure do not need to be created every time
    # However this can introduce nightmares in verifying correctness, e.g. acyclicity and missing parents
    schema = RelationalSchema()
    schema.load('example/covid_schema.json')
    structure = RelationalCausalStructure(schema)
    structure.load('example/covid_structure.json')
    scm = RelationalSCM()
    scm.create_from_structure(structure)
    print(scm.functions)

    # Hardcoding the number of instances
    num_instances = {'state': 2, 'town': 3, 'business': 5}