from Products.ZenUI3.browser.streaming import StreamingView
from Products.ZenUtils.jsonutils import unjson
from Products.Zuul import getFacade


class AuditLogView(StreamingView):
    """
    Accepts a list of uids to get audit logs for.
    """
    def stream(self):
        self.write('Starting to retrieve logs...')
        facade = getFacade('auditlogs', self.context)
        data = unjson(self.request.get('data'))
        deviceUids = data['uids']
        for deviceUid in deviceUids:
            output = facade.getLogs(deviceUid)
            for line in output:
                self.write(line)
        self.write('Finished.')
