from django.urls import path

from producer.api.views import generator_list

urlpatterns = [
    path(
        "",
        generator_list,
        name="generator-list",
    ),
]
