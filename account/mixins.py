from shop.models import Product
from django.http import Http404


class FieldMixins():

    def dispatch(self , request,*args,**kwargs):
        if request.user.is_superuser:
            self.fields   = ["title","price","discount_price","category","description","image",]
        else:
            raise Http404("You are not allowed to view this page")
        return super().dispatch(request,*args ,**kwargs)


class SuperUserMixin():
    def dispatch(self,request,*args,**kwargs):
        if request.user.is_superuser:
            return super().dispatch(request,*args, **kwargs)
        else:
            raise Http404("Unauthorized access")