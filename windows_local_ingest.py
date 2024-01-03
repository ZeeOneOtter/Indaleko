import os
import json
import uuid
import stat
from arango import ArangoClient
import arango
import argparse
import datetime
from windows_local_index import IndalekoWindowsMachineConfig
from indalekocolletions import *
from dbsetup import IndalekoDBConfig
from indaleko import *
import msgpack
import base64
from IndalekoServices import IndalekoServices
import jsonlines
import logging
from indalekocolletions import *

class WindowsLocalIngest():

    WindowsMachineConfig_UUID = '3360a328-a6e9-41d7-8168-45518f85d73e'

    WindowsMachineConfigService = {
        'name': 'WindowsMachineConfig',
        'description': 'This service provides the configuration information for a Windows machine.',
        'version': '1.0',
        'identifier': WindowsMachineConfig_UUID,
        'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'type': 'Indexer',
    }

    WindowsLocalIndexer_UUID = '31315f6b-add4-4352-a1d5-f826d7d2a47c'

    WindowsLocalIndexerService = {
        'name': 'WindowsLocalIndexer',
        'description': 'This service indexes the local filesystems of a Windows machine.',
        'version': '1.0',
        'identifier': WindowsLocalIndexer_UUID,
        'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'type': 'Indexer',
    }

    WindowsLocalIngester_UUID = '429f1f3c-7a21-463f-b7aa-cd731bb202b1'

    WindowsLocalIngesterService = {
        'name': WindowsLocalIngester_UUID,
        'description': 'This service ingests captured index info from the local filesystems of a Windows machine.',
        'version': '1.0',
        'identifier': WindowsLocalIngester_UUID,
        'created': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'type': 'Ingester',
    }

    def register_service(self, service: dict) -> 'IndalekoServices':
        assert service is not None, 'Service cannot be None'
        assert 'name' in service, 'Service must have a name'
        assert 'description' in service, 'Service must have a description'
        assert 'version' in service, 'Service must have a version'
        assert 'identifier' in service, 'Service must have an identifier'
        return self.indaleko_services.register_service(service['name'], service['description'], service['version'], service['type'], service['identifier'])

    def lookup_service(self, name: str) -> dict:
        assert name is not None, 'Service name cannot be None'
        info = self.indaleko_services.lookup_service(name)
        return info

    def __init__(self, reset: bool = False) -> None:
        # Register our services
        self.indaleko_services = IndalekoServices(reset=reset)
        if len(self.lookup_service(self.WindowsMachineConfigService['name'])) == 0:
            self.register_service(self.WindowsMachineConfigService)
        if len(self.lookup_service(self.WindowsLocalIndexerService['name'])) == 0:
            self.register_service(self.WindowsLocalIndexerService)
        if len(self.lookup_service(self.WindowsLocalIngesterService['name'])) == 0:
            self.register_service(self.WindowsLocalIngesterService)
        self.sources = (
            self.WindowsMachineConfigService['name'],
            self.WindowsLocalIndexerService['name'],
            self.WindowsLocalIngesterService['name'],
        )
        self.collections = IndalekoCollections()


    def get_source(self, source_name: str) -> IndalekoSource:
        assert source_name is not None, 'Source name cannot be None'
        assert source_name in self.sources, f'Source name {source_name} is not valid.'
        source = self.lookup_service(source_name)[0]
        return IndalekoSource(uuid.UUID(source['identifier']), source['version'], source['description'])


    def get_config_data(self) -> dict:
        # this loads the data from the database if it is present.  If not, it
        # will store it.  TODO: probably need to have a versionable mechnism
        # here, to handle reconfig events.  I note there is dynamic data in here
        # so this comparison may not be trivial.

        return IndalekoWindowsMachineConfig().get_config_data()

    def save_config_data(self):
        # This saves the configuration data to the database.
        pass


def find_data_files(dir: str ='./data'):
    return [x for x in os.listdir(dir) if x.startswith('windows-local-fs-data') and x.endswith('.json')]

def find_config_files(dir: str ='./config'):
    return [x for x in os.listdir(dir) if x.startswith('windows-hardware-info') and x.endswith('.json')]

def load_config_file(config_file: str):
    with open(config_file, 'r') as f:
        config_data = json.load(f)
    return config_data


def main():
    data_files = find_data_files()
    assert len(data_files) > 0, 'At least one data file should exist'
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument('--datadir', '-d', help='Path to the data directory', default='./data')
    pre_parser.add_argument('--configdir', '-c', help='Path to the config directory', default='./config')
    pre_args, _ = pre_parser.parse_known_args()
    if pre_args.datadir != './data':
        data_files = find_data_files(pre_args.datadir)
    default_data_file = data_files[-1] # TODO: date/time sort this.
    parser = argparse.ArgumentParser(parents=[pre_parser])
    parser.add_argument('--input', choices=data_files, default=default_data_file, help='Windows Local Indexer file to ingest.')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--reset', action='store_true', help='Reset the service collection.')
    args = parser.parse_args()
    if args.datadir != './data':
        data_files = find_data_files(args.datadir)
    ingester = WindowsLocalIngest(reset=args.reset)
    machine_config = IndalekoWindowsMachineConfig(args.configdir)
    cfg = machine_config.get_config_data()
    config_data = base64.b64encode(msgpack.packb(cfg))
    config_record = IndalekoRecord(msgpack.packb(cfg), cfg, ingester.get_source(ingester.WindowsMachineConfigService['name']).get_source_identifier())

if __name__ == "__main__":
    main()
