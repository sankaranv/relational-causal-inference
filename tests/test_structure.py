from .relational import *

def test_structure():

    schema = RelationalSchema()
    schema.load('tests/example/covid_schema.json')
    structure = RelationalCausalStructure(schema)

    # Create structure from COVID example in dissertation draft
    structure.add_edge("self", ("town", "policy"), ("town", "prevalence"))
    structure.add_edge("contains", ("state", "policy"), ("town", "policy"))
    structure.add_edge("contains", ("state", "policy"), ("town", "prevalence"))
    structure.add_edge("resides", ("town", "policy"), ("business", "occupancy"))
    structure.add_edge("resides", ("business", "occupancy"), ("town", "prevalence"))
    
    ref_structure = RelationalCausalStructure(schema)
    ref_structure.load('tests/example/covid_structure.json')
    
    # Check parents
    for node in structure.parents:
        assert ref_structure.parents[node] == structure.parents[node], f"Parents of {node} don't match reference {ref_structure.parents[node]}"
