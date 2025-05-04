import graphene
import users.schema
from writeups.schema import *


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello Hacker!")

class Mutation(users.schema.Mutation, graphene.ObjectType):
    create_writeup = CreateWriteUp.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
