(function() {
    function auditLog() {
        UID = Zenoss.env.device_uid
        var win = new Zenoss.CommandWindow({
            uids: [UID],
            target: 'run_auditLogs',
            title: _t('Audit Log')
        });
        win.show();
    }

    Ext.ComponentMgr.onAvailable('footer_bar', function(config) {
        var footer_bar = Ext.getCmp('footer_bar');
        footer_bar.on('render', function() {
            footer_bar.add({
                xtype: 'button',
                id: 'auditlog_button',
                text: _t('Audit Log'),
                hidden: Zenoss.Security.doesNotHavePermission('Change Device'),
                handler: auditLog
            })
        });
    });
}());
