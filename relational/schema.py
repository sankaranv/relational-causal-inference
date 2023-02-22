import json

class RelationalSchema:
    """
    Relational Schema
    """    
    def __init__(self) -> None:
        self.empty_schema()

    def empty_schema(self):

        self.entity_classes = set() # each entry is a name
        self.relationship_classes = set() # each entry is a dict with keys left and right
        self.attribute_classes = {} # each key is an entity/relationship class and each value is a set of attribute names
        self.cardinality = {} # each key is [relationship class][entity class] and value is 'one' or 'many'
        self.relations = {} # each key is a relationship class and value is an (entity class, entity class) tuple 

    def add_entity(self, entity_name, attributes = None):
        """
        Add an entity to the schema
        """
        self.entity_classes.add(entity_name)
        self.attribute_classes[entity_name] = set()
        if attributes is not None:
            if isinstance(a, list):
                self.attribute_classes.update(attributes)
            elif isinstance(attributes, str):
                self.attribute_classes.add(attributes)
            else:
                print("Attributes should be a list or single str")
        
    def add_attribute(self, entity_name, attributes = None):
        """
        Add one or more attributes to an existing entity
        """        
        if entity_name not in self.entity_classes:
            print(f"Entity {entity_name} is not in the relational schema")
        else:
            if isinstance(a, list):
                self.attribute_classes.update(attributes)
            elif isinstance(attributes, str):
                self.attribute_classes.add(attributes)
            else:
                print("Attributes should be a list or single str") 

    def add_relation(self, relation, entity_from, entity_to, relation_type):
        """Add relation to the schema

        Args:
            relation (str): name for the relation
            entity_from (str): an entity class
            entity_to (str): an entity class
            relation_type (str): can be 'one_to_one', 'one_to_many', 'many_to_one', 'many_to_many'
        """
        valid_relation_types = ['one_to_one', 'one_to_many', 'many_to_one', 'many_to_many']

        # Check if entities exist in the schema
        if entity_from not in self.entity_classes:
            print(f"Entity {entity_from} is not in the relational schema, cannot add relation")
        elif entity_to not in self.entity_classes:
            print(f"Entity {entity_to} is not in the relational schema, cannot add relation")

        # Check if the relation is already present in the schema
        elif relation in self.relations:
            print(f"Relation {relation} already exists in the relational schema, cannot add relation")

        # Check if relation type is valid
        elif relation_type.lower() not in valid_relation_types:
            print(f"Relation type {relation_type} is not valid, should be in {valid_relation_types}")
        
        else:
            self.relations[relation] = [entity_from, entity_to]
            self.relationship_classes.add(relation)
            self.cardinality[relation] = {
                                          entity_from: relation_type.lower().split('_')[0], 
                                          entity_to: relation_type.lower().split('_')[2]
                                         } 

    def is_valid_schema(self):
        for entity in self.entity_classes:
            if entity not in self.attribute_classes or not isinstance(self.attribute_classes[entity], set):
                return False
        for relation in self.relationship_classes:
            if relation not in self.cardinality:
               return False
            else:
                for entity in self.cardinality[relation]:
                    if entity not in self.entity_classes or self.cardinality[relation][entity] not in ['one', 'many']:
                        return False
        return True

    def load_from_file(self, path_to_json):
        with open(path_to_json, 'r') as f:
            schema_dict = json.load(f)
        self.entity_classes = set(schema_dict["entity_classes"])
        self.relationship_classes = set(schema_dict["relationship_classes"])
        self.attribute_classes = schema_dict["attribute_classes"]
        self.cardinality = schema_dict["cardinality"]
        self.relations = schema_dict["relations"]
        for entity in self.attribute_classes:
            self.attribute_classes[entity] = set(self.attribute_classes[entity])
        for relation in self.relations:
            self.relations[relation] = tuple(self.relations[relation])
        if not self.is_valid_schema():
            print("Schema is invalid, could not load from file")
            self.empty_schema()

    def save_to_file(self, path_to_json):
        if self.is_valid_schema():
            schema_dict = {
                "entity_classes": list(self.entity_classes),
                "relationship_classes": list(self.relationship_classes),
                "attribute_classes": self.attribute_classes,
                "cardinality": self.cardinality,
                "relations": self.relations
            }
            with open(path_to_json, 'w') as f:
                json.dump(schema_dict, f)
        else:
            print("Schema is invalid, could not write to file")

if __name__ == "__main__":
    
    # Create relational schema
    schema = RelationalSchema()
    schema.load_from_file('example/covid_schema.json')
