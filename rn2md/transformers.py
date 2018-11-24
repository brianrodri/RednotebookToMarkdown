"""Helpers to tranform data in RedNotebook syntax to Markdown syntax.

Here is a summary of the currently implemented transformers:

    RedNotebook                       Markdown
    ===========                       ========
    [name ""url""]                    [name](url)
    //text//                          _text_
    --text--                          ~text~
    =Text=                            # Text
    [""url""]                         ![...](url)
    + Ordered item                    1. Ordered item
    - Unordered item                  - Unordered item
    ``asdf``                          `asdf`
"""
import re

import defaultlist


BACKTICKED_DATA_PATTERN = re.compile(r'`.*?`')
INNER_UNDERSCORE_PATTERN = re.compile(r'(?<=\w)_(?=\w)')
LINK_PATTERN = re.compile(r'\[([^\]]*?) ""(.*?)""\]')
LIST_ITEM_PATTERN = re.compile(r'^\s*([-|\+])\s')

CODE_BLOCK_DELIM_PATTERN = re.compile(r'``')
HEADER_DELIM_PATTERN = re.compile(r'=+')
ITALIC_DELIM_PATTERN = re.compile(r'//')
STRIKETHROUGH_DELIM_PATTERN = re.compile(r'--')


def _sub_balanced_delims(delim_pattern, sub, string, data_fun=str, **kwargs):
    """We don't use a bigger regex because avoiding link urls is messy."""
    try:
        sub_start, sub_end = sub
    except ValueError:
        sub_start = sub_end = sub
    delims = _filtered_matches(delim_pattern, string, **kwargs)
    balanced_delims = list(zip(delims, delims))
    # NOTE: Always do delim substitutions in reverse so the indices found remain
    # valid.
    for start_delim, end_delim in reversed(balanced_delims):
        start = string[:start_delim.start()]
        inner = string[start_delim.end():end_delim.start()]
        end = string[end_delim.end():]
        string = ''.join([start, sub_start, data_fun(inner), sub_end, end])
    return string


def _filtered_matches(patt, string, neg_preds=None):
    if neg_preds is None:
        neg_preds = (_occurs_in_link, _occurs_in_backtick)
    for match in patt.finditer(string):
        if any(p(match) for p in neg_preds):
            continue
        yield match


def _occurs_in_link(match):
    occurrences = LINK_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span(2)) for m in occurrences)


def _occurs_in_backtick(match):
    occurrences = BACKTICKED_DATA_PATTERN.finditer(match.string)
    return any(_spans_intersect(match.span(), m.span()) for m in occurrences)


def _spans_intersect(span1, span2):
    (lo1, hi1), (lo2, hi2) = span1, span2
    return hi1 >= lo2 and hi2 >= lo1


def LinkTransformer():  # pylint: disable=invalid-name
    """Transforms '[[text ""url""]]' to '[text](url)'."""
    line = ''
    while True:
        line = yield LINK_PATTERN.sub(r'[\1](\2)', line)


def ItalicTransformer():  # pylint: disable=invalid-name
    """Transforms '//text//' to '_text_'."""
    line = ''
    while True:
        line = yield _sub_balanced_delims(ITALIC_DELIM_PATTERN, '_', line)


def StrikethroughTransformer():  # pylint: disable=invalid-name
    """Transforms '--text--' to '**OBSOLETE**(text)'."""
    line = ''
    while True:
        if set(line) == {'-'}:
            line = yield line
        else:
            line = yield _sub_balanced_delims(
                STRIKETHROUGH_DELIM_PATTERN, ('**OBSOLETE**(', ')'), line,
                data_fun=lambda d: d.rstrip('.?!'))


def HeaderTransformer(base_level=0):  # pylint: disable=invalid-name
    """Transforms '=TEXT=' into '# TEXT'."""
    line = ''
    while True:
        line = yield line
        header_delim = HEADER_DELIM_PATTERN.search(line)
        if not header_delim or header_delim.group() == line:
            continue
        if header_delim.end() != HEADER_DELIM_PATTERN.search(line[::-1]).end():
            continue
        line = ' '.join([
            '#' * (base_level + header_delim.end()),
            line[header_delim.end():-header_delim.end()].lstrip(),
        ])


def ListTransformer():  # pylint: disable=invalid-name
    """Transforms unordered and ordered lists into markdown syntax."""
    line = ''
    ordered_list_history = defaultlist.defaultlist(lambda: 1)
    sequential_empty_lines = 0
    while True:
        line = yield line
        list_item_match = LIST_ITEM_PATTERN.match(line)
        if list_item_match:
            list_item_depth = list_item_match.start(1)
            list_item_type = list_item_match.group(1)
            # Future sub-items will restart their numbering from 1.
            del ordered_list_history[list_item_depth + 1:]
            if list_item_type == '+':
                line = ''.join([
                    line[:list_item_match.start(1)],
                    str(ordered_list_history[list_item_depth]) + '.',
                    line[list_item_match.end(1):],
                ])
                ordered_list_history[list_item_depth] += 1
        elif line.strip():
            sequential_empty_lines = 0
            ordered_list_history.clear()
        else:
            sequential_empty_lines += 1
            if sequential_empty_lines >= 2:
                ordered_list_history.clear()


def InnerUnderscoreEscaper():  # pylint: disable=invalid-name
    """Transforms underscores which need to be escaped."""
    line = ''
    while True:
        line = yield line
        matches = _filtered_matches(INNER_UNDERSCORE_PATTERN, line)
        for match in reversed(list(matches)):
            line = ''.join([line[:match.start()], r'\_', line[match.end():]])


def CodeBlockTransformer():  # pylint: disable=invalid-name
    """Transforms codeblocks into markdown syntax."""
    line = ''
    while True:
        line = yield _sub_balanced_delims(
            CODE_BLOCK_DELIM_PATTERN, '`', line, neg_preds=[_occurs_in_link])
