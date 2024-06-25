import logging
from ldap3 import Server, Connection, TLS, get_config_parameter, set_config_parameter, SASL, ALL

from django.contrib.auth.models import User

from coldfront.core.allocation.models import Allocation, AllocationUser
from coldfront.core.project.models import Project, ProjectAttribute

from coldfront_plugin_auto_ldap.utils import (
    connect,
    disconnect,
    parse_uri,
    search_project,
    add_project,
    search_user,
    add_user,
    add_user_group,
    remove_user_group
)

logger = logging.getLogger(__name__)

# gets the project title from an allocation_pk
def get_project(allocation_pk):
    allocation = Allocation.objects.get(pk=allocation_pk)
    return allocation.project.title

# creates a new project
def add_group(allocation_pk):
    conn = connect()
    project = get_project(allocation_pk)
    pi = project.pi
    #search for group
    search_project(conn, project)
    
    # some kind of check here to see if the group was found
    if len(conn.entries) != 0:
        add_project(conn, project, pi)
    else:
        logger.warn("Project %s not found", project.title)
    
    disconnect(conn)

# creates user if it doesn't already exist and adds them to a project
def add_user(allocation_user_pk):
    conn = connect()
    user = AllocationUser.objects.get(pk=allocation_user_pk)
    username = user.user.username
    project = user.allocation.project.title

    # check if user exists, create if they don't - maybe, might be able to just use existing users in ldap
    search_user(conn, username)

    if len(conn.entries) == 0:
        logger.info("User %s does not exist, creating user", username)
        add_user(conn, user)

    # add user to project's group
    add_user_group(conn, username, project)

    disconnect(conn)

# removes a user from a project
def remove_user(allocation_user_pk):
    conn = connect()
    user = AllocationUser.objects.get(pk=allocation_user_pk)
    username = user.user.username
    project = user.allocation.project.title

    # sheck if user exists
    search_user(conn, username)

    if len(conn.entries) == 0:
        logger.info("User %s does not exist", username)
    else:
        remove_user_group(conn, user, project)
        
    disconnect(conn)
