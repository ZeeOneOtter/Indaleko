"""
The purpose of this package is to create a common class structure for managing
Indaleko Services.

We have multiple sources of information that can be indexed by Indaleko.  Thus,
this provides a "registration mechanism" that allows a service to create a
registration endpoint and get back an object that it can use for interacting
with its service information.

The types of services envisioned here are:

* Indexers - these are component that gather data from storage locations.
* Ingesters - these are components that convert raw indexed information into a
  common format that is used when storing the actual data.

I expect there will be other kinds of services in the future, but that's the
list for now.
"""
import argparse
import uuid
import datetime
import json
import arango
from IndalekoDBConfig import IndalekoDBConfig
from IndalekoCollections import IndalekoCollection, IndalekoCollections
from IndalekoServicesSchema import IndalekoServicesSchema
from Indaleko import Indaleko
from IndalekoRecord import IndalekoRecord

class IndalekoServices:
    '''
    This class defines the service model for Indaleko.
    '''

    Schema = IndalekoServicesSchema.get_schema()

    indaleko_services = 'Services'
    assert indaleko_services in Indaleko.Collections, \
        f'{indaleko_services} must be in Indaleko_Collections'

    service_types = (
        'Test',
        "Machine Configuration",
        'Indexer',
        'Ingester',
        'Semantic Transducer',
        'Activity Context Generator',
        'Activity Data Collector',
    )

    CollectionDefinition = {
        'schema' : Schema,
        'edge' : False,
        'indices' : {
            'name' : {
                'fields' : ['name'],
                'unique' : True,
                'type' : 'persistent'
            },
        },
    }

    def __init__(self, reset: bool = False) -> None:
        self.db_config = IndalekoDBConfig()
        self.db_config.start()
        self.service_collection = IndalekoCollection('Services',
                                                     self.CollectionDefinition,
                                                     self.db_config,
                                                     reset=reset)


    def create_indaleko_services_collection(self) -> IndalekoCollection:
        """
        This method creates the IndalekoServices collection in the database.
        """
        assert not self.db_config.db.has_collection(self.indaleko_services), \
         f'{self.indaleko_services} collection already exists, cannot create it.'
        self.service_collection = IndalekoCollection(self.db_config.db, self.indaleko_services)
        self.service_collection.add_schema(IndalekoServices.Schema)
        self.service_collection.create_index('name', 'persistent', ['name'], unique=True)
        return self.service_collection

    def lookup_service_by_name(self, name: str) -> dict:
        """
        This method is used to lookup a service by name.
        """
        entries = self.service_collection.find_entries(name =  name)
        assert len(entries) < 2, f'Multiple entries found for service {name}, not handled.'
        if len(entries) == 0:
            return None
        else:
            return entries[0]

    def lookup_service_by_identifier(self, service_identifier: str) -> dict:
        """
        This method is used to lookup a service by name.
        """
        if not Indaleko.validate_uuid_string(service_identifier):
            raise ValueError(f'{service_identifier} is not a valid UUID.')
        entries = self.service_collection.find_entries(identifier =  service_identifier)
        assert len(entries) < 2, \
            f'Multiple entries found for service {service_identifier}, not handled.'
        if len(entries) == 0:
            return None
        else:
            return entries[0]


    def register_service(self,
                         name: str,
                         description: str,
                         version: str,
                         service_type : str = 'Indexer',
                         service_id : str  = None) -> 'IndalekoServices':
        """
        This method registers a service with the given name, description, and
        version in the database.
        """
        assert service_type in IndalekoServices.service_types, \
            f'Invalid service type {service_type} specified.'
        if service_id is None:
            service_id = str(uuid.uuid4())
        new_service = {
            'name': name,
            'description': description,
            'version': version,
            'identifier' : service_id,
            'created' : datetime.datetime.now(datetime.UTC).isoformat(),
            '_key' : service_id,
        }
        self.service_collection.insert(new_service)
        return self.lookup_service_by_name(name)

