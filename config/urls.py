from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from graphene_django.views import GraphQLView

urlpatterns = [
    # Endpoint único GraphQL con soporte de GraphiQL interactivo y exento de CSRF
    path('graphql', csrf_exempt(GraphQLView.as_view(graphiql=True))),
]
