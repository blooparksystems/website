# -*- coding: utf-8 -*-
from lxml import html
from datetime import datetime
from diff_match_patch import diff_match_patch
from openerp import api, fields
from openerp.models import Model


class IrUiView(Model):
    _inherit = "ir.ui.view"

    diffs = fields.One2many('ir.ui.view.diff', 'view', 'Diffs')

    @api.one
    def save(self, value, xpath=None):
        if self.env.context is None:
            self.env.context = {}

        if not xpath:
            return super(IrUiView, self).save(value, xpath=xpath)

        parser = html.HTMLParser(encoding='utf-8')
        arch_master = self.get_arch_master(self.arch, parser, xpath)
        arch_section = html.fromstring(value, parser=parser)

        if arch_master is not False and \
                self.section_changed(arch_master, arch_section):
            diff_model = self.env['ir.ui.view.diff']
            content_master = html.tostring(arch_master, encoding='utf-8')
            content_section = html.tostring(arch_section, encoding='utf-8')
            patch_content = self.get_patch(content_master, content_section)
            # TODO: do not save attributes from element tag that belongs to
            # website edition, maybe with a method clear_from_edition
            values = {
                'diff': patch_content,
                'datetime': datetime.now()
            }
            domain = [
                ('view', '=', self.id),
                ('name', '=', xpath),
                ('element', '=', arch_section.tag)
            ]
            diff = diff_model.search(domain)
            if diff:
                diff.write(values)
            else:
                values.update({x[0]: x[2] for x in domain})
                diff_model.create(values)

    @api.model
    def get_arch_master(self, value, parser, xpath):
        arch = html.fromstring(value, parser=parser)
        if arch:
            arch = arch.xpath('/%s' % xpath)
        if arch:
            return arch[0]
        return False

    @api.model
    def section_changed(self, arch_master, arch_section):
        if arch_section.get('data-note-id', ''):
            return True
        elif arch_master:
            master_len = len(arch_master.getchildren())
            section_len = len(arch_section.getchildren())
            if master_len != section_len:
                return True
        return False

    @api.model
    def get_patch(self, master_arch, section_arch):
        diff = diff_match_patch()
        patches = diff.patch_make(unicode(master_arch, 'utf-8'),
                                  unicode(section_arch, 'utf-8'))
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
