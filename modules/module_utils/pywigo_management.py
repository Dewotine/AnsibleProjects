#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import urllib

DOCUMENTATION='''
module: piwigo_user
author: Cédric Bleschet
description: Module to declare udsers in piwigo
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

    def get_groupid(self, groupname):
        group_id = ""
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        url_method = "&method=pwg.groups.getList&name=" + groupname

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")

        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get group information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            # If no group can be found set user_id to -1
            if content['result']['paging']['count'] == 0:
                group_id = -1
            # Store the group_id if exactly one answer is found
            elif content['result']['paging']['count'] == 1:
                group_id = content['result']['groups'][0]['id']
            # Failed otherwise
            else:
                self.module.fail_json(msg="An error occured while researching {0}".format(groupname))

        return group_id

    def get_userid(self, username):
        user_id = 0
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
            # If no user can be found set user_id to -1
            if content['result']['paging']['count'] == 0:
                user_id = -1
            # Store the userid if exactly one answer is found
            elif content['result']['paging']['count'] == 1:
                user_id = content['result']['users'][0]['id']
            # Failed otherwise
            else:
                self.module.fail_json(msg="An error occured while researching {0}".format(username))

        return user_id

    # Return a list to the piwigo format api
    def get_id_list(self, name_list, type):
        id_list = []
        type_id = ""
        assert (type in ["username", "group","category"])

        if type == "username":
            for name in name_list:
                type_id = self.get_userid(name)
                # Add to dictionnary only if user_id is valid (>0) <=> User has been found
                if type_id > 0:
                    id_list.append(type_id)
                # Used by piwigo_permission, the dictionnary returns must not contain  invalid user_id
                else:
                    self.module.fail_json(msg="Can not continue as name {0} of type {1} does not exist".format(name, type))
        elif type == "group":
            for name in name_list:
                type_id = self.get_groupid(name)
                if type_id > 0:
                    id_list.append(type_id)
                else:
                    self.module.fail_json(msg="Can not continue as name {0} of type {1} does not exist".format(name, type))

        # self.module.exit_json(changed=False, msg=user_id_list)
        return(id_list)

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