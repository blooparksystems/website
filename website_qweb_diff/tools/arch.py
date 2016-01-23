# -*- coding: utf-8 -*-
from lxml import html
from diff_match_patch import diff_match_patch


def get_html_parts(arch):
    content = html.tostring(arch, encoding='utf-8')
    start = 0
    char = content[0]
    while char != '>':
        start += 1
        char = content[start]
    end = len(content) - len(arch.tag) + 3
    return {
        'start': content[:start],
        'content': content[start:end],
        'end': content[end:]
    }


def get_html_arch(value, parser, xpath):
    arch = html.fromstring(value, parser=parser)
    if arch:
        arch = arch.xpath('/%s' % xpath)
    if arch:
        return arch[0]
    return False


def get_html_patch(master_arch, section_arch):
    diff = diff_match_patch()
    patches = diff.patch_make(unicode(master_arch, 'utf-8'),
                              unicode(section_arch, 'utf-8'))
    return diff.patch_toText(patches)


def get_patch_from_text(value):
    diff = diff_match_patch()
    return diff.patch_fromText(value)


def set_patch(patches, value):
    diff = diff_match_patch()
    return diff.patch_apply(patches, value)[0]
