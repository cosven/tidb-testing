#!/usr/bin/env python3

import logging
import os
import json
from base64 import b64decode
from datetime import datetime
from enum import Enum

import click
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Status(Enum):
    running = 'running'

    passed = 'passed'
    failed = 'failed'


def decode(s):
    return b64decode(bytes(s, 'utf-8')).decode('utf-8')


@click.command()
@click.argument('channel')
@click.argument('case')
@click.argument('status')
@click.option('--kv', multiple=True)  # simple kv
@click.option('--b64encodedkvs', default='')  # complex kv
def send_message(channel, case, status, kv, b64encodedkvs):
    status = Status(status)
    client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    fields = []
    fields.append(('status', f'{status.value}'))
    fields.append(('time', f'{datetime.now()}'))

    if status is Status.running:
        color = '#268bd2'  # blue, copied from solorized theme
        title = f"Test case `{case}` {status.value} 🙏"
    else:
        if status is Status.failed:
            color = 'danger'
        else:
            color = 'good'
        title = f"Test case `{case}` {status.value} --- {status.value}"

    if kv:
        for each in kv:
            key, value = each.split('=')
            fields.append((key, value))

    kv_pairs_str = b64decode(b64encodedkvs).decode('utf-8') or '{}'
    kv_pairs = json.loads(kv_pairs_str)
    for key, value in kv_pairs.items():
        fields.append((key, value))

    channels = channel.split(',')
    for channel_ in channels:
        try:
            client.chat_postMessage(
                channel=channel_,
                attachments=[{
                        "mrkdwn_in": ["text", "title"],
                        "color": color,
                        "title": title,
                        "text": "",
                        "fields": [{'title': name,
                                    'value': value,
                                    'short': name in ('status', 'time')}
                                   for name, value in fields],
                    }]
            )
        except:  # noqa
            logging.exception('send message failed')


if __name__ == '__main__':
    send_message()
