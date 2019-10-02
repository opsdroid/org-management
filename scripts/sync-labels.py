#!/usr/bin/env python3

import getopt
import json
import os
from pprint import pprint
import re
import sys

import requests


GITHUB_API_URL = 'https://api.github.com'
SESSION = requests.Session()


def show_help():
    print('sync-labels.py -t <label-config> -o <github-org>')


def parse_args(argv):
    args = {}

    try:
        opts, _ = getopt.getopt(argv,"ht:o:",["label-config=","org="])
    except getopt.GetoptError:
        show_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            show_help()
            sys.exit()
        elif opt in ("-t", "--label-config"):
            args["label_config"] = arg
        elif opt in ("-o", "--org"):
            args["org"] = arg

    return args


def load_labels(label_config):
    with open(label_config) as data_file:
        data = json.load(data_file)

    return data


def get_repos(org):
    page = 1
    last_page = 1
    repos = []
    while page <= last_page:
        response = SESSION.get('{}/orgs/{}/repos?page={}'.format(GITHUB_API_URL, org, page))
        if response.status_code < 300:
            _, last_page_header = response.headers['Link'].split(',')
            last_page = int(re.search(r"page\=([0-9+])", last_page_header).group(1))
            repos = repos + [repo["url"] for repo in response.json()]
            page += 1
        else:
            print("Unable to get repos from GitHub")
            print(response.json()["message"])
            sys.exit(1)
    return repos


def get_current_labels(repo):
    page = 1
    last_page = 1
    labels = []
    while page <= last_page:
        response = SESSION.get('{}/labels?page={}'.format(repo, page))
        if response.status_code < 300:
            _, last_page_header = response.headers['Link'].split(',')
            last_page = int(re.search(r"page\=([0-9+])", last_page_header).group(1))
            labels = labels +  [label for label in response.json()]
        else:
            print("Unable to get labels from GitHub")
            sys.exit(1)
    return labels


def add_label(repo, new_label):
    print("Adding new label {}".format(new_label["name"]))
    response = SESSION.post('{}/labels'.format(repo), json=new_label)
    if response.status_code != 201:
        print("Failed to add")
        print(response.json()["message"])
        sys.exit(1)


def update_label(current_label, new_label):
    if new_label["color"] != current_label["color"]:
        print("Updating color of {}".format(new_label["name"]))
        response = SESSION.patch(current_label["url"], json=new_label)
        if response.status_code != 200:
            print("Failed to update")
            print(response.json()["message"])
            sys.exit(1)


def remove_label(current_label):
    print("Removing label {}".format(current_label["name"]))
    response = SESSION.delete(current_label["url"])
    if response.status_code != 204:
        print("Failed to remove")
        print(response.json()["message"])
        sys.exit(1)


def update_repo_labels(repo, labels):
    current_labels = get_current_labels(repo)
    print("Updating {}".format(repo))
    for new_label in labels:
        if new_label["name"] in [current_label["name"] for current_label in current_labels]:
            current_label = [current_label for current_label in current_labels if current_label["name"] == new_label["name"]][0]
            update_label(current_label, new_label)
        else:
            add_label(repo, new_label)
    for current_label in current_labels:
        if current_label["name"] not in [label["name"] for label in labels]:
            remove_label(current_label)
    print("Done")


def main(argv):
    args = parse_args(argv)
    try:
        SESSION.headers.update({"Authorization": "token {}".format(os.environ['GITHUB_TOKEN'])})
    except KeyError:
        print("Environment variable GITHUB_TOKEN missing.")
        sys.exit(1)
    labels = load_labels(args.get('label_config', 'config/labels.json'))
    repos = get_repos(args.get('org', 'opsdroid'))
    for repo in repos:
        update_repo_labels(repo, labels)

if __name__ == '__main__':
    main(sys.argv[1:])
