import graphene

from graphql_api.mutations.cart_mutations import CartMutations
from graphql_api.mutations.order_mutations import OrderMutations
from graphql_api.mutations.review_mutations import ReviewMutations
from graphql_api.mutations.user_mutations import UserMutations
from graphql_api.queries.cart_queries import CartQuery
from graphql_api.queries.order_queries import OrderQuery
from graphql_api.queries.product_queries import ProductQuery
from graphql_api.queries.review_queries import ReviewQuery
from graphql_api.queries.user_queries import UserQuery


class Query(
    ProductQuery,
    CartQuery,
    OrderQuery,
    ReviewQuery,
    UserQuery,
    graphene.ObjectType,
):
    pass


class Mutation(
    CartMutations,
    OrderMutations,
    ReviewMutations,
    UserMutations,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(query=Query, mutation=Mutation)
