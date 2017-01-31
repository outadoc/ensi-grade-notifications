#!/usr/bin/env python3
import pprint
import pickle
import os
import sys

import requests

import entlogin
import entgrades

FILE_NAME = 'last_grades'

def save_obj(obj, name):
    with open('obj/'+ name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name):
    with open('obj/' + name + '.pkl', 'rb') as f:
        return pickle.load(f)

def send_maker_event(event, value1=None, value2=None, value3=None):
    try:
        response = requests.get(
            url="https://maker.ifttt.com/trigger/{event}/with/key/{api_key}".format(
                event=event,
                api_key=os.environ['MAKER_API_KEY']
            ),
            params={
                "value1": value1,
                "value2": value2,
                "value3": value3,
            },
        )
        print('sent {event} ({value1}, {value2}, {value3}) {status_code}'.format(
            event=event,
            value1=value1,
            value2=value2,
            value3=value3,
            status_code=response.status_code
        ))
    except requests.exceptions.RequestException:
        print('Maker HTTP Request failed')

def notify_new_grade(module):
    send_maker_event("ent_new_grade", module['module_name'], module['module_grade'])

def notify_deleted_grade(module):
    send_maker_event("ent_deleted_grade", module['module_name'])

def notify_edited_grade(oldmodule, newmodule):
    send_maker_event("ent_edited_grade", newmodule['module_name'], 
        oldmodule['module_grade'], newmodule['module_grade'])

def main():
    s = requests.Session()
    pp = pprint.PrettyPrinter(indent=4)

    if not "ENT_USERNAME" in os.environ or not "ENT_PASSWORD" in os.environ:
        print("error: set your credentials in the ENT_USERNAME and ENT_PASSWORD environment variables")
        sys.exit(1)

    if not "MAKER_API_KEY" in os.environ:
        print("error: set your Maker API key in the MAKER_API_KEY environment variable")
        sys.exit(1)

    entlogin.auth(s, os.environ['ENT_USERNAME'], os.environ['ENT_PASSWORD'])
    res = entgrades.get_grades(s)

    # Copy data to a nicer dictionary
    grades = {}
    for year in res:
        grades[year['year']['id']] = year['grades']

    try:
        oldyears = load_obj(FILE_NAME)

        # Analyze differences between the grades we fetched and the ones that
        # we fetched last time
        for year, modules in grades.items():
            if oldyears[year]:
                # For each module in the new list, compare to the old modules
                for module in modules:
                    found = False
                    for oldmodule in oldyears[year]:
                        if module['module_code'] == oldmodule['module_code']:
                            found = True
                            if module['module_grade'] != oldmodule['module_grade']:
                                # If we already had this module but the grade is different
                                # for some reason
                                notify_edited_grade(oldmodule, module)
                            break

                    # If we have this module in the new list, but not the old one
                    if not found:
                        notify_new_grade(module)

                # For each module in the old list, compare to the new modules
                for oldmodule in oldyears[year]:
                    found = False
                    for module in modules:
                        if module['module_code'] == oldmodule['module_code']:
                            found = True
                            break

                    if not found:
                        # We used to have the grade for this module but we don't
                        # anymore for some reason
                        notify_deleted_grade(oldmodule)

    except FileNotFoundError as ex:
        print("no existing grades on disk, skipping checks")

    save_obj(grades, FILE_NAME)

main()
