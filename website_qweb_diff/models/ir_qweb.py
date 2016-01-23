# -*- coding: utf-8 -*-
from lxml import html
from diff_match_patch import diff_match_patch
from openerp import models, api


class QWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    @api.model
    def render(self, id_or_xml_id, qwebcontext=None, loader=None):
        res = super(QWeb, self).render(id_or_xml_id,
                                       qwebcontext=qwebcontext,
                                       loader=loader)
        parser = html.HTMLParser(encoding='utf-8')
        try:
            arch = html.fromstring(res, parser=parser)
        except Exception:
            return res

        update = False
        diff = diff_match_patch()
        view = self.get_page_view_id(id_or_xml_id)
        domain = [('view', '=', view.id)]
        for section in self.env['ir.ui.view.diff'].search(domain):
            xpath = '//%s' % '/'.join([x for x in section.name.split('/')
                                       if not x.startswith('t')])
            arch_section = arch.xpath(xpath)
            if not arch_section:
                continue
            element = arch_section[0]
            update = True

            patches = diff.patch_fromText(section.diff)
            element_content = html.tostring(element, encoding='utf-8')
            section_content = diff.patch_apply(patches,
                                               unicode(element_content,
                                                       'utf-8'))[0]
            section_element = html.fromstring(section_content, parser=parser)
            element.getparent().replace(element, section_element)

        if update:
            res = html.tostring(arch, method='html', encoding='utf8',
                                doctype='<!DOCTYPE html>')
        return res

    @api.model
    def get_page_view_id(self, id_or_xml_id):
        view = False
        model = self.env['ir.ui.view']

        if isinstance(id_or_xml_id, (int, long)):
            view = model.browse(id_or_xml_id)
        else:
            try:
                view = model.browse(int(id_or_xml_id))
            except ValueError:
                view = self.env.ref(id_or_xml_id)

        # Look for an inherited view
        views = model.search([('key', '=', view.key)])
        website = self.env['website'].get_current_website()
        for v in views:
            if v.website_id.id == website.id:
                view = v
                break

        return view
