"""Aliyun API
Auth Params:
    :param action.ak: Access key for user.
    :param action.secret: Access secret for user.
    :param action.region_id: Servers accessed.

SingleSendMail:
    API Document：
        https://help.aliyun.com/document_detail/29444.html?spm=a2c4g.11186623.6.597.1c4510c3mIMFOm
    :param action.domain:
        Access domain name.
    :param action.version:
        API version.
    :param action.AccountName:
        The mailing address configured in the management console.
    :param action.AddressType:
        Address type. Value: 0 is random account number 1 is mailing address.
    :param action.ReplyToAddress:
        Whether to use the reply address configured in the
        management console (the address must be verified).
    :param action.ToAddress:
        Target address. Multiple email addresses can be
        separated by commas, with a maximum of 100 addresses.
    :param action.FromAlias:
        Sender's nickname, less than 15 characters in length. For example:
        the sender's nickname is set to "Xiaohong", the sending address is
        tests@example.com, and the sending address seen by the receiver is
        "Xiaohong" < tests @ example.com >.
    :param action.TagName:
        Label, negligible.
    :param **active_params:
        Subject: Email subject, it is recommended to fill in.
        HtmlBody: Email HTML body, limit 28K. Priority greater than 'Textbody'.
        TextBody: Email text body, limit 28K.
"""
import sys
import time
import threading
import collections

from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest

from . import logger
from . import dadclass

this = sys.modules[__name__]

__queue__ = collections.deque(maxlen=9999)


def __init__(config: dadclass.Dict):
    """
    Generate all action objects and
    establish pointers in the current module.
    """
    aliyun: dict = config.tools.aliyun
    init: dict = aliyun.pop('init', {})

    queue_mode: bool = init.pop('queue_mode', False)
    action_cycle: int = init.pop('action_cycle', 600)

    for name, conf in aliyun.items():

        for item in init.items():
            conf.setdefault(*item)

        setattr(this, name, Aliyun(conf, queue_mode))

    if queue_mode:
        threading.Thread(
            target=__exec__,
            args=(action_cycle,),
            daemon=True,
            name='AliyunAction'
        ).start()


class Aliyun:
    """Secondary encapsulation of `aliyunsdkcore`"""

    def __init__(self, action: dadclass.Dict, queue_mode: bool):
        self.queue_mode = queue_mode

        self.client = AcsClient(
            ak=action.ak,
            secret=action.secret,
            region_id=action.region_id,
            timeout=action.timeout)

        request = CommonRequest(
            domain=action.domain,
            version=action.version,
            action_name=action.name)

        request._method = action.method.upper()
        request._protocol_type = action.protocol_type
        request._accept_format = action.accept_format

        request._params = action

        self.request = request

    def __call__(self, sync: bool = False, **active_params):
        if sync or not self.queue_mode:
            self.request._params.update(active_params)
            logger.info(self.client.do_action(self.request))
        else:
            __queue__.appendleft((
                self.client,
                self.request,
                active_params))


def __exec__(action_cycle: int):
    while True:
        while __queue__:
            try:
                first: tuple = __queue__.pop()

                # Hard to deal with:
                if 'ConnectionError' in first:
                    continue

                count: int = __queue__.count(first)

                while first in __queue__:
                    __queue__.remove(first)

                client, request, active_params = first

                if count:
                    active_params['Subject'] += f' +{count}'

                request._params.update(active_params)
                logger.info(client.do_action(request))

            except Exception as e:
                logger.error(e)

        time.sleep(action_cycle)


send_mail: Aliyun
