from zope.interface import implements

from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade

from .lib.ccClient import ccClient


_ZPROPS = ['zCChost', 'zCCPort', 'zCCUser', 'zCCPass']


class IAuditLogFacade(IFacade):
    def getLogs(self, deviceUid):
        """Pulls audit logs for device"""


class AuditLogFacade(ZuulFacade):
    implements(IAuditLogFacade)

    def getLogs(self, deviceUid):
        device = self.context.unrestrictedTraverse(deviceUid)
        if not device.zCCHost:
            msg = 'Must setup Audit zProperties (%s)' % ', '.join(_ZPROPS)
            return [msg]

        kibana = ccClient(
            device.zCCHost,
            int(device.zCCPort),
            device.zCCUser,
            device.zCCPass
        )

        login = kibana.login()
        if not login:
            return ['Login failed, check zProperties']

        logs = kibana.getKibanaLogs(device.id)
        return logs
