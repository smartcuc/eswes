from django.urls import path

from producer.api.views import generator_list, generator_create, string_create

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
]
