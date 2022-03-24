from shopl_app.serializers import ListNameSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.forms import model_to_dict
from .models import User


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=False)
        try:
            user = serializer.validated_data['user']  
        except KeyError:
            return Response(status=403)        
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'id': user.pk,
            'name':user.name,
            'email': user.email,
            'token': token.key
        })

#/lists
@api_view(['POST','GET'])
@permission_classes([IsAuthenticated])
def lists_endpoint(request):
    user = User.objects.get(email=request.user)

    if request.method == 'POST':
        serializer = ListNameSerializer(data=request.data)
        if serializer.is_valid():
            new_list = serializer.save()
            user.user_lists.add(new_list)
            return Response(new_list.json())
        else:
            return Response(status=400)
    if request.method == 'GET':
        list_of_lists = [i.json() for i in user.user_lists.all()]
        return Response({
            "lists":list_of_lists
        })
       
#/list/{list_id}
@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated])
def list_endpoint(request,list_id):

    if request.method == 'GET':
        return Response({
            "list_id":list_id
            })

    if request.method == 'DELETE':
        return Response({
            "list_id":list_id
            })

#/list/{list_id}/product/{id}
@api_view(['PUT','DELETE'])
@permission_classes([IsAuthenticated])
def product_endpoint(request,list_id,id):
    if request.method == 'PUT':
        return Response({
            "list_id":list_id,
            "id":id
        })
    if request.method == 'DELETE':
        return Response({
            "list_id":list_id,
            "id":id
        })

#/list/{list_id}/product
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_add_endpoint(request,list_id):
    if request.method == "POST":
        return Response({
             "list_id":list_id,
        })

#/list/{list_id}/invite
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_endpoint(request,list_id):
    if request.method == "POST":
        return Response({
            "list_id":list_id,
        })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def particip_endpoint(request,list_id):
    if request.method == "GET":
        return Response({
            "list_id":list_id,
        })
    










    