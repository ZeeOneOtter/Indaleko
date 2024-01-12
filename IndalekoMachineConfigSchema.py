'''
This module defines the database schema for the MachineConfig collection.
'''
import json

from IndalekoRecordSchema import IndalekoRecordSchema

class IndalekoMachineConfigSchema(IndalekoRecordSchema):
    '''Define the schema for use with the MachineConfig collection.'''

    @staticmethod
    def get_schema():

        machine_config_schema = {
            '''
            This schema relates to the machine configuration collection,
            which captures meta-data about the machine where the data was indexed.
            '''
            "$schema": "https://json-schema.org/draft/2020-12/schema#",
            "$id": "https://activitycontext.work/schema/machineconfig.json",
            "title": "Data source schema",
            "description": "This schema describes information about the machine where the data was indesxed.",
            "type": "object",
            "rule" : {
                "Platform" : {
                    "type" : "object",
                    "properties" : {
                        "software" : {
                            "type" : "object",
                            "properties" : {
                                "OS" : {
                                    "type" : "string",
                                    "description" : "Name of the software.",
                                },
                                "Version" : {
                                    "type" : "string",
                                    "description" : "Version of the software.",
                                },
                            },
                            "required" : ["OS", "version"],
                        },
                        "hardware" : {
                            "type" : "object",
                            "properties" : {
                                "CPU" : {
                                    "type" : "string",
                                    "description" : "Processor Architecture.",
                                },
                                "Version" : {
                                    "type" : "string",
                                    "description" : "Version of the hardware.",
                                },
                            },
                            "required" : ["CPU", "version"],
                        },
                    },
                },
                "Captured" : {
                    "type" : "object",
                    "properties" : {
                        "Label" : {
                            "type" : "string",
                            "description" : "UUID representing the semantic meaning of this timestamp.",
                            "format": "uuid",
                        },
                        "Value" : {
                            "type" : "string",
                            "description" : "Timestamp in ISO date and time format.",
                            "format" : "date-time",
                        },
                    },
                    "required" : ["Label", "Value"],
                },
                "required" : ["Captured"],
            }
        }
        assert 'Record' not in machine_config_schema['rule'], \
            'Record should not be in machine config schema.'
        machine_config_schema['rule']['Record'] = IndalekoRecordSchema.get_schema()['rule']
        machine_config_schema['rule']['required'].append('Record')
        return machine_config_schema

def main():
    """Test the IndalekoMachineConfigSchema class."""
    if IndalekoMachineConfigSchema.is_valid_schema(IndalekoMachineConfigSchema.get_schema()):
        print('Schema is valid.')
    print(json.dumps(IndalekoMachineConfigSchema.get_schema(), indent=4))

if __name__ == "__main__":
    main()
