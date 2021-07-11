import requests

"""
需要做参数化的： url data headers method

"""


class SendRequests(object):
    """cookie+session鉴权的请求封装"""

    def __init__(self):
        self.session = requests.session()

    def send(self, url, method, headers=None, params=None, data=None, json=None, files=None):
        method = method.lower()
        if method == "get":
            response = self.session.get(url=url, params=params, headers=headers)
        elif method == "post":
            response = self.session.post(url=url, json=json, data=data, files=files, headers=headers)
        elif method == "patch":
            response = self.session.patch(url=url, json=json, data=data, files=files, headers=headers)
        return response
