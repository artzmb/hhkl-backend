#!/usr/bin/env python
# coding: utf-8
from fabric.api import env, sudo, run, cd, settings, prefix
from contextlib import contextmanager as _contextmanager

def production_env():
    "Production environment"
    env.hosts = ['artzmb.com']
    env.user = 'hhkl'
    env.path = '/webapps/hhkl'
    env.activate = 'source /webapps/hhkl/venv/bin/activate'
    env.app = '/webapps/hhkl/hhkl-backend/hhkl'

@_contextmanager
def virtualenv():
    with cd(env.path):
        with prefix(env.activate):
            yield

def restart_webserver():
    "Restart the web server"
    sudo('supervisorctl restart hhkl')


def deploy():
    "Deploy the latest version of the site to the production server"
    with settings(host_string='artzmb.com'):
        production_env()
        with virtualenv():
            with cd(env.app):
                run('git pull origin master')
                run('find . -name "*.mo" -print -delete')
                run('pip install -r requirements.txt')
                run('python manage.py collectstatic --noinput --settings=settings.production')
                run('python manage.py migrate --settings=settings.production')

                restart_webserver()
