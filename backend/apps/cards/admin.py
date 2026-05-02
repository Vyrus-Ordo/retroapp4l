from django.contrib import admin

from apps.cards.models import Card, CardVote

admin.site.register(Card)
admin.site.register(CardVote)

# Register your models here.
