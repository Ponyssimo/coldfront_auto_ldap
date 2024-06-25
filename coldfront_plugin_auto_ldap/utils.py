import logging
import os
from ldap3 import Server, Connection, Tls, get_config_parameter, set_config_parameter, SASL, ALL, MOCK_SYNC, ALL_ATTRIBUTES, SUBTREE
from ldap3.core.exceptions import LDAPException

from coldfront.core.utils.common import import_from_settings

logger = logging.getLogger(__name__)

LDAP_SERVER_URI = import_from_settings("LDAP_USER_SEARCH_SERVER_URI")
LDAP_USER_SEARCH_BASE = import_from_settings("LDAP_USER_SEARCH_BASE")
LDAP_BIND_DN = import_from_settings("LDAP_USER_SEARCH_BIND_DN", None)
LDAP_BIND_PASSWORD = import_from_settings("LDAP_USER_SEARCH_BIND_PASSWORD", None)
LDAP_CONNECT_TIMEOUT = import_from_settings("LDAP_USER_SEARCH_CONNECT_TIMEOUT", 2.5)
LDAP_USE_SSL = import_from_settings("LDAP_USER_SEARCH_USE_SSL", True)
LDAP_USE_TLS = import_from_settings("LDAP_USER_SEARCH_USE_TLS", False)
LDAP_SASL_MECHANISM = import_from_settings("LDAP_USER_SEARCH_SASL_MECHANISM", None)
LDAP_SASL_CREDENTIALS = import_from_settings("LDAP_USER_SEARCH_SASL_CREDENTIALS", None)
LDAP_PRIV_KEY_FILE = import_from_settings("LDAP_USER_SEARCH_PRIV_KEY_FILE", None)
LDAP_CERT_FILE = import_from_settings("LDAP_USER_SEARCH_CERT_FILE", None)
LDAP_CACERT_FILE = import_from_settings("LDAP_USER_SEARCH_CACERT_FILE", None)

OU = import_from_settings("AUTO_LDAP_COLDFRONT_OU", 'COLDFRONT')
MOCK = import_from_settings("AUTO_LDAP_MOCK", False) #whether to use a mock server
MOCK_FILE = import_from_settings("AUTO_LDAP_MOCK_FILE", None) #json file with mock server schema
MOCK_INFO = import_from_settings("AUTO_LDAP_INFO_FILE", None)
MOCK_SCHEMA = import_from_settings("AUTO_LDAP_SCHEMA_FILE", None)

# parse a given uri with OU into a format usable in LDAP operations
def parse_uri(uri=LDAP_SERVER_URI, ou = OU, shortened=False):
    parsed = ""
    if "://" in uri:
        uri = uri.split("/")[2]
    else:
        uri = uri.split("/")[0]
    partURI = uri.split(".")
    if ou == None or ou == "":
        ou = 'COLDFRONT'
    if not shortened:
        parsed = 'ou=' + ou
    for part in partURI:
        parsed += ',dc=' + part
    if shortened:
        parsed = parsed[1:]
    return parsed

URI = parse_uri()

