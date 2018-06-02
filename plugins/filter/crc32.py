# plugins/filter/crc32.py
import binascii


def crc32(s):
    return binascii.crc32(s) & 0xffffffff


class FilterModule(object):
    ''' Ansible core jinja2 filters '''

    def filters(self):
        return {
            'crc32': crc32,
        }
