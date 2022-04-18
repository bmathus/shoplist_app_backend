from shopl_app.serializers import InviteCodeSerializer, ListNameSerializer,ProductPutSerializer,ProductPostSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from .models import User,List,Product
from django.core.exceptions import ObjectDoesNotExist
import json


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=False)
        try:
            user = serializer.validated_data['user']  
        except KeyError:
            return Response(status=401)        
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
            return Response({"detail":"List must have a name"},status=400)
    if request.method == 'GET':
        list_of_lists = [i.json() for i in user.user_lists.all()]
        return Response({
            "lists":list_of_lists
        })
       
#/list/{list_id}
@api_view(['GET','DELETE'])
@permission_classes([IsAuthenticated])
def list_endpoint(request,list_id):
    user = User.objects.get(email=request.user)
    users_l = check_list(list_id,user)
    if not isinstance(users_l,List):
        return users_l

    if request.method == 'GET': # Getting list products
        list_of_products = []
        prods = users_l.product_set.all()
        with open('pictures.json', 'r') as f:  # Finding and loading the image
            pics = json.load(f)
            for p in range(len(prods)):
                js = prods[p].json()
                js["picture_base64"] = None
                for i in range(len(pics)):
                    if pics[i]["id"] == prods[p].id:
                        js["picture_base64"] = pics[i]["base64"]
                list_of_products.append(js)
        return Response({
            "products": list_of_products
            })

    if request.method == 'DELETE': # Leaving/deleting a shopping list
        if users_l.num_ppl == 1: # A single person remains. We will delete this list
            prods = users_l.product_set.all()
            for i in range(len(prods)): # Delete all products from the list
                del_product(prods[i])
            users_l.delete()
            msg = "List deleted"
        else: # Just remove the user from list
            users_l.num_ppl -= 1
            users_l.save()
            user.user_lists.remove(users_l)
            msg = "User left the list"
        return Response({
            "detail": msg
            })

#/list/{list_id}/product/{id}
@api_view(['PUT','DELETE'])
@permission_classes([IsAuthenticated])
def product_endpoint(request,list_id,id):
    user = User.objects.get(email=request.user)
    users_l = check_list(list_id, user)
    if not isinstance(users_l, List):
        return users_l
    # Check if product exists and is part of given list
    try:
        prod = Product.objects.get(id=id)
    except ObjectDoesNotExist:
        return Response({"detail":"Product with this id does not exist"},status=404)
    if prod.list_id != list_id: # Produkt nie je v danom zozname
        return Response({"detail":"Product not in list with this list_id"},status=400)
    
    if request.method == 'PUT':
        serializer = ProductPutSerializer(data=request.data)
        if serializer.is_valid() and product_check(serializer.save()):
            data = serializer.validated_data
            prod.name = data["name"]
            prod.quantity = data["quantity"]
            prod.unit = data["unit"]
            prod.bought = data["bought"]
            with open('pictures.json', 'r+') as f:  # Finding the image reference
                pics = json.load(f)
                found = False
                for i in range(len(pics)):
                    if pics[i]["id"] == id:
                        found = True
                        if data["picture_base64"] is None: # Delete reference from JSON file
                            pics.pop(i)
                        else:
                            pics[i]["base64"] = data["picture_base64"] # Rewrite image
                        break
                if not found and data["picture_base64"] is not None:
                    pics.append({"id": prod.id, "base64": data["picture_base64"]})
                f.seek(0)
                f.truncate()
                json.dump(pics, f, indent=2)
            prod.save()
            return Response(status=200)
        else:
            return Response({"detail":"Not valid or missing fields"},status=400)

    if request.method == 'DELETE':
        del_product(prod)
        users_l.num_items -= 1
        users_l.save()
        return Response(status=200)

