# -*- coding: utf-8 -*-
from lxml import html
from diff_match_patch import diff_match_patch
from openerp import models, api


class QWeb(models.AbstractModel):
    _inherit = 'ir.qweb'

    @api.model
    def render(self, id_or_xml_id, qwebcontext=None, loader=None):
        res = super(QWeb, self).render(id_or_xml_id, qwebcontext=qwebcontext, loader=loader)

        parser = html.HTMLParser(encoding='utf-8')

        # TODO: look for in more inherited views
        if isinstance(id_or_xml_id, (int, long)):
            view = self.env['ir.ui.view'].browse(id_or_xml_id)
        else:
            view = self.env.ref(id_or_xml_id)

        domain = [('view', '=', view.id)]
        update = False
        sections = {x.name: x.diff for x in self.env['ir.ui.view.diff'].search(domain)}
        arch = html.fromstring(res, parser=parser)

        diff = diff_match_patch()
        # TODO: cover the view for public user
        for element in arch.xpath('//*[@data-oe-xpath]'):
            key = element.get('data-oe-xpath')
            if key in sections:
                text, elements = sections[key].split('|T|')
                if text:
                    patches = diff.patch_fromText(text)
                    version_text = diff.patch_apply(patches, unicode(element.text, 'utf-8'))
                    element.text = version_text[0]
                children = zip(element.getchildren(), elements.split('|E|'))
                for child, child_version in children:
                    child_master = html.tostring(child, encoding='utf-8')
                    patches = diff.patch_fromText(child_version)
                    version = diff.patch_apply(patches, unicode(child_master, 'utf-8'))[0]
                    version_element = html.fromstring(version, parser=parser)
                    element.replace(child, version_element)
                update = True

        if update:
            res = html.tostring(arch, encoding='utf8')

        return res
