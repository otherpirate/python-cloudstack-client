from base64 import b64encode
from hmac import new
from hashlib import sha1
from urllib.parse import quote_plus
from requests import get, post


class BaseClient(object):

    def __init__(self, endpoint, secret_key, api_key):
        self.endpoint = endpoint
        self.secret_key = secret_key
        self.api_key = api_key

    def _build_params(self, **kwargs):
        kwargs['apiKey'] = self.api_key
        kwargs['response'] = 'json'

        params = []
        for key in sorted(kwargs.keys()):
            params.append('{}={}'.format(key, kwargs[key]))

        return '&'.join(params)

    def _generate_signature(self, query):
        digest = new(
            self.secret_key.encode('utf-8'),
            msg=query.lower().encode('utf-8'), digestmod=sha1
        ).digest()

        return quote_plus(b64encode(digest))

    def _add_signature(self, query):
        signature = self._generate_signature(query)
        return query + '&signature=' + signature

    def _request(self, **kwargs):
        query = self._build_params(**kwargs)
        query = self._add_signature(query)

        command = kwargs.get("command", "GET")
        if command == "POST":
            return post(self.endpoint, query)

        return get(self.endpoint + "?" + query)



class CloudStackClient(BaseClient):

    def deploy_virtual_machine(
        self, service_offering_id, template_id, zone_id, **kwargs
    ):
        return self._request(
            command='deployVirtualMachine',
            serviceofferingid=service_offering_id, templateid=template_id,
            zoneid=zone_id, **kwargs
        )
