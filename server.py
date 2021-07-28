import traceback
import os

from flask import Response, Flask, request, make_response, send_file
from flask_swagger_ui import get_swaggerui_blueprint

from helpers import flask_json_response
from service import Service

# from sentry_sdk.integrations.flask import FlaskIntegration

IS_SUICIDED = False


class Server(object):

    def __init__(self, flask_name):

        self.name = flask_name

        self.server = FlaskAppWrapper(flask_name)

        self.server.app.register_blueprint(
            get_swaggerui_blueprint(
                '/swagger',
                'swagger.yaml',
                config={'app_name': 'Vision'}
            ),
            url_prefix='/swagger'
        )

        self.server.add_handler_errors(500, self.handle_errors)

        self.server.add_endpoint(endpoint='/', endpoint_name='health',
                                 handler=self.get_health, methods=['GET'])

        self.server.add_endpoint(endpoint='/get-data-bcb-ptax', endpoint_name='get_data_bcb_ptax',
                                 handler=self.get_data_bcb_ptax, methods=['GET'])

        self.server.add_endpoint(endpoint='/get-data-bcb-ptax/usd', endpoint_name='get_data_bcb_ptax_usd',
                                 handler=self.get_data_bcb_ptax_usd, methods=['GET'])

        self.server.add_endpoint(endpoint='/get-data-bcb-ptax/euro', endpoint_name='get_data_bcb_ptax_euro',
                                 handler=self.get_data_bcb_ptax_euro, methods=['GET'])

        self.server.add_endpoint(endpoint='/swagger/swagger.yaml', endpoint_name='swagger_yaml',
                                 handler=self.send_swagger_yaml)

        self.service = Service()

    def get_health(self):
        global IS_SUICIDED

        if not IS_SUICIDED:
            return flask_json_response({'success': True}, 200)

        return flask_json_response(None, 500)

    def handle_errors(self, error):
        status_code = 500

        if not isinstance(error, Exception):
            # bugsnag enter here
            traceback.print_exc()
            return flask_json_response("Internal server error", status_code)

        if hasattr(error, 'status_code'):
            status_code = error.status_code

        if os.environ.get('MES_ENV', None) == 'dev':
            response = error
        elif hasattr(error, 'to_dict'):
            response = error.to_dict()
        else:
            response = error.args[0]

        return flask_json_response(response, status_code)

    def get_data_bcb_ptax_usd(self):
        return self.get_data_bcb_ptax('61')

    def get_data_bcb_ptax_euro(self):
        return self.get_data_bcb_ptax('222')

    def get_data_bcb_ptax(self, currency):
        currency_names = {
            '61': 'dolar',
            '222': 'euro'
        }
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        dolar = self.service.get_data_bcb_ptax(currency, start_date, end_date)
        # euro = self.service.get_data_bcb_ptax('222', request.args.get('start_date'), request.args.get('end_date'))
        output = make_response(dolar)
        start_date_snake = start_date.replace('-', '_')
        end_date_snake = end_date.replace('-', '_')
        currency_name = currency_names.get(currency)
        output.headers["Content-Disposition"] = f"attachment; filename={currency_name}_{start_date_snake}_{end_date_snake}.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    def send_swagger_yaml(self):
        return send_file(f'{os.path.dirname(__file__)}/swagger.yaml')


class EndpointAction(object):

    def __init__(self, name, action_name, action, request_validator=None):
        self.name = name
        self.action = action
        self.action_name = action_name
        self.request_validator = request_validator
        self.response = Response(status=200, headers={})

    def __call__(self, **args):
        #  if is not health check send to sentry
        if self.action.__name__ != 'get_health':

            if self.request_validator is not None:

                args['request_validator'] = self.request_validator
                self.request_validator.set_request(request)
                if self.request_validator.handle():
                    messages = self.request_validator.get_messages_validation().to_dict()
                    self.request_validator.clear_cache_request()
                    return flask_json_response(messages,
                                               400)

            self.response = self.action(**args)
        else:
            self.response = self.action(**args)
        return self.response


class FlaskAppWrapper(object):
    _app = None

    def __init__(self, name):
        self.name = name
        self._app = Flask(name)

    def run(self, host, port, debug, threaded):
        self._app.run(host, port, debug, threaded)

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None, request_validator=None,
                     **options):
        self._app.add_url_rule(endpoint, endpoint_name, EndpointAction(self.name, endpoint, handler, request_validator),
                               **options)

    def add_handler_errors(self, code=None, handler=None, **options):
        self._app.register_error_handler(code, handler, **options)

    @property
    def app(self):
        return self._app