# connects to an ldap server based on parameters in Coldfront settings
def connect(uri = URI):
    tls = None
    if LDAP_USE_TLS:
        tls = Tls(
            local_private_key_file=LDAP_PRIV_KEY_FILE,
            local_certificate_file=LDAP_CERT_FILE,
            ca_certs_file=LDAP_CACERT_FILE,
        )
    server = Server(LDAP_SERVER_URI, use_ssl=LDAP_USE_SSL, connect_timeout=LDAP_CONNECT_TIMEOUT, tls=tls, get_info=ALL)
    conn_params = {"auto_bind": True}
    if LDAP_SASL_MECHANISM:
        conn_params["sasl_mechanism"] = LDAP_SASL_MECHANISM
        conn_params["sasl_credentials"] = LDAP_SASL_CREDENTIALS
        conn_params["authentication"] = SASL
    conn = Connection(server, LDAP_BIND_DN, LDAP_BIND_PASSWORD, **conn_params)
    if MOCK:
        if not os.path.exists(MOCK_FILE):
            os.mknod(MOCK_FILE)
            if conn.search(URI, '(objectclass=*)', attributes=ALL_ATTRIBUTES):
                conn.response_to_file(MOCK_FILE, raw=True)
        server.info.to_file(MOCK_INFO)
        server.schema.to_file(MOCK_SCHEMA)
        fake_server = Server.from_definition('my_fake_server', MOCK_INFO, MOCK_SCHEMA)
        connection = Connection(fake_server, user='cn=my_user,ou=test,o=lab', password='my_password', client_strategy=MOCK_SYNC)
        try:
            connection.strategy.entries_from_json(MOCK_FILE)
        except:
            pass
        connection.bind()
        conn.unbind()
        return connection
    return conn

# writes current DIT to file if MOCK is set to true, then unbinds from the connection
def disconnect(conn):
    if MOCK:
        if conn.search(URI, '(objectclass=*)', attributes=ALL_ATTRIBUTES):
            conn.response_to_file(MOCK_FILE, raw=True)
    conn.unbind

# searches for a given ldap group in the Coldfront OU
def search_project(conn, project, uri = URI):
    search_base = 'ou=projects,' + uri
    search_scope = LEVEL
    search_filter = '(cn=' + project + ')'
    try:
        conn.search(search_base=search_base,
                    search_filter=search_filter,
                    search_scope=search_scope)
    except LDAPException as e:
        logger.warn(e)

# adds an ldap group to the Coldfront OU
def add_project(conn, project, pi, pi_cn, pi_sn, uri = URI):
    add_user(conn, pi, pi_cn, pi_sn)
    try:
        response = conn.add('cn=' + project + ',ou=projects,' + uri, 'groupOfNames', {'cn': project, 'member': 'uid=' + pi + ',ou=users,' + uri})
    except LDAPException as e:
        logger.warn(e)

# searches for a given user by UID in the Coldfront OU
def search_user(conn, username, uri = URI):
    search_base = 'ou=users,' + uri
    search_scope = SUBTREE
    search_filter = '(uid=' + username + ')'
    try:
        conn.search(search_base=search_base,
                    search_filter=search_filter,
                    search_scope=search_scope)
    except LDAPException as e:
        logger.warn(e)

# searches for a given user by UID in a given group in the Coldfront OU
def search_user_group(conn, username, project, uri = URI):
    search_base = 'cn=' + project + ',ou=projects,' + uri
    search_scope = SUBTREE
    search_filter = '(uid=' + username + ')'
    try:
        conn.search(search_base=search_base,
                    search_filter=search_filter,
                    search_scope=search_scope)
    except LDAPException as e:
        logger.warn(e)

# creates a new user in the Coldfront OU
def add_user(conn, username, cn, sn, uri = URI):
    try:
        response = conn.add('uid=' + username + ',ou=users,' + uri, 'inetOrgPerson', {'cn': cn, 'sn': sn})
    except LDAPException as e:
        logger.warn(e)

# adds a given user to a given group in the Coldfront OU
def add_user_group(conn, username, project, uri = URI):
    search_project(conn, project, uri)

    if len(conn.entries) != 0:
        try:
            conn.modify('cn=' + project + ',ou=projects' + uri, {'member': [(MODIFY_ADD, ['uid=' + username + ',ou=users,' + uri])]})
        except LDAPException as e:
            logger.warn(e)
            return -1

# removes a given user from a given group in the Coldfront OU
def remove_user_group(conn, username, project, uri = URI):
    search_project(conn, project, uri)

    if len(conn.entries) != 0:
        try:
            conn.modify('cn=' + project + ',ou=projects' + uri, {'member': [(MODIFY_DELETE, ['uid=' + username])]})
        except LDAPException as e:
            logger.warn(e)
            return -1
