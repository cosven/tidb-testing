import json
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

from jira import JIRA


JIRA_URI = os.getenv('JIRA_URI')
JIRA_USERNAME = os.getenv('JIRA_USERNAME')
JIRA_PASSWORD = os.getenv('JIRA_PASSWORD')

jira = JIRA(JIRA_URI, auth=(JIRA_USERNAME, JIRA_PASSWORD))


def parse_hit(hit):
    source = hit['_source']

    case_id = source['name']
    reason = source['reason']
    url = source['annotations']['jenkins.build']
    duration = source['finished_at'] - source['started_at']

    return [case_id, reason, url, duration]


def get_owner(case_id):
    issue = jira.issue(case_id)
    return issue.fields.assignee.displayName, issue.fields.reporter.displayName


def main():
    with open('/tmp/hits.json') as f:
        hits = json.load(f)

    rows = []
    for hit in hits:
        rows.append(parse_hit(hit))

    case_owner_mapping = {}

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_case = {executor.submit(get_owner, row[0]): row[0]
                          for row in rows}
        for future in as_completed(future_to_case):
            case_id = future_to_case[future]
            try:
                owner, qa_owner = future.result()
            except:  # noqa
                print('WARN', case_id)
            else:
                case_owner_mapping[case_id] = (owner, qa_owner)

    with open('utf.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', lineterminator='\r\n',
                            quoting=csv.QUOTE_ALL)
        writer.writerow(['case id', 'failed reason', 'url',
                         'duration', 'owner', 'qa owner'])
        for row in rows:
            newrow = row.copy()
            newrow.extend(case_owner_mapping.get(row[0], ('Unknown', 'Unknown')))
            writer.writerow(newrow)


if __name__ == '__main__':
    main()
