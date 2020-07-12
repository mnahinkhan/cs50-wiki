from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry_page, name="entry"),
    path("search", views.search, name="search"),
    path("new-page", views.new_page, name="new page"),
    path("save-page", views.save_page, name="save page"),
    path("edit-page/<str:title>", views.edit_page, name="edit page"),
    path("save-page/<str:title>", views.save_page, name="save edited page"),
    path("random-page", views.random_page, name="random page")
]
