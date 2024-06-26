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
    add_user,
    add_user_group,
    remove_user_group
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Adds users or projects to LDAP. Adds all users and projects in Coldfront if no options specified"

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--user",
            help="Add a user, use -p to specify a project to add the user to"
        )
        parser.add_argument(
            "-p",
            "--project",
            help="Add a project, or specify project when used with -u"
        )
        parser.add_argument(
            "-r",
            "--remove",
            action="store_true",
            help="Use with -r and -p to remove a user from a project"
        )

    def handle(self, *args, **options):
        projects = Project.objects.all()
        users = User.objects.all()

        user = None
        project = None

        try:
            user = User.objects.get(name=options["user"])
        except:
            pass
        try:
            project = name=options["project"]
        except:
            pass

        conn = connect()

        if user != None:
            search_user(conn, user)
            if len(conn.entries) == 0:
                add_user(conn, user)
            if project != None:
                search_project(project)
                if len(conn.entries) != 0:
                    if options["remove"]:
                        remove_user_group(conn, user, project)
                    else:
                        add_user(conn, user, project)
                else:
                    logger.warn("Project " + project + " does not exist")
        elif project != None:
            search_project(conn, project)
            if len(conn.entries) != 0:
                add_project(conn, project)
        else:
            for p in projects:
                proj = p.title
                search_project(conn, proj)
                if len(conn.entries) == 0:
                    break
                add_project(conn, proj)
                users = project.ProjectUser.all()
                for u in users:
                    username = u.user.username
                    search_user(conn, username)
                    if len(conn.entries) == 0:
                        add_user(conn, username)
                    add_user_group(conn, username, proj)
                

        disconnect(conn)
