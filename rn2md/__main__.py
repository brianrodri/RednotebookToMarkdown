"""Entry point for rn2md tool."""
import sys

from . import config
from . import formatters
from . import storage
from . import util

ENTRY_SEP = '\n\n\n'


def main():
    """Prints RedNotebook entries in markdown syntax."""
    opt, remaining_argv = config.Options.from_argv(sys.argv)
    rednotebook = storage.load_rednotebook_entries(opt.data_path)
    def rednotebook_to_markdown(date):
        """Returns the given date's RedNotebook entry in Markdown format."""
        rn_lines = rednotebook[date].split('\n') if date in rednotebook else []
        formatter = formatters.format_rednotebook_as_markdown()
        md_lines = [formatter.send(line.rstrip()) for line in rn_lines]
        return '\n'.join(md_lines)
<<<<<<< HEAD
    print(ENTRY_SEP.join(rednotebook_to_markdown(d) for d in dates))
=======
    if remaining_argv:
        date_range = (
            util.parse_date_range(' '.join(remaining_argv), opt.workdays_only))
    else:
        date_range = opt.default_date_range
    print('\n\n\n'.join(rednotebook_to_markdown(d) for d in date_range))
>>>>>>> 164c4fbd55db7214ad8a0cf7585a6d4527b31d69


if __name__ == '__main__':
    main()
