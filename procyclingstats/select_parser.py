from typing import List, Tuple

from selectolax.parser import Node


class SelectParser:
    """
    Parser for select menu, parsed data are stored in `self.table`, which
    is represented as list of dicts

    :param html_select_menu: HTML select menu to be parsed from
    """

    def __init__(self, html_select_menu: Node) -> None:
        self.html_select_menu = html_select_menu
        self.table = []

    def parse(self, fields: Tuple[str]) -> None:
        """
        Parses HTML table to `self.table` (list of dicts) by calling given
        `TableRowParses` methods. Every parsed table row is dictionary with
        `fields` keys

        :param fields: fields that parsed table should have, current options:
            - text
            - value
        """
        for option in self.html_select_menu.css("option"):
            row = {}
            if "text" in fields:
                row['text'] = option.text()
            if "value" in fields:
                row['value'] = option.attributes['value']
            self.table.append(row)
