# -*- coding: utf-8 -*-
from lxml import html
from openerp import models, api
from openerp.addons.website_qweb_diff.tools import arch


class QWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    @api.model
    def render(self, id_or_xml_id, qwebcontext=None, loader=None):
        res = super(QWeb, self).render(id_or_xml_id,
                                       qwebcontext=qwebcontext,
                                       loader=loader)
        parser = html.HTMLParser(encoding='utf-8')
        try:
            arch_master = html.fromstring(res, parser=parser)
        except Exception:
            return res

        update = False
        view = self.get_page_view_id(id_or_xml_id)
        domain = [('view', '=', view.id)]
        for section in self.env['ir.ui.view.diff'].search(domain):
            xpath = '//%s' % '/'.join([x for x in section.name.split('/')
                                       if not x.startswith('t')])
            arch_section = arch_master.xpath(xpath)
            if not arch_section:
                continue
            element = arch_section[0]
            update = True

            patches = arch.get_patch_from_text(section.diff)
            dict_content = arch.get_html_parts(element)
            element_content = unicode(dict_content['content'], 'utf-8')
            section_content = arch.set_patch(patches, element_content)
            section_full = dict_content['start'] + section_content + dict_content['end']
            section_element = html.fromstring(section_full, parser=parser)
            element.getparent().replace(element, section_element)

        if update:
            res = html.tostring(arch_master, method='html', encoding='utf8',
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
