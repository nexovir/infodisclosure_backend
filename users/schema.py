import graphene
from django.contrib.auth.models import User
from graphene_django import DjangoObjectType
from django.contrib.auth import authenticate
from graphql import GraphQLError
from graphql_jwt.shortcuts import get_token




class UserType(DjangoObjectType):
    class Meta:
        model = User
        fields = ("id", "email", "username")




class SignupUser(graphene.Mutation):
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        username = graphene.String(required=True)

    user = graphene.Field (UserType)
    success = graphene.Boolean()
    message = graphene.String()


    def mutate(self, info, username, email, password):
        try:
            if User.objects.filter(email=email).exists():
                return SignupUser(success=False, message="Email already exists!")
            
            if User.objects.filter(username=username).exists():
                return SignupUser(success=False, message="Username already exists!")
            
            else :
                user = User.objects.create_user(username=username, email=email, password=password)
                return SignupUser(user=user, success=True, message="User created successfully!")
            
        except Exception as e:
            return SignupUser(success=False, message=str(e))




class LoginUser(graphene.Mutation):
    class Arguments:
        userEmail = graphene.String(required=True)
        password = graphene.String(required=True)

    user = graphene.Field(UserType)
    token = graphene.String()
    success = graphene.Boolean()
    message = graphene.String()

    def mutate(self, info, userEmail, password):

        user = authenticate(username=userEmail, password=password)

        if user is None:
            try:
                user_obj = User.objects.get(email=userEmail)
                if user_obj.check_password(password):
                    user = user_obj
                else:
                    return LoginUser(success=False, message="Username or password is incorrect")
            except User.DoesNotExist:
                return LoginUser(success=False, message="Username or password is incorrect")

        token = get_token(user)

        return LoginUser(
            user=user,
            token=token,
            success=True,
            message="Login successful"
        )
    


class Mutation(graphene.ObjectType):
    Signup = SignupUser.Field()
    Login = LoginUser.Field()
