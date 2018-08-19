#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.pywigo_management import *
import json
import urllib

DOCUMENTATION='''
module: piwigo_user
author: Cédric Bleschet
description: Module to grant access to category to user and group. The category must exist. It the category is found
the status will always be changed even the no change is really done (no information given by the API) 
options:
  username:
    cat_name: The category (photo album) name
    required: yes
  password:
    description:User Password
    required: false
'''

EXAMPLES = '''
- name: "Grant access "
  piwigo_permissions:
    cat_name:
      - "my album"
    user_name:
      - "user1"
      - "user2"
      - "user3"
      - "user4"
    group_name:
      - "testgroup"
      - "testgroup2"
    url_username: "piwigo_admin"
    url_password: "password"
    url: "http://piwigo.essai.fr:8080"
'''

RETURN = '''
results:
    description: user status
'''

class PiwigoPermissionsManagement(PiwigoManagement):
    def manage_permissions(self, cat_id, group_id, user_id):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.permissions.add',
                  'user_id[]': user_id,
                  'cat_id[]': cat_id,
                  'group_id[]': group_id ,
                  'recursive': self.module.params["recursive"],
                  'pwg_token': self.token
                  }

        my_data = urllib.urlencode(values, True)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo to set album permissions", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Access to {0} succesfully granted to user(s) {1} and group(s) {2}".format(
                            self.module.params["cat_name"],
                            self.module.params["user_name"],
                            self.module.params['group_name'])})
            else:
                self.module.fail_json(msg="Failed to set permissions", response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cat_name=dict(required=True, type='list'),
            group_name=dict(required=False, type='list', default=[]),
            user_name=dict(required=False, type='list', default=[]),
            recursive=dict(required=False, default=False, type='bool'),
            url=dict(required=True, type='str'),
            url_username=dict(required=True, type='str'),
            url_password=dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigopermission = PiwigoPermissionsManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of PiwigoPermissionsManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigopermission.request_piwigo_login()
    piwigopermission.header = my_header

    # Get token for admin user
    my_token = piwigopermission.get_admin_status()
    piwigopermission.token = my_token


    #Get cat id
    cat_id = piwigopermission.get_id_list(module.params['cat_name'], "category")

    #Get User id
    user_id = piwigopermission.get_id_list(module.params['user_name'], "username")

    #Get Group Id
    group_id = piwigopermission.get_id_list(module.params['group_name'], "group")


    piwigopermission.manage_permissions(cat_id, group_id, user_id)
    piwigopermission.finish_request()

if __name__ == '__main__':
    main()
