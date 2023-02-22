import json
import torch

class RelationalSkeleton:
    """
    Relational Skeleton
    """
    def __init__(self, schema) -> None:
        self.empty_skeleton(schema)

    def empty_skeleton(self, schema):
        self.entity_instances = {}
        self.relationship_instances = {}
        for entity in schema.entity_classes:
            self.entity_instances[entity] = {"names": []}
            for attribute in schema.attribute_classes[entity]:
                self.entity_instances[entity][attribute] = []
        for relation in schema.relationship_classes:
            self.relationship_instances[relation] = []
        self.instance_type = {}

    def get_instance_type(self, instance):
        return self.instance_type[instance]

    def load_from_file(self, schema, path_to_json):
        with open(path_to_json, 'r') as f:
            skeleton_dict = json.load(f)
        self.entity_instances = skeleton_dict["entity_instances"]
        for entity in self.entity_instances:
            # Save entity types for all entities
            for name in self.entity_instances[entity]["names"]:
                self.instance_type[name] = entity
        self.relationship_instances = skeleton_dict["relationship_instances"]
        for relation in self.relationship_instances:
            self.relationship_instances[relation] = [tuple(e) for e in self.relationship_instances[relation]]
        if not self.is_valid_skeleton(schema):
            print("Skeleton is invalid for the given schema, could not load from file")
            self.empty_skeleton(schema)

    def save_to_file(self, schema, path_to_json):
        if self.is_valid_skeleton(schema):
            skeleton_dict = {
                "entity_instances": self.entity_instances,
                "relationship_instances": self.relationship_instances
            }
            with open(path_to_json, 'w') as f:
                json.dump(skeleton_dict, f)
        else:
            print("Skeleton is invalid for the given schema, could not write to file")                

    def is_valid_skeleton(self, schema):
        for entity in schema.entity_classes:
            if entity not in self.entity_instances or not isinstance(self.entity_instances[entity], dict):
                print(f"Entity {entity} in the schema is missing in the skeleton")
                return False
            if "names" not in self.entity_instances[entity]:
                print(f"Names are missing for entity {entity}")
                return False
            for attribute in schema.attribute_classes[entity]:
                if attribute not in self.entity_instances[entity]:
                    print(f"Attribute {entity}.{attribute} in the schema is missing in the skeleton")
                    return False
                if not isinstance(self.entity_instances[entity][attribute], list):
                    print(f"Values of {entity}.{attribute} are not in a list or missing")
                    return False
                if len(self.entity_instances[entity][attribute]) != len(self.entity_instances[entity]["names"]):
                    print(f"Number of values of {entity}.{attribute} are not equal to the number of instance names")
                    return False
        all_instance_names = self.instance_type.keys()
        for relation in schema.relationship_classes:
            if relation not in self.relationship_instances or not isinstance(self.relationship_instances[relation], list):
               return False
            else:
                for item in self.relationship_instances[relation]:
                    if not isinstance(item, tuple) or item[0] not in all_instance_names or item[1] not in all_instance_names:
                        return False
        return True

    def get_attribute_vector(self, entity: str, attribute: str) -> torch.Tensor:
        """ Obtain list of instances of given attribute in given entity

        Args:
            entity (str): entity name
            attribute (str): attribute name

        Returns:
            torch.Tensor: list of all instances of given attribute in the given entity
        """
        attribute_instances = self.entity_instances[entity][attribute]
        return torch.Tensor(attribute_instances)