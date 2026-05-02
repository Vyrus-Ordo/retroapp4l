from django.contrib import admin

from apps.retrospectives.models import AccessLog, Milestone, Participant, Retrospective

admin.site.register(Retrospective)
admin.site.register(Milestone)
admin.site.register(Participant)
admin.site.register(AccessLog)

# Register your models here.