#/list/{list_id}/product
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def product_add_endpoint(request,list_id):
    user = User.objects.get(email=request.user)
    users_l = check_list(list_id, user)
    if not isinstance(users_l, List):
        return users_l

    if request.method == "POST":
        serializer = ProductPostSerializer(data=request.data)
        if serializer.is_valid() and product_check(serializer.save(),False):
            data = serializer.validated_data
            prod = Product.objects.create(name=data["name"], quantity=data["quantity"], unit=data["unit"], bought=False,
                    list_id=list_id)
            users_l.num_items += 1
            users_l.save()
            if data["picture_base64"] is not None:
                with open('pictures.json', 'r+') as f:
                    pics = json.load(f)
                    pics.append({"id": prod.id, "base64": data["picture_base64"]})
                    f.seek(0)
                    f.truncate()
                    json.dump(pics, f, indent=2)
            js = prod.json()
            js["picture_base64"] = data["picture_base64"]
            return Response(js)
        else:
            return Response({"detail":"Not valid or missing fields"},status=400)

# list/invite
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_endpoint(request):
    user = User.objects.get(email=request.user)
    if request.method == "POST":
        serializer = InviteCodeSerializer(data=request.data)
        if serializer.is_valid():
            invite_code = serializer.validated_data["invite_code"]
            try:
                ilist = List.objects.get(invite_code=invite_code)
            except ObjectDoesNotExist:
                return Response({"detail": "List with the given invite code does not exist"},status=404)
            try:
                user.user_lists.get(id=ilist.id)
                return Response({"detail": "You are already in this list."}, status=400)
            except ObjectDoesNotExist:
                ilist.num_ppl += 1
                ilist.save()
                user.user_lists.add(ilist)
            return Response(ilist.json())

        else:
            return Response({"detail":"Invite code not valid"},status=400)
          

# /list/{list_id}/participants
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def particip_endpoint(request,list_id):
    user = User.objects.get(email=request.user)
    if request.method == "GET":
        users_l = check_list(list_id,user)
        if not isinstance(users_l,List):
            return users_l

        list_of_users = [i.json() for i in users_l.user_set.all()]
        return Response({
            "users":list_of_users
        })


# call/<int:user_id>
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def call_room_check(request, user_id):
    calluser = User.objects.get(id=user_id)
    user = User.objects.get(email=request.user)
    if calluser == user:
        return Response({"detail": "You cannot call yourself"}, status=400)
    if request.method == "GET":
        if calluser.called_user is None or calluser.called_user == user.email:
            # If None is returned, user must create a room. Otherwise existing room is returned.
            if calluser.called_user == user.email:
                user.room_id = calluser.room_id
                user.called_user = calluser.email
                calluser.save()
                user.save()
            return Response({"room_id": calluser.room_id}, status=200)
        else:
            return Response({"detail": "The user is already in a call"}, status=400)

# call
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_room(request):
    user = User.objects.get(email=request.user)
    if request.method == "POST":
        data = request.data
        user.room_id = data["room_id"]
        user.called_user = data["called_user"]
        user.save()
    return Response(status=200)

# call/end
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def call_end(request):
    user = User.objects.get(email=request.user)
    calluser = User.objects.get(email=user.called_user)
    user.room_id = calluser.room_id = None
    user.called_user = calluser.called_user = None
    user.save()
    calluser.save()
    return Response(status=200)
    
def product_check(data, include_bought=True):
    # Check if data contains all fields
    to_test = ["name", "quantity", "unit", "picture_base64"]
    if include_bought:
        to_test.append("bought")
    for i in range(len(to_test)):
        if not to_test[i] in data:
            return False
    return True

def del_product(product): # The product needs to be removed from DB, but we also may need to remove the image
    id = product.id
    product.delete()
    with open('pictures.json', 'r+') as f:  # Finding the image reference
        pics = json.load(f)
        for i in range(len(pics)):
            if pics[i]["id"] == id:
                pics.pop(i) # Removing the reference from the JSON object
                break
        f.seek(0)
        f.truncate()
        json.dump(pics, f, indent=2) # Write it back into the file

def check_list(list_id,user):
    # Check if the list exists
    try:
        l = List.objects.get(id=list_id)
    except ObjectDoesNotExist:
        return Response( 
            {"detail":"List does not exist"},
            status=404)
    # Check if user belongs to the list
    try:
        users_l = user.user_lists.get(id=list_id)
    except ObjectDoesNotExist:
        return Response({"detail":"User not allowed in list"},status=401)
    return users_l