import os
import logging
from subprocess import call

from charms.reactive import when, hook
from charms.reactive import is_state, set_state, remove_state
from charmhelpers import fetch
from charmhelpers.core import hookenv
from charmhelpers.core import templating
from charmhelpers.core.hookenv import (
    config, relation_set, relation_get,
    local_unit, related_units, remote_unit)


logger = logging.getLogger('serial-vault')


@hook('install')
def install():
    if is_state('serial-vault.available'):
        return
    logger.info("***install_serial_vault")
    print("***install_serial_vault")

    # Install the dependency packages
    install_packages()

    hookenv.status_set('maintenance', 'Waiting for database')
    set_state('serial-vault.available')


@hook('config-changed')
def config_changed():
    logger.info("***config_changed_serial_vault")
    print("***config_changed_serial_vault")


@hook(
    'database-relation-changed')
def db_relation_changed(*args):
    logger.info("***DB RELATION CHANGED - setup_serial_vault")
    print("***DB RELATION CHANGED - setup_serial_vault")

    database = {}

    for db_unit in related_units():
        # if relation_get('database', db_unit) != config('database'):
        #     continue  # Not yet acknowledged requested database name.

        remote_state = relation_get('state', db_unit)
        if remote_state in ('master', 'standalone'):
            database = relation_get(unit=db_unit)

    # Configure and install the snap when the database is ready
    install_snap(database)

    hookenv.status_set('active', '')
    set_state('serial-vault.active')


def install_packages():
    config = hookenv.config()
    hookenv.status_set('maintenance', 'Installing packages')
    packages = ['snapcraft']
    fetch.apt_install(fetch.filter_installed_packages(packages))
    logger.info("***install packages done")
    print("***install packages done")


def install_snap(postgres):
    hookenv.status_set('maintenance', 'Install snap')
    logger.info('*** INSTALL SNAP')
    print('*** INSTALL SNAP')
    logger.info(postgres)
    print(postgres)

    # Configure the snapcraft file to deploy the requested service
    configure_snapcraft()

    # Fetch the snap assets using snapcraft
    call(['snapcraft', 'pull'])

    # Override the settings.yaml file in the parts directory
    configure_service(postgres)

    # Build the snap using snapcraft
    call(['snapcraft'])

    # Install the snap
    call(['sudo', 'snap', 'install', 'serial-vault_0.1_amd64.snap'])

    hookenv.status_set('maintenance', 'Installed snap')


def configure_snapcraft():
    hookenv.status_set('maintenance', 'Configuring snapcraft')
    config = hookenv.config()
    templating.render(
        source='snapcraft.yaml',
        target='snapcraft.yaml',
        context={
            'service_type': config['service_type'],
        }
    )
    hookenv.status_set('maintenance', '')


def configure_service(postgres):
    hookenv.status_set('maintenance', 'Configuring service')
    config = hookenv.config()
    templating.render(
        source='settings.yaml',
        target='parts/assets/src/settings.yaml',
        context={
            'keystore_secret': config['keystore_secret'],
            'db': postgres,
        }
    )
