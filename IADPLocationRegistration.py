'''Indaleko Activity Data Provider Location Registration'''

import argparse
import logging

from icecream import ic

from IndalekoActivityDataProviderRegistration import IndalekoActivityDataProviderRegistrationService
from IndalekoSingleton import IndalekoSingleton
from Indaleko import Indaleko
from IndalekoDBConfig import IndalekoDBConfig

class IADPLocationRegistration(IndalekoSingleton):
    '''This defines the class for location registration data.'''

    indaleko_activity_provider_location_name = 'IADPLocation'
    indaleko_activity_provider_location_source_uuid = '04c82f31-07d8-409c-9dd3-cbc661b7756d'
    indaleko_activity_provider_location_source = {
        'Identifier' : indaleko_activity_provider_location_source_uuid,
        'Version' : '1.0',
        'Description' : 'Indaleko Activity Data Provider for Location',
        'Name' : indaleko_activity_provider_location_name,
    }

    def __init__(self) -> None:
        '''Initialize the location data registration.'''
        if self._initialized:
            return
        registration = IADPLocationRegistration.lookup_service_registration()
        #registration = IndalekoActivityDataProviderRegistrationService().\
        #    lookup_provider_by_identifier(self.indaleko_activity_provider_location_source_uuid)
        if registration is None:
            registration = self.register_service()
        else:
            assert len(registration) == 2, \
                f'Invalid data returned from registration lookup {registration}'
            self.activity_provider = registration[0]
            self.activity_provider_collection = registration[1]
        assert registration is not None, 'Failed to register the location service'
        super().__init__()
        self._initialized = True


    def register_service(self) -> bool:
        '''Register the location service.'''
        source = IADPLocationRegistration.indaleko_activity_provider_location_source
        registration_data = IndalekoActivityDataProviderRegistrationService()\
            .register_provider(
                Identifier=source['Identifier'],
                Version=source['Version'],
                Description = source.get('Description', None),
                Name = source.get('Name', None),
                CreateCollection=True,
        )
        assert len(registration_data) == 2, \
            f'Invalid data returned from registration {registration_data}'
        self.activity_provider = registration_data[0]
        self.activity_provider_collection = registration_data[1]
        return True

    def unregister_service(self) -> bool:
        '''Unregister the location service.'''
        assert self.activity_provider is not None, 'No location service to unregister'
        IndalekoActivityDataProviderRegistrationService()\
            .delete_provider(IADPLocationRegistration.indaleko_activity_provider_location_source_uuid)
        if self.activity_provider_collection is not None:
            IndalekoActivityDataProviderRegistrationService()\
                .delete_activity_provider_collection(
                    self.activity_provider.get_activity_collection_name())
        return True

    def get_activity_collection_name(self) -> str:
        '''Return the activity collection name.'''
        if self.activity_provider_collection is None:
            return None
        return self.activity_provider_collection.collection_name

    @staticmethod
    def lookup_service_registration() -> IndalekoActivityDataProviderRegistrationService:
        '''Lookup the location service registration.'''
        registration = IndalekoActivityDataProviderRegistrationService().\
            lookup_provider_by_identifier(IADPLocationRegistration\
                                          .indaleko_activity_provider_location_source_uuid)
        return registration

class IADPLocationRegistrationTest:
    '''Test the IADPLocationRegistration class.'''

    @staticmethod
    def check_command(args: argparse.Namespace) -> None:
        '''Check the base functionality.'''
        ic('Checking IADPLocationRegistration')
        ic(args)
        registration = IADPLocationRegistration()
        ic(registration)
        ic('Checking IADPLocationRegistration complete')

    @staticmethod
    def test_command(args: argparse.Namespace) -> None:
        '''Test the base functionality.'''
        ic('Testing IADPLocationRegistration')
        ic(args)
        ic('Testing IADPLocationRegistration complete')

    @staticmethod
    def show_command(args: argparse.Namespace) -> None:
        '''Show the registration information'''
        ic('Showing IADPLocationRegistration')
        ic(args)
        IndalekoDBConfig().start()
        registration = IADPLocationRegistration()
        ic(registration)
        ic(registration.activity_provider)
        ic(registration.activity_provider_collection)
        ic('Showing IADPLocationRegistration complete')

    @staticmethod
    def remove_command(args: argparse.Namespace) -> None:
        '''Remove the registration information'''
        ic('Removing IADPLocationRegistration')
        ic(args)
        IndalekoDBConfig().start()
        registration = IADPLocationRegistration()
        ic(registration.activity_provider.to_dict())
        ic(registration.get_activity_collection_name())
        registration.unregister_service()
        ic('Removing IADPLocationRegistration complete')

def main():
    '''Test the IADPLocationRegistration class.'''
    ic('Testing IADPLocationRegistration')
    parser = argparse.ArgumentParser(description='Test the IADPLocationRegistration class')
    parser.add_argument('--logdir' ,
                        type=str,
                        default=Indaleko.default_log_dir,
                        help='Log directory')
    parser.add_argument('--log',
                        type=str,
                        default=None,
                        help='Log file name')
    parser.add_argument('--loglevel',
                        type=int,
                        default=logging.DEBUG,
                        choices=Indaleko.get_logging_levels(),
                        help='Log level')
    command_subparsers = parser.add_subparsers(help='Command subparsers', dest='command')
    parser_check = command_subparsers.add_parser('check', help='Check the base functionality')
    parser_check.set_defaults(func=IADPLocationRegistrationTest.check_command)
    parser_test = command_subparsers.add_parser('test', help='Test the base functionality')
    parser_test.set_defaults(func=IADPLocationRegistrationTest.test_command)
    parser_show = command_subparsers.add_parser('show', help='Show the registration information')
    parser_show.set_defaults(func=IADPLocationRegistrationTest.show_command)
    parser_remove = command_subparsers.add_parser('remove', help='Remove the registration information')
    parser_remove.set_defaults(func=IADPLocationRegistrationTest.remove_command)
    parser.set_defaults(func=IADPLocationRegistrationTest.show_command)
    args = parser.parse_args()
    if args.log is None:
        args.log = Indaleko.generate_file_name(
            suffix='log',
            service='IADPLocationRegistration',
        )
    IADPLocationRegistration()
    args.func(args)

if __name__ == '__main__':
    main()
