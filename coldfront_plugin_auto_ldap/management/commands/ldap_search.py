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
        username = None
        project = None
        uri = parse_uri()

        try:
            username = options["user"]
        except:
            pass
        try:
            project = options["project"]
        except:
            pass

        if username == None and project == None:
            logger.warn("Usage error: no arguments given")
            return

        conn = connect()

        if username != None:
            if project != None:
                search_project(conn, project)
                if len(conn.entries) == 0:
                    print(f"Project {project} does not exist")
                search_user_group(conn, username, project)
                if "uid=" + username + ",ou=users," + uri in conn.entries[0].entry_to_json():
                    print(f"User {username} found in project {project}")
                else:
                    print(f"User {username} not found in project {project}")
            else:
                search_user(conn, username)
                if len(conn.entries) == 0:
                    print(f"User {username} not found")
                else:
                    print(f"User {username} found")
        else:
            search_project(conn, project)
            if len(conn.entries) == 0:
                print(f"Project {project} not found")
            else:
                print(f"Project {project} found")

        disconnect(conn)
