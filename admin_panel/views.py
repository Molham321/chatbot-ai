import json
from io import BytesIO

from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

from admin_panel.models import AdminSettings
from chatbot_logging.models import ChatbotConversationLog, CalculatedAnswer
from chatbot_logic.models import Question, Answer, Context
from chatbot_logic.classes.ChatSessions import ChatSessions


def index_view(request):
    """
    Renders the Main Menu Page template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        return render(request, 'admin_panel/sites/index.html')
    else:
        return redirect('admin_panel:admin_login')


def login_view(request):
    """
    Renders the Login Page template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        return redirect('admin_panel:admin_index')
    else:
        return render(request, 'admin_panel/sites/login.html')


def login_user_view(request):
    """
    Tries the login for the user specified by the POST body data.
    There are two possible returns for this function depending on the login success:
        1. Login was successful -> User is redirected to the Home menu.
        2. Login failed -> User is redirected back to the Login screen.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.method == 'POST':
        request_object = request.POST.copy()
        username = request_object['username']
        password = request_object['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('admin_panel:admin_index')

        else:
            return redirect('admin_panel:admin_login')


def logout_user_view(request):
    """
    Performs the logout for the current user. Redirects to the Login page afterwards.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        logout(request)
        return redirect('admin_panel:admin_login')


def settings_view(request):
    """
    Renders the Settings Page template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        settings = get_settings()
        return render(request, 'admin_panel/sites/settings.html', {'settings': settings})
    else:
        return redirect('admin_panel:admin_login')


def logging_view(request):
    """
    Renders the Logging Overview template and returns it as HttpResponse.
    The Logs are automatically paginated, the current page is defined by the 'page' GET parameter.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        # Prepending "-" equals descending Order
        conversation_logs = ChatbotConversationLog.objects.order_by('-created_at').all()
        # Initiate Paginator
        paginator = Paginator(conversation_logs, 25)
        # Get requested page number
        page_number = request.GET.get('page')
        # Get current page from Paginator
        paginator_obj = paginator.get_page(page_number)

        # In case no page number was provided
        if page_number is None:
            page_number = 1
        else:
            page_number = int(page_number)

        return render(request, 'admin_panel/sites/logging.html',
                      {'paginator': paginator, 'currentPage': page_number, 'logs': paginator_obj})
    else:
        return redirect('admin_panel:admin_login')


def logging_detail_view(request, log_id):
    """
    Renders the Logging Detail template and returns it as HttpResponse.
    :param request: Passed django request object.
    :param log_id: The id of the log to be displayed.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        conversation_log = ChatbotConversationLog.objects.get(id=log_id)
        calculated_answers = CalculatedAnswer.objects.filter(
            chatbot_log_id=conversation_log.id).select_related('answer').select_related('question')
        return render(request, 'admin_panel/sites/logging_detail.html',
                      {'log': conversation_log, 'answers': calculated_answers})
    else:
        return redirect('admin_panel:admin_login')


def save_settings_view(request):
    """
    Saves the Adminsettings to the Database which are passed in the POST body.
    :param request: Passed django request object.
    :return: Returns an Json Response containing the status text.
    """
    if request.user.is_authenticated:
        return_data = {
            'toast_html': 'Es ist ein Fehler aufgetreten',
        }

        if request.method == 'POST':
            data = json.loads(request.body)

            if float(data["similarity_factor"]) > 0 and float(data["context_factor"]) > 0:
                settings = AdminSettings.objects.get(id=1)
                settings.greeting_text = data["greeting_text"]
                settings.noanswer_text = data["noanswer_text"]
                settings.similarity_factor = data["similarity_factor"]
                settings.context_factor = data["context_factor"]
                settings.matching_method = data["matching_method"]
                settings.mail_timeout_in_seconds = data["mail_timeout"]
                settings.similarity_mail_threshold = data["similarity_threshold"]
                settings.number_of_quality_test_answers = data["quality_test_answers"]

                settings.save()
                return_data['toast_html'] = 'Einstellungen gespeichert'
            else:
                return_data['toast_html'] = 'Kontext und Similarity Faktor müssen größer als 0.0 sein'

        return HttpResponse(json.dumps(return_data))
    else:
        return redirect('admin_panel:admin_login')


def questions_view(request):
    """
    Renders the Question / Answer / Kontext Overview template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        questions = Question.objects.order_by('-created_at').all()
        answers = Answer.objects.order_by('-created_at').all()
        contexts = Context.objects.order_by('-created_at').all()
        return render(request, 'admin_panel/sites/questions.html',
                      {'questions': questions, 'answers': answers, 'contexts': contexts})
    else:
        return redirect('admin_panel:admin_login')


