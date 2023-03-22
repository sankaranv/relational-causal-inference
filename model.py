from relational import *
import pyro
import funsor

def relational_linear_gaussian_model(scm):
    pass

if __name__ == "__main__":
    structure = RelationalCausalStructure()
    structure.load('example/covid_structure.json')
    scm = RelationalSCM(structure)
    print(scm.functions)