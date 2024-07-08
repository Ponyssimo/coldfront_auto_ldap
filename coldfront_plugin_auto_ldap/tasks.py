import logging
from ldap3 import Server, Connection, Tls, get_config_parameter, set_config_parameter, SASL, ALL

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

# creates a new project
def add_group(allocation_pk):
    conn = connect()
    project = Allocation.objects.get(pk=allocation_pk).project
    pi = project.pi
    #search for group
    search_project(conn, project.title)
    
    # some kind of check here to see if the group was found
    if len(conn.entries) == 0:
        add_project(conn, project.title, pi)
    else:
        logger.info("Project %s already exists", project.title)
    
    disconnect(conn)

# creates user if it doesn't already exist and adds them to a project
def add_user_proj(allocation_user_pk):
    conn = connect()
    user = AllocationUser.objects.get(pk=allocation_user_pk)
    username = user.user.username
    project = user.allocation.project.title
    projAllocs = Allocation.objects.filter(project=Project.objects.get(title=project)).order_by('pk').first()
    if user.allocation != projAllocs:
        disconnect(conn)
        return
    
    # check if user exists, create if they don't - maybe, might be able to just use existing users in ldap
    search_user(conn, username)

    if len(conn.entries) == 0:
        logger.info("User %s does not exist, creating user", username)
        add_user(conn, user.user)

    # add user to project's group
    add_user_group(conn, username, project)

    disconnect(conn)

# removes a user from a project
def remove_user_proj(allocation_user_pk):
    conn = connect()
    user = AllocationUser.objects.get(pk=allocation_user_pk)
    username = user.user.username
    project = user.allocation.project.title
    projAllocs = Allocation.objects.filter(project=Project.objects.get(title=project)).order_by('pk').first()
    if user.allocation != projAllocs:
        disconnect(conn)
        return

    # check if user exists
    search_user(conn, username)

    if len(conn.entries) == 0:
        logger.info("User %s does not exist", username)
    else:
        remove_user_group(conn, user.user, project)
        
    disconnect(conn)
