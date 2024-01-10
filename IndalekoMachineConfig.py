import argparse
import json
import os
from IndalekoRecord import IndalekoRecord
from IndalekoCollections import IndalekoCollections
from IndalekoDBConfig import IndalekoDBConfig
from IndalekoMachineConfigSchema import IndalekoMachineConfigSchema
import datetime
import uuid

class IndalekoMachineConfig(IndalekoRecord):
    '''
    This is the generic class for machine config.  It should be used to create
    platform specific machine configuration classes.
    '''

    DefaultConfigDir = './config'
    IndalekoMachineConfig_UUID_str = '811c33bb-b7ce-4903-a441-1c2d228a38ec'
    IndalekoMachineConfig_version_str = '1.0.0'

    Schema = IndalekoMachineConfigSchema

    def __init__(self: 'IndalekoMachineConfig', timestamp : datetime = None, db : IndalekoDBConfig = None):
        '''
        Constructor for the IndalekoMachineConfig class. Takes a
        set of configuration data as a parameter and initializes the object.
        '''
        if timestamp is None:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        super().__init__(b'', {},
                        {
                            'Identifier' : IndalekoMachineConfig.IndalekoMachineConfig_UUID_str,
                            'Version' : IndalekoMachineConfig.IndalekoMachineConfig_version_str
                        })
        self.platform = {}
        self.captured = {
            'Label' : 'Timestamp',
            'Value' : timestamp,
        }
        collections = IndalekoCollections(db_config=db)
        self.collection = collections.get_collection('MachineConfig')
        assert self.collection is not None, 'MachineConfig collection does not exist.'

    def set_platform(self, platform : dict) -> None:
        '''
        This method sets the platform information for the machine.
        '''
        assert type(platform) is dict, f'platform must be a dict (not {type(platform)})'
        assert 'software' in platform, 'platform must contain a software field'
        assert type(platform['software']) is dict, f'platform["software"] must be a dictionary, not {type(platform["software"])}'
        assert type(platform['software']['OS']) is str, f'platform must contain a string OS field, not {type(platform["software"]["OS"])}'
        assert type(platform['software']['Version']) is str, 'platform must contain a string version field'
        assert type(platform['software']['Architecture']) is str, 'platform must contain a string architecture field'
        assert 'hardware' in platform, 'platform must contain a hardware field'
        assert type(platform['hardware']) is dict, 'platform["hardware"] must be a dictionary'
        assert type(platform['hardware']['CPU']) is str, 'platform must contain a string CPU field'
        assert type(platform['hardware']['Version']) is str, 'platform must contain a string version field'
        assert type(platform['hardware']['Cores']) is int, 'platform must contain an integer cores field'
        self.platform = platform
        return self

    def get_platform(self) -> dict:
        '''
        This method returns the platform information for the machine.
        '''
        if hasattr(self, 'platform'):
            return self.platform
        return None

    def set_captured(self, timestamp : datetime) -> None:
        '''
        This method sets the timestamp for the machine configuration.
        '''
        if type(timestamp) is dict:
            assert 'Label' in timestamp, 'timestamp must contain a Label field'
            assert timestamp['Label'] == 'Timestamp', 'timestamp must have a Label of Timestamp'
            assert 'Value' in timestamp, 'timestamp must contain a Value field'
            assert type(timestamp['Value']) is str, 'timestamp must contain a string Value field'
            assert self.validate_iso_timestamp(timestamp['Value']), f'timestamp {timestamp["Value"]} is not a valid ISO timestamp'
            self.captured = {
                'Label' : 'Timestamp',
                'Value' : timestamp['Value'],
            }
        elif type(timestamp) is datetime:
            timestamp = timestamp.isoformat()
        else:
            assert type(timestamp) is str, f'timestamp must be a string or timestamp (not {type(timestamp)})'
        self.captured = {
            'Label' : 'Timestamp',
            'Value' : timestamp,
        }
        return self

    def get_captured(self) -> datetime:
        '''
        This method returns the timestamp for the machine configuration.
        '''
        if hasattr(self, 'captured'):
            return self.captured
        return None

    def parse_config_file(self, config_data : dict) -> None:
        '''
        This method parses the configuration data from the config file.
        '''
        assert False, 'This method should be overridden by the derived classes.'

    def set_machine_id(self, machine_id)-> None:
        '''
        This method sets the machine ID for the machine configuration.
        '''
        if type(machine_id) is str:
            assert self.validate_uuid_string(machine_id), f'machine_id {machine_id} is not a valid UUID.'
        elif type(machine_id) is uuid.UUID:
            machine_id = str(machine_id)
        self.machine_id = machine_id
        return self

    def get_machine_id(self) -> str:
        '''
        This method returns the machine ID for the machine configuration.
        '''
        if hasattr(self, 'machine_id'):
            return self.machine_id
        return None

    @staticmethod
    def load_config_from_file(config_file : str) -> dict:
        '''
        This method creates a new IndalekoMachineConfig object from an
        existing config file.  This must be overriden by the platform specific
        machine configuration implementation.
        '''
        assert False, 'This method should be overridden by the derived classes.'

    @staticmethod
    def load_config_from_db(machine_id : str) -> 'IndalekoMachineConfig':
        '''
        This method loads the configuration from the database.
        '''
        assert IndalekoMachineConfig.validate_uuid_string(machine_id), f'machine_id {machine_id} is not a valid UUID.'
        collections = IndalekoCollections()
        machine_config_collection = collections.get_collection('MachineConfig')
        entries = machine_config_collection.find_entries(_key=machine_id)
        if len(entries) == 0:
            return None # not found
        assert len(entries) == 1, f'Found {len(entries)} entries for machine_id {machine_id} - multiple entries case not handled.'
        entry = entries[0]
        print(json.dumps(entry['platform'], indent=4))
        machine_config = IndalekoMachineConfig()
        machine_config.set_platform(entry['platform'])
        # temporary: I've changed the shape of the database, so I'll need to
        # work around it temporarily
        if type(entry['source'] is str) and 'version' in entry:
            machine_config.set_source({
                'Identifier' : entry['source'],
                'Version' : entry['version'],
            })
        else:
            assert type(entry['source']) is dict, f'entry["source"] must be a dict, not {type(entry["source"])}'
            machine_config.set_source(entry['source'])
        machine_config.set_captured(entry['captured'])
        machine_config.set_base64_data(entry['Data'])
        machine_config.set_attributes(entry['Attributes'])
        machine_config.set_machine_id(machine_id)
        return machine_config

    def to_json(self, indent : int = 4) -> str:
        '''
        This method returns the JSON representation of the machine config.
        '''
        record = super().to_dict()
        record['platform'] = self.platform
        record['captured'] = self.captured
        if hasattr(self, 'machine_id'):
            record['_key'] = self.machine_id
        print('***\n\n\n***', record)
        return json.dumps(record, indent=indent)

    @staticmethod
    def build_config(**kwargs) -> 'IndalekoMachineConfig':
        assert 'os' in kwargs, 'OS must be specified'
        assert type(kwargs['os']) is str, 'OS must be a string'
        assert 'arch' in kwargs, 'Architecture must be specified'
        assert type(kwargs['arch']) is str, 'Architecture must be a string'
        assert 'os_version' in kwargs, 'OS version must be specified'
        assert type(kwargs['os_version']) is str, 'OS version must be a string'
        assert 'cpu' in kwargs, 'CPU must be specified'
        assert type(kwargs['cpu']) is str, 'CPU must be a string'
        assert 'cpu_version' in kwargs, 'CPU version must be specified'
        assert type(kwargs['cpu_version']) is str, 'CPU version must be a string'
        assert 'cpu_cores' in kwargs, 'CPU cores must be specified'
        assert type(kwargs['cpu_cores']) is int, 'CPU cores must be an integer'
        assert 'source_id' in kwargs, 'Source must be specified'
        assert type(kwargs['source_id']) is str, 'Source must be a dict'
        assert 'source_version' in kwargs, 'Source version must be specified'
        assert type(kwargs['source_version']) is str, 'Source version must be a string'
        assert 'attributes' in kwargs, 'Attributes must be specified'
        assert 'data' in kwargs, 'Data must be specified'
        assert 'machine_id' in kwargs, 'Machine ID must be specified'
        if 'timestamp' in kwargs:
            assert IndalekoMachineConfig.validate_iso_timestamp(kwargs['timestamp']), f'Timestamp {kwargs["timestamp"]} is not a valid ISO timestamp'
            timestamp = kwargs['timestamp']
        else:
            timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if 'machine_config' not in kwargs:
            machine_config = IndalekoMachineConfig()
        else:
            machine_config = kwargs['machine_config']
        machine_config.set_platform({
            'software' : {
                'OS' : kwargs['os'],
                'Architecture' : kwargs['arch'],
                'Version' : kwargs['os_version']
            },
            'hardware' : {
                'CPU' : kwargs['cpu'],
                'Version' : kwargs['cpu_version'],
                'Cores' : kwargs['cpu_cores'],
            },
        })
        machine_config.set_captured(timestamp)
        machine_config.set_source({
            'Identifier' : kwargs['source_id'],
            'Version' : kwargs['source_version'],
        })
        machine_config.set_attributes(kwargs['attributes'])
        machine_config.set_base64_data(kwargs['data'])
        machine_config.set_machine_id(kwargs['machine_id'])
        return machine_config



def main():
    starttime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    parser = argparse.ArgumentParser()
    logfile = f'indalekomachineconfig-test-{starttime}.log'
    parser = argparse.ArgumentParser(description='Test base class for MachineConfig for the Indaleko database.')
    parser.add_argument('--machine_id', '-m', help='Machine ID to load from database', default='2e169bb7-0024-4dc1-93dc-18b7d2d28190')
    parser.add_argument('--log', '-l', help='Log file to use', default=logfile)
    parser.add_argument('--logdir', help='Log directory to use', default='./logs')
    args = parser.parse_args()
    if args.machine_id is not None:
        assert IndalekoMachineConfig.validate_uuid_string(args.machine_id), f'machine_id {args.machine_id} is not a valid UUID.'
        # look it up in the database
        machine_config = IndalekoMachineConfig.load_config_from_db(args.machine_id)
        print(machine_config.to_json())



if __name__ == "__main__":
    main()



