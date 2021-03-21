import json
import xml.etree.ElementTree as et
from urllib.parse import urlencode

import dicttoxml
import requests
from decouple import config
from django.http import HttpResponse
from rest_framework import views, status

from geocoordinates.serializers import (AddressToCoordinatesSerializer, OUTPUT_CHOICES)

API_KEY = config('API_KEY')


class AddressToCoordinateViews(views.APIView):
    """
    To convert address into coordinates
    Required data:
        address
        output_form
    """

    def post(self, request):
        context = {'view': self, 'request': request}
        serializer = AddressToCoordinatesSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        url_params = {
            'address': serializer.validated_data['address'],
            'key': API_KEY
        }
        params = urlencode(url_params)

        # google api to get geo-coordinates according to output format
        geocode_result = requests.get(
            url="https://maps.googleapis.com/maps/api/geocode/{output_format}".format(
                output_format=serializer.validated_data['output_format'],
            ),
            params=params
        )
        response = dict()

        # to reformat data for xml
        if serializer.validated_data['output_format'] == OUTPUT_CHOICES[1]:
            content_type = 'application/xml'
            if geocode_result.status_code == status.HTTP_200_OK:
                root = et.fromstring(geocode_result.content)
                # if valid coordinates are found
                if root[0] is not None and root[0].tag == 'status':
                    if root[0].text == 'OK':
                        geometry = [child[0] for child in root[1] if child.tag == 'geometry']
                        geo_coordinates = list()
                        for coordinates in geometry[0]:
                            geo_coordinates.append(coordinates.text)
                        data = {
                            "root": [
                                {'address': serializer.validated_data['address'],
                                 'coordinates': {
                                     'lat': geo_coordinates[0],
                                     'long': geo_coordinates[1]
                                 }
                                 }
                            ]}
                        response = dicttoxml.dicttoxml(data, attr_type=False)
                    # to send zero results when status is other than OK
                    else:
                        response = geocode_result.text
            else:
                response = geocode_result.text

        # to reformat data for json
        else:
            content_type = 'application/json'
            # reformatting of response
            if geocode_result.status_code == status.HTTP_200_OK:
                if geocode_result.json()['status'] == 'OK':
                    response['coordinates'] = geocode_result.json()['results'][0]['geometry'].get('location')
                    response['address'] = serializer.validated_data['address']
                else:
                    response = geocode_result.json()
            else:
                response = geocode_result.json()
            response = json.dumps(response)

        return HttpResponse(
            response, status=geocode_result.status_code, content_type=content_type
        )
