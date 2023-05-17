from rest_framework import serializers


class AnswerItemSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    question_text = serializers.CharField(required=True, allow_blank=False)
    answer_id = serializers.IntegerField()
    answer_text = serializers.CharField(required=True, allow_blank=False)
    answer_rating = serializers.FloatField()


class AnswerSetSerializer(serializers.Serializer):
    answer = AnswerItemSerializer(required=True)
    assumed_answers = serializers.ListField(
        child=AnswerItemSerializer()
    )