def edit_questions_view(request, question_id):
    """
    View which handles the Edit of Questions. The question_id specifies which answer is saved.
    :param request: Passed django request object.
    :param question_id: The id from the question to be edited.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        question = Question.objects.get(id=question_id)
        answers = Answer.objects.order_by('-id').all()
        contexts = Context.objects.order_by('-id').all()
        return render(request, 'admin_panel/sites/edit_question.html',
                      {'question': question, 'answers': answers, 'contexts': contexts})
    else:
        return redirect('admin_panel:admin_login')


def save_questions_view(request, question_id):
    """
    View which handles the Save of Questions. The question_id specifies which question is saved.
    :param request: Passed django request object.
    :param question_id: The id from the question to be saved.
    :return: Returns an Json Response containing the status text.
    """
    if request.user.is_authenticated:
        return_data = {
            'toast_html': 'Frage konnte nicht gespeichert werden',
        }

        if request.method == 'POST':
            data = json.loads(request.body)
            question = Question.objects.get(id=question_id)

            if data['question_text'] and data['answer_id'] and data['context_id']:
                question.question_text = data["question_text"]
                question.answer_id = int(data["answer_id"])
                question.context_id = int(data["context_id"])
                question.save()
                return_data['toast_html'] = 'Frage wurde gespeichert'
            else:
                return_data['toast_html'] = 'Speichern fehlgeschlagen, bitte Dateneingabe prüfen'

        return HttpResponse(json.dumps(return_data))
    else:
        return redirect('admin_panel:admin_login')


def create_questions_view(request):
    """
    View which handles the Creation of Questions.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        message = request.GET.get('message', 'Neue Frage')

        question = Question()
        question.question_text = message
        question.save()
        return redirect('admin_panel:admin_questions_edit', question_id=question.id)
    else:
        return redirect('admin_panel:admin_login')


def edit_answers_view(request, answer_id):
    """
    View which handles the Edit of Answers. The context id specifies which answer is edited.
    :param request: Passed django request object.
    :param answer_id: The id from the answer to edit.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        answer = Answer.objects.get(id=answer_id)
        return render(request, 'admin_panel/sites/edit_answer.html', {'answer': answer})
    else:
        return redirect('admin_panel:admin_login')


def save_answers_view(request, answer_id):
    """
    View which represents the Save operation of an edited Answer.
    :param request: Passed django request object.
    :param answer_id: The id from the answer to save.
    :return: Returns an Json Response containing the status text.
    """
    if request.user.is_authenticated:
        return_data = {
            'toast_html': 'Antwort konnte nicht gespeichert werden',
        }

        if request.method == 'POST':
            data = json.loads(request.body)
            answer = Answer.objects.get(id=answer_id)

            if data['answer_text']:
                answer.answer_text = data['answer_text']
                answer.save()
                return_data['toast_html'] = 'Antwort wurde gespeichert'
            else:
                return_data['toast_html'] = 'Speichern fehlgeschlagen, bitte Dateneingabe prüfen'

        return HttpResponse(json.dumps(return_data))
    else:
        return redirect('admin_panel:admin_login')


def create_answers_view(request):
    """
    View which handles the Creation of Answers.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        message = request.GET.get('message', 'Neue Frage')

        answer = Answer()
        answer.answer_text = message
        answer.save()
        return redirect('admin_panel:admin_answers_edit', answer_id=answer.id)
    else:
        return redirect('admin_panel:admin_login')


def edit_contexts_view(request, context_id):
    """
    View which handles the Edit of Contexts. The context id specifies which context is edited.
    :param request: Passed django request object.
    :param context_id: The id from the context to edit.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        context = Context.objects.get(id=context_id)
        return render(request, 'admin_panel/sites/edit_context.html', {'context': context})
    else:
        return redirect('admin_panel:admin_login')


def save_contexts_view(request, context_id):
    """
    View which represents the Save operation of an edited Context.
    :param request: Passed django request object.
    :param context_id: The id from the context to save.
    :return: Returns an Json Response containing the status text.
    """
    if request.user.is_authenticated:
        return_data = {
            'toast_html': 'Kontext konnte nicht gespeichert werden',
        }

        if request.method == 'POST':
            data = json.loads(request.body)
            context = Context.objects.get(id=context_id)

            if data['context_text']:
                context.context_text = data['context_text']
                context.save()
                return_data['toast_html'] = 'Kontext wurde gespeichert'
            else:
                return_data['toast_html'] = 'Speichern fehlgeschlagen, bitte Dateneingabe prüfen'

        return HttpResponse(json.dumps(return_data))
    else:
        return redirect('admin_panel:admin_login')


def create_contexts_view(request):
    """
    View which handles the Creation of Contexts.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        context = Context()
        context.answer_text = 'Neuer Kontext'
        context.save()
        return redirect('admin_panel:admin_contexts_edit', context_id=context.id)
    else:
        return redirect('admin_panel:admin_login')


