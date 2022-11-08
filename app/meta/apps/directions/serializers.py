from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

from .models import Direction, Subject
from .service import DirectionService
from ..users.services import AuthAppService
from ..users.choices import StatusUser


User = get_user_model()


class DirectionsSerializers(serializers.ModelSerializer):

    class Meta:
        model = Direction
        fields = ('title', 'user', )


class SubjectSerializers(serializers.ModelSerializer):

    class Meta:
        model = Subject
        fields = ('name', 'description', 'direction')


class AddCuratorInDirectionSerializer(serializers.Serializer):
    curator = serializers.EmailField(min_length=2, max_length=100, required=True)
    direction_name = serializers.CharField(max_length=100)

    def validate(self, data):
        curator = AuthAppService.get_user(data['curator'])
        direction = DirectionService.get_direction(data.get('direction_name'))
        if not curator:
            raise serializers.ValidationError(
                {'Error': _("This curator is not found")})
        if not direction:
            raise serializers.ValidationError(
                {'Error': _("This direction is not found")})
        if curator.role != StatusUser.CURATOR:
            raise serializers.ValidationError(
                {'Error': _("This user is not a curator")})
        return data

    def create(self, validated_data):
        direction_name = validated_data.get('direction_name')
        print(direction_name)
        email = validated_data.get('curator')
        user = User.objects.get(email=email)
        direction = Direction.objects.get(title=direction_name)
        direction.user = user
        direction.save()
        return direction
