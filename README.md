# About
This charm installs a Serial Vault service, https://github.com/ubuntu-core/identity-vault

# Install
After bootstrapping a juju environment, run:
```bash
juju deploy postgresql

juju deploy serial-vault serial-vault         # The signing service
juju add-relation serial-vault:database postgresql:db-admin

juju deploy serial-vault serial-vault-admin   # The admin service
juju add-relation serial-vault-admin:database postgresql:db-admin
juju config serial-vault-admin service_type=admin

# Expose the services
juju expose serial-vault         # port 8080
juju expose serial-vault-admin   # port 8081
```

Note: the db-admin relation is needed for the PostgreSQL service currently to avoid object ownership issues.
