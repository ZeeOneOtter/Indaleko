'''
This module defines the common database schema for Activity Data.

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
from datetime import datetime
from graphql import print_schema
from uuid import UUID
from typing import Annotated, List
from dataclasses import dataclass
from apischema.graphql import graphql_schema
from apischema.metadata import required


from IndalekoDataModel import IndalekoDataModel
from IndalekoRecordDataModel import IndalekoRecordDataModel

class IndalekoActivityDataModel(IndalekoRecordDataModel):
    '''This is the data model for the Indaleko Object type.'''
    @dataclass
    class ActivityData:
        ActivityDataIdentifier : Annotated[
            IndalekoDataModel.IndalekoUUID,
            required
        ]

        CollectionTimestamp: Annotated[
            IndalekoDataModel.Timestamp,
            required
        ]

        ActivityTimestamps : List[IndalekoDataModel.Timestamp]


def get_activity_data(context_id : UUID) -> IndalekoActivityDataModel.ActivityData:
    '''Return an activity context.'''
    activity_data = IndalekoActivityDataModel.ActivityData(
        ActivityDataIdentifier=context_id,
        CollectionTimestamp=IndalekoDataModel.Timestamp(
            Label=UUID('12345678-1234-5678-1234-567812345678'),
            Value=datetime.now(),
            Description='Test Timestamp'),
        ActivityTimestamps=[IndalekoDataModel.Timestamp(
            Label=UUID('12345678-1234-5678-1234-567812345678'),
            Value=datetime.now(),
            Description='Test Timestamp')]
    )
    return activity_data


def main():
    '''Test code for IndalekoObjectDataModel.'''
    print('GraphQL Schema:')
    print(print_schema(graphql_schema(query=[get_activity_data], types=[IndalekoActivityDataModel.ActivityData])))

if __name__ == '__main__':
    main()
