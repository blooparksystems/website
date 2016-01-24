odoo.define('website.contentUndo', function (require) {
"use strict";

    var ajax = require('web.ajax');
    var base = require('web_editor.base');
    var content_menu = require('website.contentMenu');

    content_menu.TopBar.include({
        undo_change: function() {
            var self = this;
            var context = base.get_context();
            self.mo_id = self.getMainObject().id;

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'ir.ui.view',
                method: 'reset_last_change',
                args: [self.mo_id],
                kwargs: {
                    context: context
                },
            }).then(function (res) {
                window.location.reload();
            });
        },
        reset_changes: function() {
            var self = this;
            var context = base.get_context();
            self.mo_id = self.getMainObject().id;

            ajax.jsonRpc('/web/dataset/call_kw', 'call', {
                model: 'ir.ui.view',
                method: 'reset_last_change',
                args: [self.mo_id],
                kwargs: {
                    context: context
                },
            }).then(function (res) {
                window.location.reload();
            });
        },
    });

});
