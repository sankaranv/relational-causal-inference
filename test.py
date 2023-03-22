from relational import *

if __name__ == "__main__":

    ##### Test relational schema
    print("Testing relational schema \n")

    schema = RelationalSchema()
    schema.add_entity("state", "policy")
    schema.add_entity("town", ["prevalence", "policy"])
    schema.add_entity("business")
    schema.add_attribute("business", "occupancy")
    schema.add_relation("contains", "state", "town", "one_to_many")
    schema.add_relation("resides", "town", "business", "one_to_many")
    print(f"Checking if schema is valid: {schema.is_valid_schema()}")
    print(f"Entities: {schema.entity_classes}")
    print(f"Relationships: {schema.relationship_classes}")
    print(f"Attributes: {schema.attribute_classes}")
    print(f"Cardinality: {schema.cardinality}")
    print(f"Relations: {schema.relations}")
    schema.save('example/covid_schema.json') 

    ##### Test relational causal structure
    print("\nTesting relational causal structure \n")

    schema = RelationalSchema()
    schema.load('example/covid_schema.json')
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
    structure.save('example/covid_structure.json')

    ##### Test relational SCM
    print("\nTesting relational SCM \n")

    # Load schema and structure
    schema = RelationalSchema()
    schema.load('example/covid_schema.json')
    structure = RelationalCausalStructure(schema)
    structure.load('example/covid_structure.json')

    # Create SCM
    scm = RelationalSCM()
    scm.load_structure(structure)
    intervened_scm = scm.intervene("town_policy", 10)
    print(intervened_scm.functions)
    intervened_scm.intervene_("town_prevalence", 20)