def get_settings():
    """
    Returns the Adminsettings object containing all global chatbot settings.
    The function fulfills two purposes:
        1. Return the Adminsettings for further use in the application.
        2. In case there are no settings yet: Initalize the Adminsettings and return them.
    :return: The AdminSettings Object.
    """
    count = AdminSettings.objects.count()

    if count == 1:
        return AdminSettings.objects.first()
    else:
        settings = AdminSettings.objects.create(
            similarity_factor=1.0,
            context_factor=1.0,
            matching_method='cosine',
            greeting_text='',
            noanswer_text=''
        )
        return settings


def toggle_questions_view(request):
    """
    Handles the activation / deactivation of questions and settings.
    Requires a POST body param named 'type' which specifies if a question or answer should be edited.
    The possible values for this param are:
        1. question
        2. answer
    Additionally the id of the edited object is expected in the POST body.
    :param request: Passed django request object.
    :return: Returns an Json Response containing the status text.
    """
    if request.user.is_authenticated:

        return_data = {
            'toast_html': 'Status konnte nicht aktualisiert werden',
            'status': False,
        }

        data = json.loads(request.body)
        obj_id = data['id']
        obj_type = data['type']
        obj = None

        if obj_type == 'question':
            obj = Question.objects.get(id=obj_id)
        elif obj_type == 'answer':
            obj = Answer.objects.get(id=obj_id)

        if obj:
            obj.active = not obj.active
            obj.save()
            return_data['toast_html'] = 'Status aktualisiert'
            return_data['status'] = obj.active
            return_data['id'] = obj_id

        return HttpResponse(json.dumps(return_data))
    else:
        return redirect('admin_panel:admin_login')


def log_download_view(request):
    """
    Returnes all Logs as Textfile
    :param request: Passed django request object.
    :return: Returns an Text Response with the Logging Data.
    """
    if request.user.is_authenticated:

        conversation_logs = ChatbotConversationLog.objects.all()
        logs = []

        for log in conversation_logs:
            tmp = {
                'conversation_log': log,
                'answers': CalculatedAnswer.objects.filter(chatbot_log_id=log.id).select_related(
                    'answer').select_related('question')[:5]
            }

            logs.append(tmp)

        template = get_template('admin_panel/logs/logfile.html')
        html = template.render({'logs': logs})

        response = BytesIO()

        pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')), response)
        return HttpResponse(response.getvalue(), content_type='application/pdf')
    else:
        return redirect('admin_panel:admin_login')


def chats_view(request):
    """
    Renders the Chat Overview template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        page = request.GET.get('page', 1)

        chat_sessions = ChatSessions()
        chats = chat_sessions.get_chats(page=page)

        return render(request, 'admin_panel/sites/chats.html',
                      {
                          'chats': chats
                      })
    else:
        return redirect('admin_panel:admin_login')


def chat_detail_view(request, chat_id):
    """
    Renders the Chat Detail template and returns it as HttpResponse.
    :param request: Passed django request object.
    :return: Returns an HttpResponse.
    """
    if request.user.is_authenticated:
        chat_sessions = ChatSessions()
        chat = chat_sessions.get_chat(chat_id=chat_id)

        if request.method == 'POST' and "delete" in request.POST:
            chat_sessions.delete_chat(chat_id=chat_id)
            return redirect('admin_panel:admin_chat')

        return render(request, 'admin_panel/sites/chat_details.html',
                      {
                          'chat': chat
                      })
    else:
        return redirect('admin_panel:admin_login')


def chat_view(request, session_token):
    if request.user.is_authenticated:
        return render(request, 'admin_panel/sites/chat.html', {'session_id': session_token})
    else:
        return redirect('admin_panel:admin_login')