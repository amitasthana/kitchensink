import os
import flask

from fulfil_client.oauth import Session
from fulfil_client import Client, BearerAuth, ClientError
from flask_babel import Babel
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from werkzeug.local import LocalProxy
from raven.contrib.flask import Sentry

from .settings import Config
# from flask.ext.celery import Celery

# Setup fulfil session
Session.setup(
    os.environ['FULFIL_APP_ID'], os.environ['FULFIL_APP_SECRET']
)

# celery = Celery()
babel = Babel()
toolbar = DebugToolbarExtension()
login_manager = LoginManager()
login_manager.login_view = "user.login"

# sentry
sentry = Sentry()

# login page is now converted to redirect, this message will only be visible
# when user comes back after login.
login_manager.login_message = None


def get_fulfil():
    subdomain = Config.FULFIL_SUBDOMAIN

    access_token = Config.FULFIL_OFFLINE_ACCESS_TOKEN

    if 'FULFIL_ACCESS_TOKEN' in flask.session:
        # Use current login token
        access_token = flask.session['FULFIL_ACCESS_TOKEN']

    if access_token is None:
        flask.abort(403)

    try:
        return Client(
            subdomain,
            auth=BearerAuth(access_token)
        )
    except ClientError, e:
        if e.code == 401:
            # unauthorized
            flask.abort(flask.redirect(flask.url_for('user.logout')))
        raise


fulfil = LocalProxy(get_fulfil)
