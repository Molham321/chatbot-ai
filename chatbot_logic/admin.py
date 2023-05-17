from django.contrib import admin

from admin_panel.models import AdminSettings
from .models import Question, Answer, Keyword, Context, Settings

# Register your models here.
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(Keyword)
admin.site.register(Context)
admin.site.register(Settings)
admin.site.register(AdminSettings)