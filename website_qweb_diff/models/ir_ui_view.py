# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from lxml import html
from diff_match_patch import diff_match_patch
from openerp import api, fields, SUPERUSER_ID
from openerp.models import Model


class IrUiView(Model):
    _inherit = "ir.ui.view"

    diffs = fields.One2many('ir.ui.view.diff', 'view', 'Diffs')

    @api.one
    def save(self, value, xpath=None):
        if self.env.context is None:
            self.env.context = {}

        parser = html.HTMLParser(encoding='utf-8')

        arch_section = html.fromstring(value, parser=parser)
        # TODO: the 9.0 version doesn't use id, I think it use an attribute data-note-id
        section_id = arch_section.get('id', '')
        if section_id.startswith('note-editor'):
            diff_model = self.env['ir.ui.view.diff']
            arch_master = self.get_master_view_part(xpath)[0]

            arch_list = []
            # TODO: cover case when adding a new section from blocks
            children = zip(arch_master.getchildren(), arch_section.getchildren())
            for child_master, child_version in children:
                child_master = html.tostring(child_master, encoding='utf-8')
                child_version = html.tostring(child_version, encoding='utf-8')
                if child_master and child_version:
                    arch_list.append(self.get_patch(child_master, child_version))
                else:
                    arch_list.append(child_version)
            patch_text = self.get_patch(arch_master.text, arch_section.text)
            diff = '%s|T|%s' % (patch_text, '|E|'.join(arch_list))
            vals = {'diff': diff}
            part_view = diff_model.search(('view', '=', self.id),
                                          ('name', '=', xpath))
            if part_view:
                part_view.write(vals)
            else:
                vals.update({
                    'name': xpath,
                    'element': arch_section.tag,
                    'view': self.id,
                })
                diff_model.create(vals)

    @api.one
    def get_master_view_part(self, xpath):
        arch = html.fromstring(self.arch, parser=html.HTMLParser(encoding='utf-8'))
        arch_section = arch.xpath('/' + xpath)
        return arch_section and arch_section[0] or False

    @api.model
    def get_patch(self, master_arch, version_arch):
        diff = diff_match_patch()
        patches = diff.patch_make(unicode(master_arch, 'utf-8'),
                                  unicode(version_arch, 'utf-8'))
        return diff.patch_toText(patches)

    @api.one
    def reset_all_changes(self, hard=False):
        for diff in self.diffs:
            if hard:
                diff.unlink()
            else:
                diff.write({'active': False})

    @api.one
    def reset_last_change(self, hard=False):
        if self.diffs:
            if hard:
                self.diffs[0].unlink()
            else:
                self.diffs[0].write({'active': False})


class IrUiViewDiff(Model):
    _name = 'ir.ui.view.diff'
    _order = 'datetime desc'

    name = fields.Char('Name')
    element = fields.Char('Element')
    diff = fields.Text('Diff')
    view = fields.Many2one('ir.ui.view', 'View', ondelete="cascade")
    datetime = fields.Datetime('Datetime')
