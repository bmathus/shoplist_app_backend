from rest_framework import serializers

from shopl_app.models import List,Product
import uuid

class ListNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['name',]
    def create(self, validated_data):
        random_uuid = str(uuid.uuid4())
        return List.objects.create(**validated_data,invite_code=random_uuid)

class InviteCodeSerializer(serializers.Serializer):
    invite_code = serializers.CharField()

class ProductPutSerializer(serializers.ModelSerializer):
    picture_base64 = serializers.CharField(allow_null=True)
    class Meta:
        model = Product
        fields = ['name','quantity','unit','bought','picture_base64']
    def create(self, validated_data):
        return validated_data

class ProductPostSerializer(serializers.ModelSerializer):
    picture_base64 = serializers.CharField(allow_null=True)
    class Meta:
        model = Product
        fields = ['name','quantity','unit','picture_base64']
    def create(self, validated_data):
        return validated_data
