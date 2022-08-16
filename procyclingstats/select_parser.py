from typing import List, Tuple

from requests_html import HTML


class SelectParser:
    """
    Parser for select menu, parsed data are stored in `self.table`, which
    is represented as list of dicts

    :param html_select_menu: HTML select menu to be parsed from
    """

    def __init__(self, html_select_menu: HTML) -> None:
        self.html_select_menu: HTML = html_select_menu
        self.table: List[dict] = []

    def parse(self, fields: Tuple[str]) -> None:
        """
        Parses HTML table to `self.table` (list of dicts) by calling given
        `TableRowParses` methods. Every parsed table row is dictionary with
        `fields` keys

        :param fields: fields that parsed table should have, current options:
            - text
            - value
        """
        for option in self.html_select_menu.find("option"):
            row = {}
            if "text" in fields:
                row['text'] = option.text
            if "value" in fields:
                row['value'] = option.attrs['value']
            self.table.append(row)
