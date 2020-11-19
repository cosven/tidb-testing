#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from enum import Enum

import click
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class Stage(Enum):
    running = 'running'
    end = 'end'


class Status(Enum):
    passed = 'passed'
    failed = 'failed'


@click.command()
@click.argument('channel')
@click.argument('case')
@click.argument('workflow')
@click.argument('stage')
@click.option('--status', default='passed')
def send_message(channel, case, workflow, stage, status):
    stage = Stage(stage)
    status = Status(status)

    client = WebClient(token=os.getenv('SLACK_BOT_TOKEN'))
    fields = []
    fields.append(('time', f'{datetime.now()}'))
    fields.append(('argo workflow', f'{workflow}'))
    fields.append(('stage', f'{stage.value}'))
    if stage is Stage.end and status is Status.failed:
        color = 'danger'
    else:
        color = 'good'
    if stage is Stage.end:
        fields.append(('status', f'{status.value}'))
        title = f"Tipocket test case `{case}` {stage.value} --- {status.value}"
    else:
        title = f"Tipocket test case `{case}` {stage.value} 🙏"

    channels = channel.split(',')
    for channel in channels:
        client.chat_postMessage(
            channel=channel,
            attachments=[
                {
                    "mrkdwn_in": ["text", "title"],
                    "color": color,
                    "title": title,
                    "text": f"",
                    "fields": [{'title': name, 'value': value, 'short': False}
                               for name, value in fields],
                }
            ])


if __name__ == '__main__':
    send_message()
