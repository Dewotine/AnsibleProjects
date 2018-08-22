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

    def _dictdiff(self, d1, d2):
        output = {}
        all_keys = set(d1.keys() + d2.keys())

        for key in all_keys:
            if d1.get(key) != d2.get(key):
                output[key] = [d1.get(key), d2.get(key)]

        return output

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

    def get_categorydict(self, category):
        category_dict = {}
        category_found = False
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        url_method = "&method=pwg.categories.getAdminList"

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")

        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get group information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                for my_category in content['result']['categories']:
                    if my_category['name'] == category:
                        category_dict['category_id'] = int(my_category['id'])
                        category_dict['name'] = category
                        category_dict['comment'] = my_category['comment']
                        category_dict['status'] = my_category['status']
                        category_found = True
            # Failed otherwise
            else:
                self.module.fail_json(msg="An error occured while researching {0}".format(category))

        if not category_found:
            category_dict['category_id'] = -1

        return category_dict

    def get_groupid(self, groupname):
        group_id = 0
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
            if int(content['result']['paging']['count']) == 0:
                group_id = -1
            # Store the group_id if exactly one answer is found
            elif int(content['result']['paging']['count']) == 1:
                group_id = int(content['result']['groups'][0]['id'])
            # Failed otherwise
            else:
                self.module.fail_json(msg="An error occured while researching {0}".format(groupname))

        return group_id

    def get_userdict(self, username):
        user_dict = {}
        server_name = self.module.params["url"]
        my_url = server_name + self.api_endpoint
        url_method = "&method=pwg.users.getList&username=" + username + "&display=basics"

        rsp, info = fetch_url(self.module,
                              my_url + url_method,
                              headers=self.header,
                              method="GET")
        if info["status"] != 200:
            self.module.fail_json(msg="Failed to get user information from Piwigo", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            # If no user can be found set user_id to -1
            if int(content['result']['paging']['count']) == 0:
                user_dict['user_id'] = -1
            # Store the userid if exactly one answer is found
            elif int(content['result']['paging']['count']) == 1:
                user_dict['user_id'] = int (content['result']['users'][0]['id'])
                user_dict['username'] = content['result']['users'][0]['username']
                user_dict['email'] = content['result']['users'][0]['email']
                user_dict['status'] = content['result']['users'][0]['status']
                user_dict['level'] = content['result']['users'][0]['level']
                user_dict['groups'] = content['result']['users'][0]['groups']

            # Failed otherwise
            else:
                self.module.fail_json(msg="An error occured while researching {0}".format(username))

        return user_dict

    # Return a list to the piwigo format api
    def get_id_list(self, name_list, type):
        id_list = []
        type_id = ""
        assert (type in ["username", "group", "category"])

        if type == "username":
            for name in name_list:
                type_id = self.get_userdict(name)['user_id']
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
        else:
            for name in name_list:
                type_id = self.get_categorydict(name)['category_id']
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