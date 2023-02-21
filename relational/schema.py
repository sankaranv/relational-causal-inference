import json
from collections import namedtuple 
import torch
import numpy as np
import pandas as pd
import networkx as nx

class RelationalSchema:
    """
    Relational Schema
    """    
    def __init__(self) -> None:
        self.empty_schema()

    def empty_schema(self):

        self.entity_classes = [] # each entry is a name
        self.relationship_classes = [] # each entry is a dict with keys left and right
        self.attribute_classes = {} # each key is an entity/relationship class and each value is a set of attribute names
        self.cardinality = {} # each key is [relationship class][entity class] and value is 'one' or 'many'
        self.relations = {} # each key is a relationship class and value is an (entity class, entity class) tuple    

    def is_valid_schema(self):
        for entity in self.entity_classes:
            if entity not in self.attribute_classes or not isinstance(self.attribute_classes[entity], list):
                return False
        for relation in self.relationship_classes:
            if relation not in self.cardinality:
               return False
            else:
                for entity in self.cardinality[relation]:
                    if entity not in self.entity_classes or self.cardinality[relation][entity] not in ['one', 'many']:
                        return False
        return True

    def add_entity(self, entity_name, attributes = None):
        """
        Add an entity to the schema
        """
        self.entity_classes.append(entity_name)
        self.attribute_classes[entity_name] = []
        if attributes is not None:
            if isinstance(a, list):
                self.attribute_classes.extend(attributes)
            elif isinstance(attributes, str):
                self.attribute_classes.append(attributes)
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
                self.attribute_classes.extend(attributes)
            elif isinstance(attributes, str):
                self.attribute_classes.append(attributes)
            else:
                print("Attributes should be a list or single str")

        def load_from_file(self, path_to_json):
        with open(path_to_json, 'r') as f:
            schema_dict = json.load(f)
        self.entity_classes = schema_dict["entity_classes"]
        self.relationship_classes = schema_dict["relationship_classes"]
        self.attribute_classes = schema_dict["attribute_classes"]
        self.cardinality = schema_dict["cardinality"]
        self.relations = schema_dict["relations"]
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
