
from rest_framework import serializers
from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ["id", "title", "description", "created_at"]
        read_only_fields = ["id", "created_at"]

class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, allow_blank=False)