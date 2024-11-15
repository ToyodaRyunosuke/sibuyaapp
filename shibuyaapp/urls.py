from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path("", views.home_view,name = "home"),
    path("shibuyaapp/",views.shibuyaapp_view,name = "shibuyaapp"),
    path("event/<int:event_id>",views.event_ditail_view,name = "event_ditail"),
    path(
        "event/<int:event_id>/participate/",
        views.participate_in_event,
        name = "participate_in_event",
    ),
    path("mypage/",views.my_page_view, name = "my_page"),
    path("search/",views.search_view, name = "search"),
    path(
        "login/",
        LoginView.as_view(template_name="registration/login.html"),
        name = "login",
    ),
    path("sigup/",views.sigup_view,name = "sigup"),
    path("accounts/profile/",views.profile,name = "profile"),
    path("logout/",LoginView.as_view(),name = "logout"),
    path(
        "scraped_event_viewed/<str:event_title>/",
        views.scraped_event_viewed,
        name="scraped_event_viewed",
    ),
]