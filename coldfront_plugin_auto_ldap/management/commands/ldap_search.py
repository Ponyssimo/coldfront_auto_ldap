import logging

from django.core.management.base import BaseCommand, CommandError

from coldfront.core.project.models import Project, ProjectAttribute, ProjectUser
from coldfront.core.user.models import User

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
    help="Search for a user or group in LDAP"

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--user",
            help="Specify the user to search for. Use -p to specify the project to search in"
        )
        parser.add_argument(
            "-p",
            "--project",
            help="Specify the project to search for. Use -u to search for a user in the project"
        )

    def handle(self, *args, **options):
        user = None
        username = None
        project = None

        try:
            user = User.objects.get(username=options["user"])
            username = user.username
        except:
            pass
        try:
            projobj = Project.objects.get(title=options["project"])
            project = projobj.title
        except:
            pass

        if user == None and project == None:
            logger.warn("Usage error: no arguments given")
            return

        conn = connect()

        if user != None:
            if project != None:
                search_user_group(conn, user, project)
                if "uid=" + username + ",ou=users," + uri in conn.entries[0].entry_to_json():
                    logger.info("User {username} found in project {project}")
                else:
                    logger.info("User {username} not found in project {project}")
            else:
                search_user(conn, username)
                if len(conn.entries) == 0:
                    logger.info("User {username} not found")
                else:
                    logger.info("User {username} found")
        else:
            search_project(conn, project)
            if len(conn.entries) == 0:
                logger.info("Project {project} not found")
            else:
                logger.info("Project {project} found")

        disconnect(conn)
