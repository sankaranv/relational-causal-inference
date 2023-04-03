from .relational import *

def test_schema():

    schema = RelationalSchema()
    schema.add_entity("state", "policy")
    schema.add_entity("town", ["prevalence", "policy"])
    schema.add_entity("business")
    schema.add_attribute("business", "occupancy")
    schema.add_relation("contains", "state", "town", "one_to_many")
    schema.add_relation("resides", "town", "business", "one_to_many")
    
    # Check if schema is valid using the reference schema from file
    ref_schema = RelationalSchema()
    ref_schema.load('tests/example/covid_schema.json')
    assert schema.is_valid_schema(), "Schema is not valid"
    assert schema.entity_classes == ref_schema.entity_classes, f"Entity classes {schema.entity_classes} don't match reference {ref_schema.entity_classes}"
    assert schema.relationship_classes == ref_schema.relationship_classes, f"Relationship classes {schema.relationship_classes} don't match reference {ref_schema.relationship_classes}"
    assert schema.attribute_classes == ref_schema.attribute_classes, f"Attribute classes {schema.attribute_classes} don't match reference {ref_schema.attribute_classes}"
    assert schema.cardinality == ref_schema.cardinality, f"Cardinalities {schema.cardinality} don't match reference {ref_schema.cardinality}"
    assert schema.relations == ref_schema.relations, f"Relations {schema.relations} don't match reference {ref_schema.relations}"
