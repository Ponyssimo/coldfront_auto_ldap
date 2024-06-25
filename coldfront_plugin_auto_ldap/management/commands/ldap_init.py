import logging

from django.core.management.base import BaseCommand, CommandError

from ldap3 import LEVEL
from ldap3.core.exceptions import LDAPException

from coldfront.core.project.models import Project, ProjectAttribute, ProjectUser
from coldfront.core.user.models import User

from coldfront.core.utils.common import import_from_settings

OU = import_from_settings("AUTO_LDAP_COLDFRONT_OU", 'COLDFRONT')

from coldfront_plugin_auto_ldap.utils import (
    connect,
    disconnect,
    parse_uri,
    search_project,
    add_project,
    search_user,
    search_user_group,
    add_user,
    add_user_group,
    remove_user_group
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help="Checks that an LDAP database is set up for Coldfront"

    def handle(self, *args, **options):
        conn = connect()
        uri = parse_uri(shortened=True)

        search_base = uri
        search_scope = LEVEL
        search_filter = '(ou=' + OU + ')'
        try:
            conn.search(search_base=search_base,
                        search_filter=search_filter,
                        search_scope=search_scope)
        except LDAPException as e:
            logger.warn(e)

        uri = parse_uri()

        if len(conn.entries) == 0:
            try:
                response = conn.add(uri, 'organizationalUnit')
            except LDAPException as e:
                logger.warn(e)


        search_base = uri
        search_scope = LEVEL
        search_filter = '(ou=users)'
        try:
            conn.search(search_base=search_base,
                        search_filter=search_filter,
                        search_scope=search_scope)
        except LDAPException as e:
            logger.warn(e)

        if len(conn.entries) == 0:
            try:
                response = conn.add('ou=users,' + uri, 'organizationalUnit')
            except LDAPException as e:
                logger.warn(e)


        search_base = uri
        search_scope = LEVEL
        search_filter = '(ou=projects)'
        try:
            conn.search(search_base=search_base,
                        search_filter=search_filter,
                        search_scope=search_scope)
        except LDAPException as e:
            logger.warn(e)

        if len(conn.entries) == 0:
            try:
                response = conn.add('ou=projects,' + uri, 'organizationalUnit')
            except LDAPException as e:
                logger.warn(e)

        disconnect(conn)
