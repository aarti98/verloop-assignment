from urllib.parse import urlencode
from decouple import config
import requests
from rest_framework import views, status
from rest_framework.response import Response

from geocoordinates.serializers import AddressToCoordinatesSerializer

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

        # google api to get geocoordinates according to output format
        geocode_result = requests.post(
            url="https://maps.googleapis.com/maps/api/geocode/{output_format}".format(
                output_format=serializer.validated_data['output_format'],
            ),
            params=params
        )
        response = dict()

        # reformatting of response
        if geocode_result.status_code == status.HTTP_200_OK:
            if geocode_result.json()['status'] == 'OK':
                response['coordinates'] = geocode_result.json()['results'][0]['geometry'].get('location')
                response['address'] = serializer.validated_data['address']
            else:
                response = geocode_result.json()
        else:
            response = geocode_result.json()

        return Response(
            data=response, status=geocode_result.status_code
        )
