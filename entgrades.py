#!/usr/bin/env python3
import requests
import re
import urllib
from bs4 import BeautifulSoup, SoupStrainer

ROOT_URL = "https://ent.normandie-univ.fr"
DOSSIER_URL = ROOT_URL + "/uPortal/f/u1240l1s214/p/esup-mondossierweb2.u1240l1n131/max/action.uP"

def get_grades_step_0(session):
    """Fetches the homepage."""
    response = session.get(
        url=ROOT_URL
    )
    print('[STEP 0] Status Code: {status_code}'.format(
        status_code=response.status_code))
    return response.text

def get_grades_step_1(session, page):
    """Fetches the 'dossier' page.
    Params:
    page -- the path of the 'dossier' page
    """
    response = session.get(
        url=ROOT_URL + page
    )
    print('[STEP 1] Status Code: {status_code}'.format(
        status_code=response.status_code))
    return response.text

def get_grades_step_2(session):
    """Fetches the page with the list of years and links to the results pages."""
    response = session.post(
        url=DOSSIER_URL,
        params={
            "pP_org.apache.myfaces.portlet.MyFacesGenericPortlet.VIEW_ID": "/stylesheets/etu/welcome.xhtml"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        data={
            "formMenu_SUBMIT": 1,
            "formMenu:_idcl": "formMenu:linknotes1",
            "formMenu:_link_hidden_": ""
        }
    )
    print('[STEP 2] Status Code: {status_code}'.format(
        status_code=response.status_code))
    return response.text

def get_grades_step_3(session, year):
    """Fetches the page with the results for the specified year.
    Params:
    year -- a custom object with JSF ids 'n' stuff
    """
    response = session.post(
        url=DOSSIER_URL,
        params={
            "pP_org.apache.myfaces.portlet.MyFacesGenericPortlet.VIEW_ID": "/stylesheets/etu/notes.xhtml"
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        data={
            year['param'] + "_SUBMIT": 1,
            year['param'] + ":_idcl": year['paramval'],
            year['param'] + ":_link_hidden_": "",
            'row': year['row']
        }
    )
    print('[STEP 3] Status Code: {status_code}'.format(
        status_code=response.status_code))
    return response.text

def get_grades(session):
    """Fetches all of the grades for the authenticated user for the given session.""" 
    res = get_grades_step_0(session)
    dossier_path = re.search('href="([\/a-zA-Z0-9\.]*)" title="Mon dossier"', res).group(1)

    print("[STEP 0] got dossier path: " + dossier_path)

    res = get_grades_step_1(session, dossier_path)

    # Get the list of years available (1A, 2A, 3A) and their identifiers
    res = get_grades_step_2(session)
    rgx = re.finditer('''<u>([A-Z\/0-9]*)<\/u><\/a><\/td><td width="30%"><a href="#" onclick="return oamSubmitForm\('([a-zA-Z0-9_]*)','([a-zA-Z0-9_:]*)',null,\[\['row','([0-9]*)'\]\]\);" id="([a-zA-Z0-9_:]*)">([a-zA-Z0-9 ]*)<\/a>''', res)

    years = []
    for match in rgx:
        years.append({
            "id": match.group(1),
            "name": match.group(6),
            "param": match.group(2),
            "paramval": match.group(5),
            "row": match.group(4)
        })

    print("[STEP 2] got years:", years)

    year_grades = []
    for year in years:
        res = get_grades_step_3(session, year)

        soup = BeautifulSoup(res, 'html.parser')
        table = soup.find('table', attrs={'class':'portlet-table'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')

        rawgrades = []
        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]

            data = []
            for ele in cols:
                if ele:
                    data.append(ele)

            rawgrades.append(data)

        grades = []
        gradergx = re.compile('^[0-9]{1,2}$')
        for line in rawgrades:
            if len(line) == 3 and gradergx.match(line[2]):
                grades.append({
                    "module_code": line[0],
                    "module_name": line[1],
                    "module_grade": int(line[2])
                })

        print("[STEP 3] got {nb} modules with grades for year {year}".format(
            nb=len(grades), year=year['name']))

        year_grades.append({
            'year':{'id': year['id'], 'label': year['name']},
            'grades': grades,
            'raw': rawgrades
        })

    return year_grades
