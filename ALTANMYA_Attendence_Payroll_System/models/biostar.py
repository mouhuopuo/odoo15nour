import requests
import json
import urllib3
import logging
logger = logging.getLogger('odoo')

def get_events(env,bio_id,last_index,limit=20000):
    ret_fnc = [{"error": "unknown0"}]
    rec_settings = env['od.fp.settings'].sudo().search([('setting_name', '=', 'biostar ip')], limit=1)
    api_ip = rec_settings.setting_value_text
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    url_events = "https://"+api_ip+"/api/events/search"
    ret_fnc=[{"error":"unknown1"}]
    sessionid =get_session(env,api_ip)
    ret_fnc = [{"error": str(sessionid)}]
    errnum="000"
    try:
        if sessionid:
            # from_dt=from_date+"T00:00:00.000Z" #"2023-05-01T16:00:00.000Z"
            # to_dt=from_date+"T00:00:00.000Z"
            event_query = {"Query": {"limit": limit, "conditions": [{
                "column": "index", "operator": 3, "values": [last_index+1,last_index+1+limit]},
                {"column": "device_id", "operator": 0, "values": [bio_id]}
            ], }}

            session_header = {'content-type': 'application/json', 'bs-session-id': sessionid}
            response = requests.post(url_events, json=event_query, headers=session_header, verify=False)

            if response.status_code == 200:
                bio_events=response.json()
                errnum = "001"
                evv=bio_events['EventCollection'].get('rows')
                errnum = "002"
                ret_fnc= [{'index':x.get('index'),'datetime':x['datetime'],'status': (1 if 'ENTRANCE' in x['device_id'].get('name') else 2),'user_id':x['user_id'].get('user_id') } for x in evv if ( ("4867" in x['event_type_id'].get('code') or "4865" in x['event_type_id'].get('code')  ) and ('user_id' in x) and (('ENTRANCE' in x['device_id'].get('name'))or ('EXIT' in x['device_id'].get('name')))) ]

            else:
                ret_fnc= [{"error":"download from biostar failure"}]
    except Exception as e:
            ret_fnc= [{"error": "Plus"+errnum+str(e)}]
    return ret_fnc


def get_session(env,api_ip):
    ssid=None
    errocc = False
    # rec_settings = self.env['od.fp.settings'].sudo().search([('setting_name', '=', settingname)], limit=1)
    rec_settings = env['od.fp.settings'].sudo().search([('setting_name', '=', 'biostar session')], limit=1)
    if False:
        ssid= rec_settings.setting_value_text
    else:
        try:
            rec_settings = env['od.fp.settings'].sudo().search([('setting_name', '=', 'biostar user')], limit=1)
            username = rec_settings.setting_value_text
            rec_settings = env['od.fp.settings'].sudo().search([('setting_name', '=', 'biostar password')], limit=1)
            passw = rec_settings.setting_value_text
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            url_login = "https://" + api_ip + "/api/login"
            json_login = {"User": {"login_id": username, "password": passw}}
            ret_fnc = {"error": "unknown 5"}
            response = requests.post(url_login, json=json_login, verify=False)
            if response.status_code == 200:
                ssid = response.headers['bs-session-id']
                sss=env['od.fp.settings'].sudo().search([('setting_name', '=', 'biostar session')], limit=1)
                sss.update({'setting_value_text': ssid})
            else:
                raise odoo.exceptions.Warning("Failed to get session")
        except Exception as e:
            errocc = True
        finally:
            if errocc:
                raise odoo.exceptions.Warning("Failed to connect to biostart service")
            else:
                return ssid





