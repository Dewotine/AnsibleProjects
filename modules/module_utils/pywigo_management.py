#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import urllib

DOCUMENTATION='''
module: piwigo_user
author: Cédric Bleschet
description: Module to declare users in piwigo
options:
  username:
    description: User name
    required: yes
  password:
    description:User Password
    required: false
'''

EXAMPLES='''
- name: "Insert Piwigo user"
  pywigo_user:
    username: "test"
    pwg_token: "gdgjdklfjgmfld"
'''

RETURN = '''
results:
    description: user status
'''

class PiwigoManagement:
    def __init__(self, module, token, header, ansible_status, api_endpoint):
        self.module = module
        self.token = token
        self.header = header
        self.ansible_status = ansible_status
        self.api_endpoint = api_endpoint

    def _get_piwigo_list(self, ansible_list):
        return "|".join(ansible_list)

    def request_piwigo_login(self):
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        my_header = {}
        values = {'method': 'pwg.session.login',
                  'username': self.module.params["url_username"],
                  'password': self.module.params["url_password"]}

        my_data = urllib.urlencode(values)
        # Get connnexion
        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              method="POST")

        if info["status"] != 200:
            self.module.fail_json(msg="Failed to connect to piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] != "ok":
                self.module.fail_json(msg=content)
            else:
                my_header = {
                    'Cookie': info['set-cookie']
                }

        return my_header

    def get_admin_status(self):
        my_token = ""
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        url_method = "&method=pwg.session.getStatus"

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")
        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get session information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            my_token = content['result']['pwg_token']

        return my_token

    def get_userid(self, username):
        user_id = ""
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        url_method = "&method=pwg.users.getList&username=" + username + "&display=none"

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")
        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get user information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())

            user_id = content['result']['users'][0]['id']

        return user_id

    def get_userid_dict(self, username_list):
        user_id_dict = {}
        user_id = ""
        for username in username_list:
            user_id = self.get_userid(username)
            user_id_dict[user_id] = username

        return user_id_dict

    def finish_request(self):
        my_url = self.module.params["url"] + self.api_endpoint
        url_method = "&method=pwg.session.logout"

        fetch_url(self.module,
                  my_url + url_method,
                  headers=self.header,
                  method="GET")

        if self.ansible_status['result'] == 'Changed':
            self.module.exit_json(changed=True, msg=self.ansible_status['message'])
        elif self.ansible_status['result'] == 'Unchanged':
            self.module.exit_json(changed=False, msg=self.ansible_status['message'])
        else:
            self.module.fail_json(msg=self.ansible_status['message'])