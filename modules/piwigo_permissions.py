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
'''

RETURN = '''
results:
    description: user status
'''

class PiwigoPermissionsManagement(PiwigoManagement):
    def manage_permissions(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.permissions.add',
                  'cat_id': self._get_piwigo_list(self.module.params["cat_id"]),
                  'group_id': self._get_piwigo_list(self.module.params["group_id"]),
                  'user_id': self._get_piwigo_list(self.module.params["user_id"]),
                  'recursive': self.module.params["recursive"],
                  'pwg_token': self.token
                  }
        
        my_data = urllib.urlencode(values)

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
                self.module.exit_json(changed=True, msg=content)
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Access to {0} succesfully granted to user {1} and group {2}".format(self.module.params["cat_id"],
                                                                                             self.module.params["user_id"],
                                                                                             self.module.params['group_id'])})
            else:
                self.module.fail_json(msg="Failed to set permissions", response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            cat_id=dict(required=True, type='list'),
            group_id=dict(required=False, type='list', default=[]),
            user_id=dict(required=False, type='list', default=[]),
            cat_name=dict(required=False, type='str'),
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

    #Get User id
    piwigopermission.get_userid_dict(module.params['user_name'])

    #Get Group Id
    piwigopermission.get_group_id(module.params['group_name'][0])


    piwigopermission.manage_permissions()
    piwigopermission.finish_request()

if __name__ == '__main__':
    main()
