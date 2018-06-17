from zope.interface import implements

from Products.Zuul.facades import ZuulFacade
from Products.Zuul.interfaces import IFacade

from .lib.ccClient import ccClient


class IAuditLogFacade(IFacade):
    def getLogs(self, deviceUid):
        """Pulls audit logs for device"""


class AuditLogFacade(ZuulFacade):
    implements(IAuditLogFacade)

    def getLogs(self, deviceUid):
        device = self.context.unrestrictedTraverse(deviceUid)
        if not device.zCCHost:
            return ['Must setup Audit zProperties (zCChost, zCCPort, zCCUser, zCCPass)']

        kibana = ccClient(
            device.zCCHost,
            int(device.zCCPort),
            device.zCCUser,
            device.zCCPass
        )
        kibana.login()
        logs = kibana.getKibanaLogs(deviceUid)
        return logs

