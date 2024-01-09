import argparse
import json
import os
from IndalekoRecord import IndalekoRecord
import msgpack


class IndalekoMachineConfig(IndalekoRecord):
    '''
    This is the generic class for machine config.  It should be used to create
    platform specific machine configuration classes.
    '''

    Schema = {
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
            "platform" : {
                "type" : "object",
                "properties" : {
                    "software" : {
                        "type" : "object",
                        "properties" : {
                            "OS" : {
                                "type" : "string",
                                "description" : "Name of the software.",
                            },
                            "version" : {
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
                            "version" : {
                                "type" : "string",
                                "description" : "Version of the hardware.",
                            },
                        },
                        "required" : ["CPU", "version"],
                    },
                },
            },
            "properties": {
                "source": {
                    "description": "This is the UUID of the given source for this metadata.",
                    "type": "string",
                    "format": "uuid"
                },
                "version": {
                    "description": "This is the version of the source provider. Versioning allows evolution of the data generated by the source.",
                    "type": "string",
                },
                "captured" : {
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
            },
            "required" : ["source", "version", "captured"],
        }
    }

    def __init__(self: 'IndalekoMachineConfig',
                 source : dict,
                 raw_data : bytes,

                 config_data : dict, test: bool = False) -> None:
        '''
        Constructor for the IndalekoMachineConfig class. Takes a
        set of configuration data as a parameter and initializes the object.
        '''




class IndalekoMachineConfig_old:
    '''
    This is the generic class for machine config.  It should be used to create
    platform specific machine configuration classes.
    '''

    Schema = {
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
            "platform" : {
                "type" : "object",
                "properties" : {
                    "software" : {
                        "type" : "object",
                        "properties" : {
                            "OS" : {
                                "type" : "string",
                                "description" : "Name of the software.",
                            },
                            "version" : {
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
                            "version" : {
                                "type" : "string",
                                "description" : "Version of the hardware.",
                            },
                        },
                        "required" : ["CPU", "version"],
                    },
                },
            },
            "properties": {
                "source": {
                    "description": "This is the UUID of the given source for this metadata.",
                    "type": "string",
                    "format": "uuid"
                },
                "version": {
                    "description": "This is the version of the source provider. Versioning allows evolution of the data generated by the source.",
                    "type": "string",
                },
                "captured" : {
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
            },
            "required" : ["source", "version", "captured"],
        }
    }

    def __init__(self: 'IndalekoMachineConfig',
                 config_data : bytes,
                 attributes: dict,
                 source: dict) -> None:
        '''
        Constructor for the IndalekoMachineConfig class. Takes a
        set of configuration data as a parameter and initializes the object.
        '''
        super().__init__(config_data, attributes, source)


    @staticmethod
    def load_config_from_file(**kwargs) -> dict:
        '''
        This method creates a new IndalekoMachineConfig object from an
        existing config file.
        '''
        if 'config_dir in kwargs':
            config_dir = kwargs['config_dir']
        if 'config_file' in kwargs:
            config_file = kwargs['config_file']
        assert config_file is not None, "No config file specified."
        if config_dir is not None:
            config_file = os.path.join(config_dir, config_file)
        assert(os.path.isfile(config_file)), f"Config file {config_file} does not exist."
        with open(config_file, 'rt', encoding='utf-8-sig') as fd:
            config_data = json.load(fd)
        # we don't have enough information here to build a valid record yet.
        return config_data

def main():
    print('No tests implemented for this class library.  Use a specialized library to test.')

if __name__ == "__main__":
    main()



