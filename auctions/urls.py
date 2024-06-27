from django.urls import path

from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "commerce"

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("listing/<int:listing_id>", views.view_listing, name="view_listing"),
    path("submitcomment/<int:listing_id>", views.submit_comment, name="submit_comment"),
    path("submitbid/<int:listing_id>", views.submit_bid, name="submit_bid"),
    path("create", views.create_listing, name="create"),
    path("close/<int:listing_id>", views.close_bid, name="close"),
    path("category", views.category_filter, name="filter"),
    path("category/<str:category>", views.view_category, name="view_category"),
    path("add/<int:listing_id>", views.add_watchlist, name="add_watchlist"),
    path("remove/<int:listing_id>", views.remove_watchlist, name="remove_watchlist"),
    path("watchlist", views.view_watchlist, name = "view_watchlist"),
    path("api", views.testAPI, name="test")
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)