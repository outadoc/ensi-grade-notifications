#!/usr/bin/env python3
import requests
import re
import urllib

def auth_step_0(session):
    # POST http:// ent.normandie-univ.fr
    response = session.post(
        url="http://ent.normandie-univ.fr",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        }
    )
    print('[STEP 0] Status Code: {status_code}'.format(
        status_code=response.status_code))
    print('[STEP 0] {nbreq} requests'.format(nbreq=len(response.history)))
    return response.text

def auth_step_1(session, cookieid):
    # POST http://wayf.normandie-univ.fr/WAYF.php
    response = session.post(
        url="http://wayf.normandie-univ.fr/WAYF.php",
        params={
            "entityID": "https://ent.normandie-univ.fr",
            "return": "https://ent.normandie-univ.fr/Shibboleth.sso/WAYF?SAMLDS=1&target=" + cookieid,
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        data={
            "user_idp": "https://shibboleth.ensicaen.fr/idp/shibboleth",
        }
    )
    print('[STEP 1] Status Code: {status_code}'.format(
        status_code=response.status_code))
    print('[STEP 1] {nbreq} requests'.format(nbreq=len(response.history)))
    return response.text

def auth_step_2(username, password, session, auth_token, jsessionid):
    # POST https://cas.ensicaen.fr/cas/login
    response = session.post(
        url="https://cas.ensicaen.fr/cas/login;jsessionid={jsessionid}".format(
            jsessionid=jsessionid),
        params={
            "service": "https://shibboleth.ensicaen.fr/idp/Authn/RemoteUser",
        },
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        data={
            "username": username,
            "password": password,
            "lt": auth_token,
            "execution": "e1s1",
            "_eventId": "submit",
        },
    )
    print('[STEP 2] {nbreq} requests'.format(nbreq=len(response.history)))
    print('[STEP 2] Status Code: {status_code}'.format(
        status_code=response.status_code))
    return response.text

def auth_step_3(session, relay_state, samlresponse):
    # POST https://ent.normandie-univ.fr/Shibboleth.sso/SAML2/POST
    response = session.post(
        url="https://ent.normandie-univ.fr/Shibboleth.sso/SAML2/POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        },
        data={
            "RelayState": relay_state,
            "SAMLResponse": samlresponse
        },
    )
    print('[STEP 3] {nbreq} requests'.format(nbreq=len(response.history)))
    print('[STEP 3] Status Code: {status_code}'.format(
        status_code=response.status_code))

def auth(session, username, password):
    """Authenticates the user in the given session."""
    # AUTH REQ #0
    res = auth_step_0(session)
    targetenc = re.search('action="(.*)"', res).group(1)
    targetdec = urllib.parse.unquote(urllib.parse.unquote(targetenc))
    cookieid = re.search('target=(.*)', targetdec).group(1)

    print("[STEP 0] got cookieid: " + cookieid)

    # AUTH REQ #1
    res = auth_step_1(session, cookieid)

    lt = re.search('name="lt" value="(.*)"', res).group(1)
    jsessionid = session.cookies.get("JSESSIONID")

    print("[STEP 1] got token: " + lt)
    print("[STEP 1] got jsessionid: " + jsessionid)

    # AUTH REQ #2
    res = auth_step_2(username, password, session, lt, jsessionid)
    saml = re.search('name="SAMLResponse" value="(.*)"', res).group(1)
    print("[STEP 2] got samlresponse of {saml_len} B".format(saml_len=len(saml)))

    # AUTH REQ #3
    auth_step_3(session, cookieid, saml)
    print("[STEP 3] Authenticated!")
