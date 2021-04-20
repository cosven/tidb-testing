#!/usr/bin/env python3

import logging
import os
from datetime import datetime

import gspread
import jira


# Setup logger
logging.basicConfig(
    format='[%(asctime)s %(name)s:%(lineno)d] [%(levelname)s]: %(message)s',
    level=logging.INFO)
logger = logging.getLogger()

try:
    JIRA_ENDPOINT = os.environ['JIRA_ENDPOINT']
    JIRA_USERNAME = os.environ['JIRA_USERNAME']
    JIRA_PASSWORD = os.environ['JIRA_PASSWORD']
except KeyError:
    raise SystemExit('Please set proper env vars.')

DEFAULT_FROM_DATE = datetime.strptime('2021-04-12', '%Y-%m-%d')

SPREAD_COLUMNS = [
    'oncall_id',
    'version',
    'status'
]


def list_oncall_issues(from_date=DEFAULT_FROM_DATE, from_issue='', max_results=1000):
    jira_cli = jira.JIRA('https://internal.pingcap.net/jira',
                         basic_auth=(JIRA_USERNAME, JIRA_PASSWORD))
    jql_tpl = 'project=oncall and created>={from_date} order by created ASC'
    jql_ctx = {'from_date': from_date.strftime(format='%Y-%m-%d')}
    jql = jql_tpl.format(**jql_ctx)
    logger.info(f'jql is: {jql}')
    issues = jira_cli.search_issues(jql, maxResults=max_results)
    results = []
    for issue in issues:
        versions = issue.fields.versions
        version_names = [version.name for version in versions]
        # for version_name in version_names:
        #     if version_name.startswith('v5.0') or version_name == 'master':
        results.append((issue.key,
                        issue.fields.status.name,
                        ','.join(version_names),
                        issue.fields.summary,
                        issue.fields.customfield_10321 or '',  # root cause
                        ))
    return results


def update_spreadsheet(issue_iterator):
    gc = gspread.oauth()
    sh = gc.open_by_key('1yEEcY2cXzcljgt5EWE6VTdlmmcox3QHg4ETR5IkZtwM')
    worksheet = sh.get_worksheet(0)

    # Get oncall id and row id mapping
    oncall_row_mapping = {}
    recorded_oncall_ids = worksheet.col_values(1)
    rows = worksheet.get(f'A2:C{len(recorded_oncall_ids) + 1}')
    for i, row in enumerate(rows):
        key, status, versions = row
        oncall_row_mapping[key] = (i + 2, (key, status, versions))

    # Update or add issues
    next_row_id = len(rows) + 2
    issues_to_be_added = []
    for issue in issue_iterator:
        key, *_ = issue
        if key in oncall_row_mapping:
            row_id, row = oncall_row_mapping[key]
            # Only compare issue status and versions
            if row[1:3] != issue[1:3]:
                # Update old data row by row
                worksheet.update(f'B{next_row_id}:D{next_row_id}', [issue[1:]])
                logger.info(f'row:{row_id} {row[0]} is updated.')
            else:
                logger.info(f'row:{row_id} {row[0]} is unchanged.')
        else:
            issues_to_be_added.append(list(issue))
    if issues_to_be_added:
        for issue in issues_to_be_added:
            key, _, _, summary, _ = issue
            if JIRA_ENDPOINT.endswith('/'):
                url = f'{JIRA_ENDPOINT}browse/{key}'
            else:
                url = f'{JIRA_ENDPOINT}/browse/{key}'
            issue_link = f'=HYPERLINK("{url}","{summary}")'
            issue[3] = issue_link  # summary
        table_range = f'A{next_row_id}:E{next_row_id + len(issues_to_be_added)}'
        # Add new issues in batch
        worksheet.append_rows(issues_to_be_added,
                              value_input_option='USER_ENTERED',
                              table_range=table_range)
        logger.info(f'{table_range} is added.')


def main():
    issues = list_oncall_issues(max_results=1000)
    update_spreadsheet(issues)


if __name__ == '__main__':
    main()
