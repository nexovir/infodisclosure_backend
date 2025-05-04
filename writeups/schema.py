import graphene
from graphene_django.types import DjangoObjectType
from .models import WriteUp, Category



class CategoryType(DjangoObjectType):
    class Meta:
        model = Category
        fields = '__all__'



class WriteUpType(DjangoObjectType):
    class Meta:
        model = WriteUp
        fields = '__all__'



class CreateWriteUp(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        category_id = graphene.Int(required=True)
        slug = graphene.String(required=True)
        short_description = graphene.String(required=True)
        content = graphene.String(required=True)
        vulnerability_type = graphene.String(required=True)
        target_type = graphene.String(required=True)
        tools_used = graphene.String()
        techniques = graphene.String()
        is_free = graphene.Boolean(default_value=True)
        price = graphene.Decimal()
        preview_text = graphene.String()
        is_public = graphene.Boolean(default_value=False)

    writeup = graphene.Field(WriteUpType)

    def mutate(self, info, title, category_id, slug, short_description, content, vulnerability_type, target_type,
               tools_used, techniques, is_free, price, preview_text, is_public):

        user = info.context.user
        if user.is_anonymous:
            raise Exception("Authentication required")

        category = Category.objects.get(id=category_id)

        writeup = WriteUp.objects.create(
            title=title,
            category=category,
            slug=slug,
            short_description=short_description,
            content=content,
            author=user,
            vulnerability_type=vulnerability_type,
            target_type=target_type,
            tools_used=tools_used,
            techniques=techniques,
            is_free=is_free,
            price=price,
            preview_text=preview_text,
            is_public=is_public,
            approved=False
        )

        return CreateWriteUp(writeup=writeup)
