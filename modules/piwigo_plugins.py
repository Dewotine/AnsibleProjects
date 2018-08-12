#!/usr/bin/python
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from ansible.module_utils.pywigo_management import *
import json
import urllib

DOCUMENTATION='''
module: piwigo_plugins (API is not working)
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

class PiwigoPuginsManagement(PiwigoManagement):
    def manage_plugin(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.plugins.performAction',
                  'action': self.module.params["action"],
                  'plugin': self.module.params["plugin"],
                  'pwg_token': self.token
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to manage plugins", response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Category {0} succesfully added".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="Fail to {0} plugin {1}".format(self.module.params["action"],
                                                                          self.module.params["plugin"]),
                                      response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            action=dict(required=True, type='str', choices=['install', 'activate', 'deactivate', 'uninstall', 'delete'],
                        default='install'),
            plugin=dict(required=True, type='str'),         
            url = dict(required=True, type='str'),
            url_username = dict(required=True, type='str'),
            url_password = dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigoplugin = piwigopluginManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of piwigopluginManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigoplugin.request_piwigo_login()
    piwigoplugin.header = my_header

    # Get token for admin user
    my_token = piwigoplugin.get_admin_status()
    piwigoplugin.token = my_token

    piwigoplugin.manage_plugin()


    piwigoplugin.finish_request()

if __name__ == '__main__':
    main()
