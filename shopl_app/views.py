from shopl_app.serializers import ListNameSerializer
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view,permission_classes
from rest_framework.response import Response
from django.forms import model_to_dict
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
        ppl = users_l.num_ppl
        msg = ""
        if ppl == 1: # A single person remains. We will delete this list
            prods = users_l.product_set.all()
            for i in range(len(prods)): # Delete all products from the list
                del_product(prods[i])
            users_l.delete()
            msg = "List deleted"
        else: # Just remove the user
            users_l.num_ppl -= 1
            users_l.save()
            msg = "User left the list"
        ref = user.user_lists.get(list__id=list_id)  # Delete user_lists reference
        ref.delete()
        return Response({
            "message": msg
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
        return Response(status=404)
    if prod.list_id != list_id: # Produkt nie je v danom zozname
        return Response(status=400) # spravny http status?
    
    if request.method == 'PUT':
        data = request.data
        if not product_check(data):
            return Response(status=400)
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
            if not found:
                pics.append({"id": prod.id, "base64": data["picture_base64"]})
            f.seek(0)
            f.truncate()
            json.dump(pics, f, indent=2)
        prod.save()
        return Response(status=200)
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
    data = request.data
    if request.method == "POST":
        if not product_check(data, False): # Bought is automatically False when created. No need to receive it
            return Response(status=400)
        prod = Product(name=data["name"], quantity=data["quantity"], unit=data["unit"], bought=False,
                       list_id=list_id)
        prod.save()
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

# /invite
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def invite_endpoint(request):
    data = request.data
    user = User.objects.get(email=request.user)
    if request.method == "POST":
        try:
            ilist = List.objects.get(invite_code=data["invite_code"])
        except ObjectDoesNotExist:
             return Response({"detail": "List with the given invite code does not exist"},status=400)
        try:
            user.user_lists.get(id=ilist.id)
            return Response({"detail": "You are already in this list."}, status=400)
        except ObjectDoesNotExist:
            ilist.num_ppl += 1
            ilist.save()
            user.user_lists.add(ilist)
        return Response(ilist.json())

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
    #check ci vobec list s danym id existuje - ak nie tak 400
    try:
        l = List.objects.get(id=list_id)
    except ObjectDoesNotExist:
        return Response( 
            {"detail":"List does not exist"},
            status=400)

    #check ci vobec user do daneho listu patri
    try:
        users_l = user.user_lists.get(id=list_id)
    except ObjectDoesNotExist:
        return Response(status=401)

    return users_l
    











    