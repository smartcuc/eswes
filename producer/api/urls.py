######################
# producer/api/urls.py
######################

from django.urls import path

from producer.api.views import generator_list, generator_create, string_create
from producer.api.views import generator_type_list, orientation_list


urlpatterns = [
    path(
        "",
        generator_list,
        name="generator-list",
    ),
    path(
        "create/",
        generator_create,
        name="generator-create",
    ),
    path(
        "string/create/",
        string_create,
        name="string-create",
    ),
    path(
        "types/",
        generator_type_list,
        name="generator-types",
    ),
    path(
        "orientations/",
        orientation_list,
        name="orientations",
    ),
]
