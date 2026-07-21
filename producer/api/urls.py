######################
# producer/api/urls.py
######################

from django.urls import path

from producer.api.views import generator_list, generator_create, generator_update, generator_delete
from producer.api.views import string_create, string_update, string_delete
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
        "<uuid:generator_id>/",
        generator_update,
    ),
    path(
        "<uuid:generator_id>/delete/",
        generator_delete,
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
    path(
        "string/create/",
        string_create,
        name="string-create",
    ),
    path(
        "string/<uuid:string_id>/",
        string_update,
    ),
    path(
        "string/<uuid:string_id>/delete/",
        string_delete,
    ),
]
