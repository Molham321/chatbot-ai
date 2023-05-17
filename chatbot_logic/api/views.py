import json

from django.template import loader
from django.views.decorators.clickjacking import xframe_options_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.response import Response
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView

from admin_panel.models import AdminSettings
from chatbot_logic.api.serializers import AnswerSetSerializer
from chatbot_logic.controllers.MatchController import MatchController


class ChatbotHTML(APIView):
    renderer_classes = [StaticHTMLRenderer]
    options = {}

    def __init__(self, options, **kwargs):
        super().__init__(**kwargs)
        self.options = options

    def get_settings(self):
        return AdminSettings.objects.all()[0]

    def get(self, request):
        template = loader.get_template('chatbot_logic/chatbot_frame.html')
        return Response(template.render({'options': self.options, 'settings': self.get_settings()}))


class AnswerUserHTML(APIView):
    renderer_classes = [StaticHTMLRenderer]
    options = {}

    def __init__(self, options, **kwargs):
        super().__init__(**kwargs)
        self.options = options

    def get(self, request):

        post_object = request.POST.copy()
        text = post_object.get('text')
        template = loader.get_template('chatbot_logic/chatbot_answer_user.html')

        return Response(template.render({'text': text}))


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def api_get_answer(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        question = data['question']

        if question is not None:

            match_controller = MatchController()

            answer = match_controller.match_against_db(question)

            serializer = AnswerSetSerializer(answer)

            return Response(serializer.data)

    return Response('Error ' + str(status.HTTP_500_INTERNAL_SERVER_ERROR))


@api_view(['GET'])
@xframe_options_exempt
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
def api_get_chatbot(request):
    if request.method == 'GET':
        view = ChatbotHTML({})
        return view.get(request)
    else:
        return Response('Error ' + str(status.HTTP_400_BAD_REQUEST))


@api_view(['POST'])
def api_render_message(request):
    if request.method == 'POST':
        view = AnswerUserHTML({})
        return view.get(request)
    else:
        return Response('Error ' + str(status.HTTP_400_BAD_REQUEST))
