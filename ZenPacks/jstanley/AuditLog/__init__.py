import logging
import os
from ZenPacks.zenoss.ZenPackLib import zenpacklib

LOG = logging.getLogger('zen.AuditLogs')
CFG = zenpacklib.load_yaml([os.path.join(os.path.dirname(__file__), "zenpack.yaml")], verbose=False, level=30)
schema = CFG.zenpack_module.schema

_ZPROPS = ['zCCHost', 'zCCPort', 'zCCUser', 'zCCPass']

class ZenPack(schema.ZenPack):

    def install(self, app):
        super(ZenPack, self).install(app)
        LOG.info('Populate zProperties ({}) at /Devices'.format(', '.join(_ZPROPS)))
