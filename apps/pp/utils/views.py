import json

from django.http.response import HttpResponseBase, HttpResponse
from rest_framework import status

# We answer all unsuccessful requests with 400 status (bad request) that indicates the client's fault.
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

default_error_status = status.HTTP_400_BAD_REQUEST
# We answer all user-caused requests with 400status
# Policy based on http://blog.restcase.com/rest-api-error-codes-101/


class ValidationErrorResponse(Response):
    def __init__(self, errors, *args, **kwargs):
        content = [{
                        'source': {
                            'field': field
                        },
                       'detail': reason
                    }
                   for field, reason in errors.items()]
        super().__init__(content, *args, status=HTTP_400_BAD_REQUEST, **kwargs)


# Based on http://jsonapi.org/examples/#error-objects-basics
class ErrorResponse(Response):
    def __init__(self, error=None, title=None, *args, status=default_error_status, **kwargs):
        # Error is a detailed error message
        # Title is less specific and represents a class of errors
        content = [{
            'details': error or 'No details provided'
        }]
        if title:
            content[0]['title'] = title
        super().__init__(content, *args, status=status, **kwargs)


class PermissionDenied(ErrorResponse):
    def __init__(self, *args, status=default_error_status, **kwargs):
        super().__init__(*args, title='Permission Denied', status=status, **kwargs)


def get_data_fk_value(object, fk):
    """
    A helper function that compensates a JSON-API django module quirk.
    It extract foreign key fields from request body for POST & PATCH mathods
    ...

    The relationship body is
    "relationships": {
        "related_object": {
            "id": "2"
        }
    }
    JSON-API parser parses the request body so that we receive
    ...
    "related_object": {
        "id": "2"
    }

    Before we can safely pass request body to a django_rest.serializer we need to correct it with:
    data["related_object"] = get_data_fk_value(data, "related_object")

    :param object: the data part of a JSON-API data object
    :param fk: The relationship attribute
    :return: this relationship's id value
    """
    relationship_field = object.get(fk, {})
    if isinstance(relationship_field, dict):
        return relationship_field.get('id')
    else:
        return None