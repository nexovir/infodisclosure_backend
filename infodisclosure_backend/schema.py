import graphene
import users.schema

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello Hacker!")

class Mutation(users.schema.Mutation, graphene.ObjectType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
