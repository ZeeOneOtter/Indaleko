'''
IndalekoActivityRegistration is a class used to register activity data
providers for the Indaleko system.

Project Indaleko
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
import logging
import msgpack
import uuid

from Indaleko import Indaleko
from IndalekoDBConfig import IndalekoDBConfig
from IndalekoServices import IndalekoService, IndalekoServices
from IndalekoSingleton import IndalekoSingleton
from IndalekoCollections import IndalekoCollections
from IndalekoCollection import IndalekoCollection
from IndalekoRecord import IndalekoRecord
from IndalekoActivityDataProviderRegistrationSchema \
    import IndalekoActivityDataProviderRegistrationSchema

class IndalekoActivityDataProviderRegistration(IndalekoRecord):
    '''This class defines the activity data provider registration for the
    Indaleko system.'''
    Schema = IndalekoActivityDataProviderRegistrationSchema.get_schema()

    UUID = '6c65350c-1dd5-4675-b17a-4dd409349a40'
    Version = '1.0'
    Description = 'Activity Data Provider Registration'
    Name = 'IndalekoActivityDataProviderRegistration'
    ActivityProviderDataCollectionPrefix = 'ActivityProviderData_'

    def __init__(self, **kwargs):
        '''Create an instance of the IndalekoActivityRegistration class.'''
        assert isinstance(kwargs, dict), 'kwargs must be a dict'
        print('IndalekoActivityDataProviderRegistration: ', kwargs)
        self.set_identifier(**{
            'Identifier' : kwargs.get('Identifier', str(uuid.UUID('00000000-0000-0000-0000-000000000000'))),
            'Version' : kwargs.get('Version', '1.0'),
            'Description' : kwargs.get('Description', 'Activity Provider'),
            'Name' : kwargs.get('Name', 'Activity Provider')
        })
        self.activity_data_collection_name = None
        # avoid the "not created in init warning" by setting a default value
        self.activity_collection_uuid = str(uuid.UUID('00000000-0000-0000-0000-000000000000'))
        self.set_activity_collection_uuid(kwargs.get('ActivityCollection', str(uuid.uuid4())))
        self.db_config = kwargs.get('DBConfig', IndalekoDBConfig())
        self.collections = kwargs.get('Collections', IndalekoCollections(db_config=self.db_config))
        self.active = kwargs.get('Active', True)
        super().__init__(raw_data = msgpack.packb(b''),
                         attributes = {},
                         source = {
                             'Identifier' : self.UUID,
                              'Version' : self.Version,
                              'Description' : self.Description,
                              'Name' : self.Name
                         })

    @staticmethod
    def generate_activity_data_provider_collection_name(identifier : str) -> str:
        '''Return the name of the collection for the activity provider.'''
        assert Indaleko.validate_uuid_string(identifier), f'Identifier {identifier} must be a valid UUID'
        return f'{IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix}{identifier}'

    def get_identifier(self, **kwargs):
        '''Return the identifier for the activity provider.'''
        if hasattr(self, 'identifier'):
            return self.identifier
        else:
            return self.set_identifier(**kwargs)

    def set_identifier(self, **kwargs) -> 'IndalekoActivityDataProviderRegistration':
        '''Set the identifier for the activity provider.'''
        assert 'Identifier' in kwargs, 'Identifier must be in kwargs'
        identifier = kwargs['Identifier']
        version = kwargs.get('Version', '1.0')
        self.identifier = {
            'Identifier' : identifier,
            'Version' : version,
            'Description' : kwargs.get('Description',
                                       f'Activity Provider {identifier} version {version}'),
            'Name' : kwargs.get('Name', f'Activity Provider {identifier}')
        }
        return self

    def get_activity_collection_uuid(self) -> str:
        '''Return the UUID for the activity collection.'''
        return self.activity_collection_uuid

    def set_activity_collection_uuid(self, collection_identifier : str) \
                                        -> 'IndalekoActivityDataProviderRegistration':
        '''Set the UUID for the activity collection.'''
        self.activity_collection_uuid = collection_identifier
        self.activity_data_collection_name = \
            self.generate_activity_data_provider_collection_name(collection_identifier)
        return self

    def set_activity_collection_name(self, collection_name : str) \
                                        -> 'IndalekoActivityDataProviderRegistration':
        '''Set the name for the activity collection.'''
        self.activity_data_collection_name = collection_name
        assert self.activity_data_collection_name.\
            startswith(IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix), \
            f'Collection name {self.activity_data_collection_name} must start with \
                {IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix}'
        collection_uuid = self.activity_data_collection_name[len(IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix):]
        assert Indaleko.validate_uuid_string(collection_uuid), \
            f'Collection UUID {collection_uuid} must be a valid UUID'
        self.activity_collection_uuid = collection_uuid
        return self

    def get_activity_collection_name(self) -> str:
        '''Return the name of the activity collection.'''
        return self.activity_data_collection_name

    def to_dict(self) -> dict:
        '''Return the object as a dictionary.'''
        registration = {
            '_key' : self.identifier['Identifier'],
            'Record' : super().to_dict(),
            'ActivityProvider'  : self.identifier,
            'ActivityCollection' : self.activity_data_collection_name,
            'Active' : self.active
        }
        return registration


    @staticmethod
    def create_from_db_entry(entry : dict) -> 'IndalekoActivityDataProviderRegistration':
        '''Return the object as a dictionary.'''
        new_record = IndalekoActivityDataProviderRegistration()
        new_record.set_identifier(**entry['ActivityProvider'])\
                  .set_activity_collection_name(entry['ActivityCollection'])
        if 'Record' in entry:
            new_record.set_base64_data(entry['Record']['Data'])\
                      .set_attributes(entry['Record']['Attributes'])\
                      .set_timestamp(entry['Record']['Timestamp'])
        new_record.active = entry.get('Active', True)
        return new_record


class IndalekoActivityDataProviderRegistrationService(IndalekoSingleton):

    '''This class is used to implement and access
    the Indaleko Activity Data Provider Registration Service.'''

    UUID = '5ef4125d-4e46-4e35-bea5-f23a9fcb3f63'
    Version = '1.0'
    Description = 'Indaleko Activity Data Provider Registration Service'
    Name = 'IndalekoActivityDataProviderRegistrationService'

    activity_registration_service = IndalekoService.create_service_data(
        service_name = Name,
        service_description = Description,
        service_version = Version,
        service_type = IndalekoServices.service_type_activity_data_registrar,
        service_identifier = UUID
    )

    def __init__(self, **kwargs):
        '''Create an instance of the
        IndalekoActivityDataProviderRegistrationService class.'''
        if self._initialized:
            return
        if 'db_config' in kwargs:
            self.db_config = kwargs['db_config']
        else:
            self.db_config = IndalekoDBConfig()
        self.service = IndalekoService(
            service_name = Indaleko.Indaleko_ActivityDataProviders,
            service_description = self.Description,
            service_version = self.Version,
            service_type=IndalekoServices.service_type_activity_data_registrar,
            service_identifier = self.UUID
        )
        self.activity_providers = IndalekoCollections.get_collection(
            Indaleko.Indaleko_ActivityDataProviders
        )
        assert self.activity_providers is not None, 'Activity Provider collection must exist'
        self._initialized = True

    def to_json(self) -> dict:
        '''Return the service as a JSON object.'''
        return self.service.to_json()

    @staticmethod
    def lookup_provider_by_identifier(identifier : str) -> IndalekoActivityDataProviderRegistration:
        '''Return the provider with the given identifier.'''
        providers = IndalekoActivityDataProviderRegistrationService().\
            activity_providers.find_entries(_key=identifier)
        if len(providers) == 0:
            return None
        if len(providers) > 1:
            raise NotImplementedError('Duplicate providers, not supported (versioning?)')
        return [IndalekoActivityDataProviderRegistration.create_from_db_entry(providers[0])]


    @staticmethod
    def lookup_provider_by_name(name : str) -> dict:
        '''Return the provider with the given name.'''
        providers = IndalekoActivityDataProviderRegistrationService().\
            activity_providers.find_entries(name=name)
        return providers

    @staticmethod
    def get_provider_list() -> list:
        '''Return a list of providers.'''
        aql_query = f'''
            FOR provider IN {Indaleko.Indaleko_ActivityDataProviders}
            RETURN provider
        '''
        cursor = IndalekoActivityDataProviderRegistrationService().db_config.db.aql.execute(aql_query)
        return [document for document in cursor]


    def get_provider(self, **kwargs) -> dict:
        '''Return a provider.'''
        if 'identifier' in kwargs:
            provider = self.lookup_provider_by_identifier(kwargs['identifier'])
        elif 'name' in kwargs:
            provider = self.lookup_provider_by_name(kwargs['name'])
        else:
            raise ValueError('Must specify either identifier or name.')
        if provider is None:
            provider = self.register_provider(**kwargs)
        return provider

    @staticmethod
    def create_activity_provider_collection(identifier : str, reset : bool = False) -> IndalekoCollection:
        '''Create an activity provider collection.'''
        assert Indaleko.validate_uuid_string(identifier), 'Identifier must be a valid UUID'
        activity_provider_collection_name = \
            IndalekoActivityDataProviderRegistration.\
                generate_activity_data_provider_collection_name(identifier)
        existing_collection = None
        try:
            existing_collection = IndalekoCollections.get_collection(activity_provider_collection_name)
        except ValueError:
            pass # this is the "doesn't exist" path
        if existing_collection is not None:
            return existing_collection
        activity_data_collection = IndalekoCollections\
            .get_collection(Indaleko.Indaleko_ActivityDataProviders)\
            .create_collection(
                name = activity_provider_collection_name,
                config = {
                    'schema' : IndalekoActivityDataProviderRegistration.Schema,
                    'edge' : False,
                    'indices' : {
                    },
                },
                reset = reset
            )
        return activity_data_collection

    @staticmethod
    def delete_activity_provider_collection(identifier : str) -> bool:
        '''Delete an activity provider collection.'''
        if identifier.startswith(IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix):
            identifier = identifier[len(IndalekoActivityDataProviderRegistration.ActivityProviderDataCollectionPrefix):]
        assert Indaleko.validate_uuid_string(identifier), 'Identifier must be a valid UUID'
        activity_provider_collection_name = \
            IndalekoActivityDataProviderRegistration.\
                generate_activity_data_provider_collection_name(identifier)
        existing_collection = None
        try:
            existing_collection = IndalekoCollections.\
                get_collection(activity_provider_collection_name)
            if existing_collection is not None:
                logging.info('Collection %s exists, deleting', activity_provider_collection_name)
                existing_collection.delete_collection(activity_provider_collection_name)
            else:
                logging.info('Collection %s does not exist', activity_provider_collection_name)
                return False
        except ValueError:
            pass
        return True

    def delete_provider(self, identifier : str) -> bool:
        '''Delete an activity data provider.'''
        existing_provider = self.lookup_provider_by_identifier(identifier)
        if existing_provider is None:
            return False
        logging.info('Deleting provider %s', identifier)
        self.activity_providers.delete(identifier)
        return False

    def register_provider(self, **kwargs) -> tuple:
        '''Register an activity data provider.'''
        assert 'Identifier' in kwargs, 'Identifier must be in kwargs'
        print('Registering provider: ', kwargs)
        existing_provider = self.lookup_provider_by_identifier(kwargs['Identifier'])
        if existing_provider is not None and len(existing_provider) > 0:
            raise NotImplementedError('Provider already exists, not updating.')
        activity_registration = IndalekoActivityDataProviderRegistration(**kwargs)
        self.activity_providers.insert(activity_registration.to_dict())
        existing_provider = self.lookup_provider_by_identifier(kwargs['Identifier'])
        assert existing_provider is not None, 'Provider creation failed'
        print(f"Registered Provider {kwargs['Identifier']}")
        activity_provider_collection = None
        create_collection = kwargs.get('CreateCollection', True)
        if create_collection:
            activity_provider_collection = self.create_activity_provider_collection(
                activity_registration.get_activity_collection_uuid()
            )
        return activity_registration, activity_provider_collection

    def deactivate_provider(self, identifier : str) -> bool:
        '''Deactivate an activity data provider.'''
        existing_provider = self.lookup_provider_by_identifier(identifier)
        if existing_provider is None:
            return False
        print('TODO: mark as inactive')
        return False

def main():
    '''Test the IndalekoActivityRegistration class.'''
    service = IndalekoActivityDataProviderRegistrationService()
    print(service.to_json())
    print(service.get_provider_list())


if __name__ == '__main__':
    main()
