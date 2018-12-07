"""Entry point for rn2md tool."""
import collections
import sys

from . import config
from . import formatters
from . import storage
from . import util


def main():
    """Prints RedNotebook entries in markdown syntax."""
    options, remaining_argv = config.build_config_options(sys.argv)
    date_arg = ' '.join(remaining_argv) or 'today'
    dates = util.parse_dates(date_arg, options.workdays_only)
    rednotebook = storage.load_rednotebook_entries(options.data_path)
    def rednotebook_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        # Entries begin with a date header to help distinguish them from each
        # other. Subsequent headers are padded by 1 to render them as children.
        md_lines = [date.strftime('# %a %b %d, %Y')]
        formatter = formatters.RednotebookToMarkdownFormatter(header_padding=1)
        md_lines.extend(formatter.fmt(rn_line.rstrip()) for rn_line in rn_lines)
        return '\n'.join(md_lines)
    print('\n\n\n'.join(rednotebook_to_markdown(d) for d in dates))


if __name__ == '__main__':
    main()
