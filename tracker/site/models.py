from django.conf import settings
from django.db import models
from django_extensions.db.models import TimeStampedModel
from django.contrib.auth import get_user_model

from djangae.fields import RelatedSetField

from django.core.cache import caches
from django.core import serializers


def deserialize_objects(serialized):
    deserialized = serializers.deserialize(settings.SERIALIZATION_FORMAT,
                                           serialized)
    return [d.object for d in deserialized]


class CachingQuerySet(models.QuerySet):
    '''Supplements the queryset returned by the database with locally
    cached objects.'''

    def _fetch_all(self):
        super(CachingQuerySet, self)._fetch_all()
        serialized = self.model.cache.get(self.model.cache_key())
        if serialized is not None:
            for obj in deserialize_objects(serialized):
                if obj in self._result_cache:
                    index = self._result_cache.index(obj)
                    self._result_cache.remove(obj)
                    self._result_cache.insert(index, obj)
                else:
                    self._result_cache.append(obj)
            self.model.cache.set(self.model.cache_key(), None)


class CachingManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        return CachingQuerySet(self.model, using=self._db)


class CachingTimeStampedModel(TimeStampedModel):
    '''Cache the last updated or created object'''
    objects = CachingManager()
    cache = caches['default']

    class Meta:
        abstract = True

    @classmethod
    def cache_key(cls):
        return 'last_saved_{}'.format(cls._meta.model_name)

    @property
    def serialized(self):
        return serializers.serialize(settings.SERIALIZATION_FORMAT, [self])

    def cache_object(self):
        self.cache.set(self.cache_key(), self.serialized)

    def save(self, *args, **kwargs):
        super(CachingTimeStampedModel, self).save(*args, **kwargs)
        self.cache_object()


class Project(CachingTimeStampedModel):
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


class Ticket(CachingTimeStampedModel):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    project = models.ForeignKey(Project, related_name="tickets")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, related_name="created_tickets")
    assignees = RelatedSetField(
        settings.AUTH_USER_MODEL, related_name="tickets")

    def __str__(self):
        return self.title
