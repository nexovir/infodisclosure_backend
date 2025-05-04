import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType




class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "username")



class RegisterUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)

    user = graphene.Field(UserType)
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, username, email, password):
        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            return RegisterUser(user=user, success=True, message="User created successfully!")
        
        except Exception as e:
            return RegisterUser(success=False, message=str(e))






class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
