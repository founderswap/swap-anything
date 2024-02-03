from importlib.metadata import version

import click
import pandas as pd

from swapanything.prep import get_all_matches
from swapanything.select import select_matches


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    click.echo(version("swap-anything"))
    ctx.exit()


@click.command(name='swapanything',
               help=('This the CLI of the swapanything package. The FILENAME argument '
                     'is the path to the file containing the information about the subjects '
                     'and their available time slots.'))
@click.argument('filename',
                type=click.Path(),
                )
@click.option('--filetype', '-ft',
              type=click.Choice(['Excel', 'E', 'csv', 'C']),
              default='csv',
              show_default=True,
              help='Type of the file to be parsed, choose between excel or csv.',
              )
@click.option('--separator', '-sep',
              type=click.STRING,
              default=',',
              show_default=True,
              help='Separator used in the input csv file. Defaults to comma.',
              )
@click.option('--headers', '-H',
              type=click.BOOL,
              is_flag=True,
              default=False,
              help='Specify whether the csv file has headers.',
              )
@click.option('--index-col', '-idx',
              type=click.BOOL,
              is_flag=True,
              default=False,
              show_default=True,
              help='Specify if the firts column contains the row indexes.',
              )
@click.option('--subject-col', '-subs',
              type=click.STRING,
              default='subject',
              show_default=True,
              help='Name of the column that stores the subjects.',
              )
@click.option('--slot-col', '-slots',
              type=click.STRING,
              default='slot',
              show_default=True,
              help='Name of the column with the slot for the subject.',
              )
@click.option('--version',
              is_flag=True,
              callback=print_version,
              expose_value=False,
              is_eager=True,
              help='Print the version of the package.',
              )
def main(filename: str,
         filetype: str,
         separator: str,
         index_col: bool,
         subject_col: str,
         slot_col: str,
         headers: bool,
         ):
    _header = 'infer' if headers else None
    _index_col = 0 if index_col else False

    if filetype.lower() == 'csv' or filetype.lower() == 'c':
        availabilities_df = pd.read_csv(
            filepath_or_buffer=filename,
            header=_header,
            sep=separator,
            index_col=_index_col,
            )
    else:
        availabilities_df = pd.read_excel(
            filepath_or_buffer=filename,
            header=_header,
            sep=separator,
            index_col=_index_col,
            )

    all_possible_matches = get_all_matches(
        availabilities=availabilities_df,
        subject_col=subject_col,
        slot_col=slot_col,
    )

    selected = select_matches(
        matches=all_possible_matches,
        subjects_col=subject_col,
        slots_col=slot_col,
    )

    print(selected)
