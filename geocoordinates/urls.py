from django.urls import re_path
from geocoordinates.views import AddressToCoordinateViews

urlpatterns = [

    re_path(r'getAddressDetails/?$', AddressToCoordinateViews.as_view(),
            name='city_list_view'
            )
]
