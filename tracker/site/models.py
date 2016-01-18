from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model

from djangae.fields import RelatedSetField


class Project(TimeStampedModel):
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True)

    def __str__(self):
        return self.title

    @property
    def assignees(self):
        '''Users who are assigned to any related ticket'''
        users = get_user_model().objects.none()
        for ticket in self.tickets.all():
            users |= ticket.assignees.all()
        return users


class Ticket(TimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, related_name="tickets")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name="created_tickets")
    assignees = RelatedSetField(
        settings.AUTH_USER_MODEL, related_name="tickets")

    def __str__(self):
        return self.title
