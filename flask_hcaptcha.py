"""
The new Google ReCaptcha implementation for Flask without Flask-WTF
Can be used as standalone
"""

__NAME__ = "Flask-hCaptcha"
__version__ = "0.5.0"
__license__ = "MIT"
__author__ = "Knugi (originally ReCaptcha by Mardix)"
__copyright__ = "(c) 2020 Knugi (originally ReCaptcha by Mardix 2015)"

try:
    from flask import request
    from jinja2 import Markup
    import requests
except ImportError as ex:
    print("Missing dependencies")


class DEFAULTS(object):
    IS_ENABLED = True

class hCaptcha(object):

    VERIFY_URL = "https://hcaptcha.com/siteverify"
    site_key = None
    secret_key = None
    is_enabled = False

    def __init__(self, app=None, site_key=None, secret_key=None, is_enabled=True, **kwargs):
        if site_key:
            self.site_key = site_key
            self.secret_key = secret_key
            self.is_enabled = is_enabled

        elif app:
            self.init_app(app=app)

    def init_app(self, app=None):
        self.__init__(site_key=app.config.get("HCAPTCHA_SITE_KEY"),
                      secret_key=app.config.get("HCAPTCHA_SECRET_KEY"),
                      is_enabled=app.config.get("HCAPTCHA_ENABLED", DEFAULTS.IS_ENABLED))

        @app.context_processor
        def get_code():
            return dict(hcaptcha=Markup(self.get_code()))

    def get_code(self):
        """
        Returns the new ReCaptcha code
        :return:
        """
        return "" if not self.is_enabled else ("""
        <script src="https://hcaptcha.com/1/api.js" async defer></script>
        <div class="h-captcha" data-sitekey="{SITE_KEY}"></div>
        """.format(SITE_KEY=self.site_key))

    def verify(self, response=None, remote_ip=None):
        if self.is_enabled:
            data = {
                "secret": self.secret_key,
                "response": response or request.form.get('h-recaptcha-response'),
                "remoteip": remote_ip or request.environ.get('REMOTE_ADDR')
            }

            r = requests.get(self.VERIFY_URL, params=data)
            return r.json()["success"] if r.status_code == 200 else False
        return True
