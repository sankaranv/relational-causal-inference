from relational import *

if __name__ == "__main__":

    print("\nTesting relational SCM \n")

    # Load schema and structure
    schema = RelationalSchema()
    schema.load('example/covid_schema.json')
    structure = RelationalCausalStructure(schema)
    structure.load('example/covid_structure.json')

    # Create SCM
    scm = RelationalSCM()
    scm.create_from_structure(structure)

    # Intervene and create copy
    town_policy = 10
    intervened_scm = scm.intervene("town_policy", town_policy)
    assert len(intervened_scm.functions["town_policy"]) == 1, "Intervention should remove all parents of town_policy"
    assert 10 in intervened_scm.functions["town_policy"], f"Intervention attempted to set town_prevalence to {town_policy} but value found was {intervened_scm.functions['town_policy']}"
    assert 10 not in scm.functions["town_policy"], "Intervention should create a copy of the SCM and not modify the original"
    
    # Intervene in place
    town_prevalence = 20
    intervened_scm.intervene_("town_prevalence", town_prevalence)
    assert len(intervened_scm.functions["town_prevalence"]) == 1, "Intervention should remove all parents of town_prevalence"
    assert 20 in intervened_scm.functions["town_prevalence"], f"Intervention attempted to set town_prevalence to {town_prevalence} but value found was {intervened_scm.functions['town_prevalence']}"