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

class PiwigoCategoryManagement(PiwigoManagement):
    def create_category(self):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.categories.add',
                  'name': self.module.params["name"],
                  'parent': self.module.params["parent"],
                  'comment': self.module.params["comment"],
                  'visible': self.module.params["visible"],
                  'status':  self.module.params["status"],
                  'commentable': self.module.params["commentable"],
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to create a category",
                                   response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Category {0} succesfully added".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="Failed to create Category", response=rsp, info=info)

    def delete_category(self, category_id):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.categories.delete',
                  'category_id': category_id,
                  'pwg_token': self.token
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to create a category",
                                   response=rsp, info=info)
        else:
            content = json.loads(rsp.read())
            if content['stat'] == "ok":
                setattr(self, 'ansible_status', {'result': 'Changed', 'message':
                        "Category {0} succesfully deleted".format(self.module.params["name"])})
            else:
                self.module.fail_json(msg="An error occured while deleting category {0}"
                                      .format(self.module.params["name"]))


    def set_category_info(self, category_id):
        my_url = self.module.params["url"] + self.api_endpoint
        values = {'method': 'pwg.categories.setInfo',
                  'category_id': category_id,
                  'name': self.module.params["name"],
                  'comment': self.module.params["comment"],
                  'status':  self.module.params["status"],
                  }
        my_data = urllib.urlencode(values)

        rsp, info = fetch_url(self.module,
                              my_url,
                              data=my_data,
                              headers=self.header,
                              method="POST")

        if info["status"] != 200:
             self.module.fail_json(msg="Failed to connect to piwigo in order to create a category",
                                   response=rsp, info=info)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            name=dict(required=True, type='str'),
            parent=dict(required=False, type='int', default=0),
            comment=dict(required=False, default='', type='str'),
            visible=dict(required=False, default=True, type='bool'),
            status=dict(type='str', choices=['public', 'private'], default='private'),
            commentable=dict(required=False, default=True, type='bool'),
            url = dict(required=True, type='str'),
            url_username = dict(required=True, type='str'),
            url_password = dict(required=True, type='str', no_log=True),
        ),
        supports_check_mode=True,
        required_together=[
            ["url_username", "url_password"],
        ]
    )

    piwigocategory = PiwigoCategoryManagement(module,
                                      token="",
                                      header={'Content-Type': 'application/x-www-form-urlencoded'},
                                      ansible_status={'result': 'Fail',
                                                      'message': 'Could not get status of '
                                                                 'PiwigoCategoryManagement module'},
                                      api_endpoint="/ws.php?format=json"
                                      )

    # Get cookie
    my_header = piwigocategory.request_piwigo_login()
    setattr(piwigocategory, 'header', my_header)

    # Get token for admin user
    my_token = piwigocategory.get_admin_status()
    setattr(piwigocategory, 'token', my_token)

    my_previous_category = piwigocategory.get_categorydict(piwigocategory.module.params["name"])
    my_new_category = {}
    my_diff_category = {}

    if module.params['state'] == 'present':
        if my_previous_category['category_id'] < 0:
            piwigocategory.create_category()
        else:
            piwigocategory.set_category_info(my_previous_category['category_id'])
            my_new_category = piwigocategory.get_categorydict(piwigocategory.module.params["name"])
            my_diff_category = piwigocategory._dictdiff(my_previous_category, my_new_category)
            if len(my_diff_category.keys()) == 0:
                setattr(piwigocategory, 'ansible_status',
                        {'result': 'Unchanged',
                         'message': 'No change in category {0} detected'.format(piwigocategory.module.params["name"])})
            else:
                setattr(piwigocategory, 'ansible_status',
                        {'result': 'Changed',
                         'message': 'Change in category {0} detected : {1}'.format(piwigocategory.module.params["name"],
                                                                                   my_diff_category)})

    else:
        if my_previous_category['category_id'] > 0:
            piwigocategory.delete_category(my_previous_category['category_id'])
        else:
            setattr(piwigocategory, 'ansible_status',
                    {'result': 'Unchanged',
                     'message': 'No Category {0} found'.format(module.params['name'])})

    piwigocategory.finish_request()


if __name__ == '__main__':
    main()
