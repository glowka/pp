from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.pp import consts
from simple_history.models import HistoricalRecords


class User(AbstractUser):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'users'


class UserInput(models.Model):
    user = models.ForeignKey('pp.User')
    create_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class Annotation(UserInput):
    url = models.CharField(max_length=200)
    # URL where the annotation has been made

    ranges = models.TextField(max_length=1000)
    # Json data with information aboute the annotation location

    quote = models.TextField(max_length=250)
    # The exact annotated text part

    active = models.BooleanField(blank=True, default=True)

    # We never actually delete models -- we only mark them as not active

    class Meta:
        abstract = True


class ReferenceRequest(Annotation):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'reference_requests'


class Reference(Annotation):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'references'

    priority = models.CharField(choices=consts.annotation_priorities, max_length=100)
    comment = models.TextField(max_length=100)

    reference_link = models.CharField(max_length=100)
    # A hyperlink

    reference_link_title = models.CharField(max_length=100)
    # Short summary of the page referred to

    reference_request = models.ForeignKey(ReferenceRequest, null=True)
    # Null when the annotation has not been created on request

    history = HistoricalRecords()

    # django-simple-history used here

    @property
    def _history_user(self):
        return self.changed_by

    @_history_user.setter
    def _history_user(self, value):
        self.changed_by = value

    def count_useful_and_objection(self):
        self.useful_count = UserReferenceFeedback.objects.filter(reference=self).filter(useful=True).count()
        self.objection_count = UserReferenceFeedback.objects.filter(reference=self).filter(objection=True).count()
        return (self.useful_count, self.objection_count)


class ReferenceReport(UserInput):
    class Meta:
        app_label = 'pp'

    class JSONAPIMeta:
        resource_name = 'reference_reports'

    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    reason = models.CharField(choices=consts.reference_report_reasons, max_length=100)
    comment = models.TextField(max_length=100)


class UserReferenceFeedback(UserInput):
    class Meta:
        app_label = 'pp'
        unique_together = [('user', 'reference')]

    # No JSONAPIMeta information; the model corresponds to two resources, not just one

    reference = models.ForeignKey(Reference, related_name='feedbacks')

    # Only one of these can be true
    # todo not a very neat representation, should probably be changed to a single choice field
    useful = models.BooleanField(blank=True, default=False)
    objection = models.BooleanField(blank=True, default=False)


class UserReferenceRequestFeedback(models.Model):
    class Meta:
        app_label = 'pp'
        unique_together = [('user', 'reference_request')]

    class JSONAPIMeta:
        resource_name = 'user_reference_request_feedbacks'

    user = models.ForeignKey('pp.User')
    reference_request = models.ForeignKey(ReferenceRequest)
