from tastypie.resources import ModelResource
from mvc.models import User


class UserResource(ModelResource):

    class Meta:
        queryset = User.objects.all()
        allowed_methods = ['get', 'post']