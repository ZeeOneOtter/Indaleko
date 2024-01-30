'''
This module handles indexing of the local Linux file systems.

Indaleko Linux Local Indexer
Copyright (C) 2024 Tony Mason

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
import argparse
import datetime
import os
import logging
import platform

from Indaleko import Indaleko
from IndalekoIndexer import IndalekoIndexer
from IndalekoLinuxMachineConfig import IndalekoLinuxMachineConfig


class IndalekoLinuxLocalIndexer(IndalekoIndexer):
    '''
    This is the class that indexes Mac local file systems.
    '''
    linux_platform = 'Linux'
    linux_local_indexer_name = 'fs-indexer'

    indaleko_linux_local_indexer_uuid = 'bef019bf-b762-4297-bbe2-bf79a65027ae'
    indaleko_linux_local_indexer_service_name = 'Mac Local Indexer'
    indaleko_linux_local_indexer_service_description = 'This service indexes the local filesystems of a Mac machine.'
    indaleko_linux_local_indexer_service_version = '1.0'
    indaleko_linux_local_indexer_service_type = 'Indexer'

    indaleko_linux_local_indexer_service ={
        'service_name' : indaleko_linux_local_indexer_service_name,
        'service_description' : indaleko_linux_local_indexer_service_description,
        'service_version' : indaleko_linux_local_indexer_service_version,
        'service_type' : indaleko_linux_local_indexer_service_type,
        'service_identifier' : indaleko_linux_local_indexer_uuid,
    }

    def __init__(self, **kwargs):
        assert 'machine_config' in kwargs, 'machine_config must be specified'
        self.machine_config = kwargs['machine_config']
        if 'machine_id' not in kwargs:
            kwargs['machine_id'] = self.machine_config.machine_id
        super().__init__(**kwargs,
                         platform=IndalekoLinuxLocalIndexer.linux_platform,
                         indexer_name=IndalekoLinuxLocalIndexer.linux_local_indexer_name,
                         **IndalekoLinuxLocalIndexer.indaleko_linux_local_indexer_service
        )


    def index(self) -> list:
        data = []
        for root, dirs, files in os.walk(self.path):
            for name in dirs + files:
                entry = self.build_stat_dict(name, root)
                if name in dirs:
                    self.dir_count += 1
                else:
                    self.file_count += 1
                if entry is not None:
                    data.append(entry[0])
        return data

def main():
    '''This is the main handler for the Indaleko Linux Local Indexer
    service.'''
    logging_levels = Indaleko.get_logging_levels()

    # Step 1: find the machine configuration file
    pre_parser = argparse.ArgumentParser(add_help=False)
    pre_parser.add_argument('--configdir',
                            help='Path to the config directory',
                            default=Indaleko.default_config_dir)
    pre_args, _ = pre_parser.parse_known_args()
    config_files = IndalekoLinuxMachineConfig.find_config_files(pre_args.configdir)
    default_config_file = IndalekoLinuxMachineConfig.get_most_recent_config_file(pre_args.configdir)
    # Step 2: figure out the default config file
    pre_parser = argparse.ArgumentParser(add_help=False, parents=[pre_parser])
    pre_parser.add_argument('--config', choices=config_files, default=default_config_file)
    pre_parser.add_argument('--path', help='Path to the directory to index', type=str,
                            default=os.path.expanduser('~'))
    pre_args, _ = pre_parser.parse_known_args()

    # Step 3: now we can compute the machine config and drive GUID
    machine_config = IndalekoLinuxMachineConfig.load_config_from_file(config_file=pre_args.config)

    drive = os.path.splitdrive(pre_args.path)[0][0].upper()
    drive_guid = machine_config.map_drive_letter_to_volume_guid(drive)
    if drive_guid is None:
        drive_guid = drive
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    indexer = IndalekoLinuxMachineConfig(machine_config=machine_config,
                                          timestamp=timestamp)
    output_file = indexer.generate_indexer_file_name()
    parser= argparse.ArgumentParser(parents=[pre_parser])
    parser.add_argument('--datadir', '-d',
                        help='Path to the data directory',
                        default=Indaleko.default_data_dir)
    parser.add_argument('--output', '-o',
                        help='name to assign to output directory',
                        default=output_file)
    parser.add_argument('--logdir', '-l',
                        help='Path to the log directory',
                        default=Indaleko.default_log_dir)
    parser.add_argument('--loglevel',
                        type=int,
                        default=logging.DEBUG,
                        choices=logging_levels,
                        help='Logging level to use (lower number = more logging)')

    args = parser.parse_args()
    indexer = IndalekoLinuxMachineConfig(timestamp=timestamp,
                                          path=args.path,
                                          machine_config=machine_config,
                                          storage_description=drive_guid)
    output_file = indexer.generate_indexer_file_name()
    log_file_name = indexer.generate_indexer_file_name(target_dir=args.logdir, suffix='log')
    logging.basicConfig(filename=os.path.join(log_file_name),
                                level=args.loglevel,
                                format='%(asctime)s - %(levelname)s - %(message)s',
                                force=True)
    logging.info('Indexing %s ' , pre_args.path)
    logging.info('Output file %s ' , output_file)
    data = indexer.index()
    indexer.write_data_to_file(data, output_file)
    counts = indexer.get_counts()
    for count_type, count_value in counts.items():
        logging.info('%s: %d', count_type, count_value)
    logging.info('Done')

if __name__ == '__main__':
    main()
