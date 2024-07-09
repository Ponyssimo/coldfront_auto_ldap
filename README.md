# coldfront_auto_ldap
A [ColdFront](https://coldfront.readthedocs.io/en/latest/) plugin that automatically creates ldap an ldap group when a project is approved and manages users in the group
## Installation
If you're using a virtual environment (following ColdFront's deployment instructions should have you make and use a virtual environment), make sure you're in the virutal environment first.
```
pip install git+https://github.com/Ponyssimo/coldfront_auto_ldap.git
```
## Configuration
Add the following to ColdFront's [local settings](https://coldfront.readthedocs.io/en/latest/config/#configuration-files):
```
INSTALLED_APPS += ["coldfront_plugin_auto_ldap"]
AUTO_LDAP_COLDFRONT_OU = Coldfront OU
```
The Coldfront OU is the LDAP OU this plugin will use. If not set, it will default to "coldfront"
## Admin Commands
This plugin provides the `ldap_add`, `ldap_search`, and `ldap_init` commands to Coldfront.

`ldap_add` is used to add or remove users, projects, or add users to existing projects in LDAP. This is used with the -u flag to specify the user, the -p flag to specify the project, and the -r flag to remove instead of add.
`ldap_search` is used to search for users, projects, or users within a project. This is used with the -u flag to specify the user, the -p flag to specify the project.
`ldap_init` is used for configuring the LDAP database with the specified OU for Coldfront and a users and projects OU within the Coldfront OU.

## Testing
For testing using a mock LDAP server, add
```
AUTO_LDAP_MOCK = True
AUTO_LDAP_MOCK_FILE = "/path/to/file"
AUTO_LDAP_INFO_FILE = "/path/to/file"
AUTO_LDAP_SCHEMA_FILE = "/path/to/file"
```
The mock file is where the mock DIT is stored. The info file and schema file are used to store the schema and configuration from your real server. These files will be created automatically, but you will need to make sure Coldfront has read and write access to these files.