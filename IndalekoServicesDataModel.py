'''
This module defines the database schema for any database record conforming to
the Indaleko Record requirements.

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
import apischema
from graphql import print_schema
from uuid import UUID
from typing import Annotated
from dataclasses import dataclass
from apischema.graphql import graphql_schema

from IndalekoDataModel import IndalekoDataModel
from IndalekoRecordDataModel import IndalekoRecordDataModel

class IndalekoServicesDataModel(IndalekoRecordDataModel):
    '''This is the data model for the Indaleko Services type.'''

    @dataclass
    class IndalekoService:
        '''This is the data model for the Indaleko Service type.'''
        Identifier : IndalekoDataModel.IndalekoUUID

        Version : Annotated[
            str,
            apischema.schema(description="This is the version of the source provider. Versioning allows evolution of the data generated by the source."),
            apischema.metadata.required
        ]

        Name : Annotated[
            str,
            apischema.schema(description="This is the name of the source provider."),
            apischema.metadata.required
        ]

        Type : Annotated [
            str,
            apischema.schema(description="This is the type of service provider."),
            apischema.metadata.required
        ]

def get_service(service_identifier : UUID) -> IndalekoServicesDataModel.IndalekoService:
    '''Return an IndalekoService object.'''
    service = IndalekoServicesDataModel.IndalekoService(
        Identifier = service_identifier,
        Version = '1.0.0',
        Name = 'Test Service',
        Type = 'Test'
    )
    return service

def main():
    '''Test the IndalekoServicesDataModel.'''
    print('GraphQL Schema:')
    print(print_schema(graphql_schema(
        query=[get_service],
        types=[IndalekoServicesDataModel.IndalekoService])))

if __name__ == '__main__':  # pragma: no cover
    main()