class IndalekoService(IndalekoRecord):
    """
    In Indaleko, a service is a component that provides some kind of
    functionality.  This class manages registration and lookup of services.
    """
    indaleko_service_uuid_str = '951724c8-9957-4455-8132-d786b7383b47'
    indaleko_service_version = '1.0'

    def __init__(self, **kwargs):
        '''
        This class takes the following optional arguments:
        * service_collection -the collection to use for service
            lookup/registration.  Note that if this is not specified the
            database configuration will be used and the default collection is
            used.
        * service_identifier - the identifier for the service.  This is used
            to look up an existing service.  If this is specified, the service
            will be looked up by its identifier.
        * service_name - the name of the service.  This is used to look up
            the service if the identifier is not specified.  If the service
            does not exist, it will be created.  See Indaleko.Collections for
            known services.
        '''
        super().__init__(raw_data=b'',
                         attributes={},
                         source={'Identifier' : IndalekoService.indaleko_service_uuid_str,
                                 'Version' : IndalekoService.indaleko_service_version
                        })
        self.collection = None
        self.service_identifier = None
        self.service_name = None
        self.service_version = None
        self.service_description = None
        self.service_version = None
        self.service_type = None
        self.creation_date = self.__timestamp__
        if 'service_identifier' in kwargs:
            self.service_identifier = kwargs['service_identifier']
        if 'service_name' in kwargs:
            self.service_name = kwargs['service_name']
        if 'service_description' in kwargs:
            self.service_description = kwargs['service_description']
        if 'service_version' in kwargs:
            self.service_version = kwargs['service_version']
        if 'service_type' in kwargs:
            self.service_type = kwargs['service_type']
        if 'creation_date' in kwargs:
            self.creation_date = kwargs['creation_date']
        if self.collection is None:
            self.collection = IndalekoCollections().get_collection(Indaleko.Indaleko_Services)
        assert isinstance(self.collection, IndalekoCollection), \
            'service_collection must be an IndalekoCollection'
        found = False
        if self.service_identifier is not None:
            found = self.lookup_service_by_identifier()
        else:
            if self.service_name is None:
                raise ValueError('service_name must be specified.')
            found = self.lookup_service_by_name()
        if not found:
            if self.service_name is None:
                raise ValueError('service_name must be specified.')
            if self.service_version is None:
                raise ValueError('service_version must be specified.')
            if self.service_type is None or self.service_type not in IndalekoServices.service_types:
                raise ValueError('service_type must be one of ' +
                                 f'{IndalekoServices.service_types}, ' +
                                  f'is {self.service_type}')
            self.register_service()

    def load_record_data(self, record_data : dict) -> None:
        """Load the record data from the given dictionary."""
        assert isinstance(record_data, dict), 'record_data must be a dict'
        assert 'Identifier' in record_data, 'Identifier must be specified'
        assert 'Version' in record_data, 'Version must be specified'
        assert 'Name' in record_data, 'Name must be specified'
        assert 'Type' in record_data, 'Type must be specified'
        assert 'Created' in record_data, 'Created must be specified'
        self.service_identifier = record_data['Identifier']
        self.service_version = record_data['Version']
        self.service_name = record_data['Name']
        self.service_type = record_data['Type']
        self.creation_date = record_data['Created']
        if 'Description' in record_data:
            self.service_description = record_data['Description']
        return

    def lookup_service_by_name(self) -> bool:
        '''Given a string name for the service, look up that service.'''
        self.service = None
        data = self.collection.find_entries(Name = self.service_name)
        if not isinstance(data, list) or len(data) == 0:
            print('Service name {self.service_name} not found.')
            return False
        data = data[0]
        if not isinstance(data, dict):
            raise ValueError(f'Invalid service {data} found.')
        self.load_record_data(data)
        return True

    def lookup_service_by_identifier(self) -> bool:
        '''
        Given a string identifier (UUID) for the service, look up that
        service.
        '''
        self.service = None
        if not Indaleko.validate_uuid_string(self.service_identifier):
            raise ValueError(f'{self.service_identifier} is not a valid UUID.')
        data = self.collection.find_entries(Identifier = self.service_identifier)
        if not isinstance(data, list) or len(data) == 0:
            print('Service id {self.service_identifier} not found.')
            return False
        data = data[0]
        if not isinstance(data, dict):
            raise ValueError(f'Invalid service {data} found.')
        self.load_record_data(data)
        return True

    def register_service(self : 'IndalekoService') -> dict:
        '''
        This method registers a service with the given name, description,
        version, identifier (if specified,) type, and creation date (if
        specified.)
        '''
        if self.service_identifier is None:
            self.service_identifier = str(uuid.uuid4())
        if self.creation_date is None:
            self.creation_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
        assert self.service_type in IndalekoServices.service_types, \
            f'Invalid service type {self.service_type} specified.'
        try:
            self.collection.insert(self.to_dict())
        except arango.exceptions.DocumentInsertError as error:
            print(f'Error inserting service {self.service_name}: {error}')
            print(self.to_json())
            raise error
        return self.get_service_data()

    def get_service_data(self) -> dict:
        """Return the data for this service."""
        return {
            'Name' : self.service_name,
            'Description' : self.service_description,
            'Version' : self.service_version,
            'Identifier' : self.service_identifier,
            'Type' : self.service_type,
            'Created' : self.creation_date
        }

    @staticmethod
    def create_service_data(**kwargs) -> dict:
        '''
        This method creates the service data for the given arguments. The
        following values are mandatory:
        * service_name - the name of the service (a string)
        * service_version - the version of the service (a string)
        * service_type - the type of the service (a string)
        The following values are optional:
        * service_identifier - the identifier for the service (a UUID).  If it
        is not provided, one is generated.
        * service_description - the description of the service (a string).  If
        it is not provided, nothing is stored.
        * creation_date - the creation date of the service (a string).  If it is
        not provided, the current date/time is used.

        '''
        service_data = {}
        if 'service_name' in kwargs:
            service_data['Name'] = kwargs['service_name']
        else:
            raise ValueError('service_name must be specified.')
        if 'service_description' in kwargs:
            service_data['Description'] = kwargs['service_description']
        if 'service_version' in kwargs:
            service_data['Version'] = kwargs['service_version']
        else:
            raise ValueError('service_version must be specified.')
        if 'service_identifier' in kwargs:
            service_data['Identifier'] = kwargs['service_identifier']
        else: # generate a new one
            service_data['Identifier'] = str(uuid.uuid4())
        if 'service_type' in kwargs:
            service_data['Type'] = kwargs['service_type']
        if 'creation_date' in kwargs:
            service_data['Created'] = kwargs['creation_date']
        else:
            service_data['Created'] = \
                datetime.datetime.now(datetime.timezone.utc).isoformat()
        return service_data


    def to_dict(self) -> dict:
        """Return a dictionary representation of this object."""
        data = self.get_service_data()
        data['Record'] = super().to_dict()
        data['_key'] = data['Identifier']
        return data

    def to_json(self, indent : int = 4) -> str:
        """Return a JSON representation of this object."""
        return json.dumps(self.to_dict(), indent=indent)

def main():
    """Test the IndalekoServices class."""
    parser = argparse.ArgumentParser()
    parser.add_argument('--identifier', type=str, default='4debd7e6-c71a-4830-a0a1-8b4e599faea6', help='The identifier of the service to look up.')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--reset', action='store_true', help='Reset the service collection.')
    args = parser.parse_args()
    service = IndalekoService(service_name='test',
                              service_identifier=args.identifier,
                              service_description='This is a test service.',
                              service_version='1.0',
                              service_type='Test')
    print('Dump record after the lookup by name test:')
    print(service.to_json())
    service = IndalekoService(service_identifier='4debd7e6-c71a-4830-a0a1-8b4e599faea6')
    print('Dump record after the lookup by identifier test:')
    print(service.to_json())


if __name__ == "__main__":
    main()
