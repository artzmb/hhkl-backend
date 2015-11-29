#!/usr/bin/env python
# coding: utf-8
from fabric.api import env, sudo, run, cd, settings


def production_env():
    "Production environment"
    env.hosts = ['artzmb.com']
    env.user = 'hhkl'
    env.path = '/webapps/hhkl/hhkl-backend/hhkl'


def restart_webserver():
    "Restart the web server"
    sudo('supervisorctl restart hhkl')


def deploy():
    "Deploy the latest version of the site to the production server"
    with settings(host_string='artzmb.com'):
        production_env()
        with cd(env.path):
            run('git pull origin master')
            run('find . -name "*.mo" -print -delete')
            run('python manage.py collectstatic --noinput --settings=settings.production')

            run('pip install -r requirements.txt')

            restart_webserver()
