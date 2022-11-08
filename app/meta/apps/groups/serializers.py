from rest_framework import serializers

from .models import StudentGroup
from ..users.models import Student
from ..users.serializers import StudentSerializer


class StudentGroupSerializers(serializers.ModelSerializer):

    class Meta:
        model = StudentGroup
        fields = ('title', )


class StudentGroupListSerializers(serializers.ModelSerializer):
    set_students = serializers.SerializerMethodField(method_name='get_students')

    class Meta:
        model = StudentGroup
        fields = ('title', 'set_students')

    def get_students(self, obj):
        student = Student.objects.filter(student_group=obj.id)
        serializer = StudentSerializer(student, many=True)
        data = serializer.data
        return data
