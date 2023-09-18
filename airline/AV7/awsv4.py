import sys, datetime, hashlib, hmac
import collections
import requests


class AwsV4:

    def __init__(self, request, service, host, region, endpoint, access_key, secret_key, date_stamp):
        """
        :param request:
        :param service: execute-api
        :param host: /eu-west-1/execute-api/aws4_request
        :param region:  eu-west-1
        :param endpoint:
        :param access_key: AKIATLNGK7P7IQRWEQ4J
        :param secret_key: 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
        :param date_stamp: 20220527T043300Z
        """
        self.request = request
        self.service = service
        self.host = host
        self.region = region
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.algorithm = 'AWS4-HMAC-SHA256'
        self.aws_datetime = date_stamp
        self.aws_date = self.aws_datetime[:8]
        self.headers = "accept;host;x-amz-date;x-api-key"
        self.x_api_key = "e94ab0cb5c614fc3b1ce49d89f6a-spa"

    @staticmethod
    def _hmac(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    @staticmethod
    def _sha256(text):
        hs256 = hashlib.sha256()
        hs256.update(bytes(text, encoding="utf-8"))
        return hs256.hexdigest()

    @property
    def hxbody(self):
        return self._sha256(self.request.body)

    @property
    def canonical_string(self):
        s = f"{self.request.method}\n{self.request.path}\n\naccept:{self.request.headers.get('accept')}" \
            f"\nhost:{self.host}\nx-amz-date:{self.aws_datetime}\nx-api-key:{self.x_api_key}\n\n" \
            f"accept;host;x-amz-date;x-api-key" \
            f"\n{self.hxbody}"
        # print("$$$$", s)
        return self._sha256(s)

    @property
    def signing_key(self):
        # print(self.secret_key)
        kDate = self._hmac(str('AWS4' + self.secret_key).encode('utf-8'), self.aws_date)
        kRegion = self._hmac(kDate, self.region)
        kService = self._hmac(kRegion, self.service)
        kSigning = self._hmac(kService, 'aws4_request')
        return kSigning

    @property
    def string_to_sign(self):
        string_to_sign = f"{self.algorithm}\n{self.aws_datetime}\n{self.aws_date}/{self.region}/{self.service}" \
                         f"/aws4_request\n{self.canonical_string}"
        return string_to_sign

    @property
    def signature(self):
        # print(self.signing_key)
        # print("self.string_to_sign\n", self.string_to_sign, "\n", "#" * 10)
        return hmac.new(self.signing_key, self.string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    def get_authorization(self):
        credential = f"{self.access_key}/{self.aws_date}/{self.region}/{self.service}/aws4_request"
        authorization_header = f"{self.algorithm} Credential={credential}, SignedHeaders={self.headers}," \
                               f" Signature={self.signature}"
        # print(authorization_header)
        return authorization_header


