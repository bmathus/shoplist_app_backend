from rest_framework import serializers

from shopl_app.models import List
import uuid

class ListNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['name',]
    def create(self, validated_data):
        random_uuid = str(uuid.uuid4())
        return List.objects.create(**validated_data,invite_code=random_uuid)

#class InviteCodeSerializer(serializers.Serializer):
    #invite_code = serializers.TextField()