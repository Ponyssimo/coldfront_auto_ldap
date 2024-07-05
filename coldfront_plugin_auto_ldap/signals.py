from django.dispatch import receiver
from django_q.tasks import async_task

from coldfront.core.allocation.signals import allocation_activate, allocation_activate_user, allocation_remove_user
from coldfront.core.project.views import ProjectAddUsersView, ProjectRemoveUsersView

from coldfront.core.allocation.models import Allocation, AllocationUser, AllocationAttribute, AllocationAttributeType

@receiver(allocation_activate)
def add_group(sender, **kwargs):
    allocation_pk = kwargs.get('allocation_pk')
    async_task('coldfront_plugin_auto_ldap.tasks.add_group', allocation_pk)

@receiver(allocation_activate_user, sender=ProjectAddUsersView)
def add_user(sender, **kwargs):
    allocation_user_pk = kwargs.get('allocation_user_pk')
    async_task('coldfront_plugin_auto_ldap.tasks.add_user', allocation_user_pk)

@receiver(allocation_remove_user, sender=ProjectRemoveUsersView)
def remove_user(sender, **kwargs):
    allocation_user_pk = kwargs.get('allocation_user_pk')
    async_task('coldfront_plugin_auto_ldap.tasks.remove_user', allocation_user_pk)
