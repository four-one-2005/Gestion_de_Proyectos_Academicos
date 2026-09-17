import graphene
import graphql_jwt
import academico.schema


class Query(academico.schema.Query, graphene.ObjectType):
    """
    Query principal del proyecto que combina las queries de la aplicación académica
    y cualquier otra aplicación futura.
    """
    pass


class Mutation(academico.schema.Mutation, graphene.ObjectType):
    """
    Mutation principal del proyecto con mutaciones JWT estándar
    y las mutaciones académicas de negocio.
    """
    # Mutaciones de Autenticación JWT estándar
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
