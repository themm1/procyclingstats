import glob
import json
from typing import Any, Dict, List, Optional, Type

from procyclingstats import Scraper
from procyclingstats.errors import ExpectedParsingError


class FixturesUtils:
    """
    Class for working with fixtures.

    Every fixture has to have filename as valid PCS relative URL where
    slashes are replaced with underscores. Fixture's URL means filename of
    a fixture where are underscores replaced with slashes.

    Currently there are two types of fixtures:
    - data fixture: Stores parsed data in .json file. While
    testing parsed data are tested against corresponding data fixture.
    - HTML fixture: Stores HTML in .txt file. While testing scraper object is
    created from this fixture's URL and HTML, so making request to PCS isn't
    needed.

    :param fixtures_path: Path to fixtures directory, defaults to
    "tests/fixtures/".
    """

    def __init__(self, fixtures_path: str = "tests/fixtures/") -> None:
        self.fixtures_path = fixtures_path

    def make_data_fixture(self, scraper_obj: Scraper) -> None:
        """
        Makes data fixture from dict returned by scraper object's `parse`
        method

        :param scraper_obj: Scraper object ready for HTML parsing.
        :raises ExpectedParsingError: When object's HTML is None.
        """
        filename = self._get_filename_for_parsing(scraper_obj)
        data = scraper_obj.parse()
        json_obj = json.dumps(data, indent=2)
        with open(f"{self.fixtures_path}{filename}.json", "w") as fixture:
            fixture.write(json_obj)

    def make_html_fixture(self, scraper_obj: Scraper) -> None:
        """
        Makes HTML fixture from scraper object's `url` and `html`.

        :param scraper_obj: Scraper object ready for HTML parsing.
        :raises ExpectedParsingError: When object's HTML is None.
        """
        filename = self._get_filename_for_parsing(scraper_obj)
        with open(f"{self.fixtures_path}{filename}.txt", "w") as fixture:
            fixture.write(scraper_obj.html.html) # type: ignore

    def get_data_fixture(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Gets data fixture with wanted URL.

        :param url: URL of wanted fixture.
        :return: Fixture file content as dict. If file wasn't found None is
        returned.
        """
        filename = self.url_to_filename(url)
        try:
            with open(f"{self.fixtures_path}{filename}.json", "r") as fixture:
                return json.load(fixture)
        except FileNotFoundError:
            return None

    def get_html_fixture(self, url: str) -> Optional[str]:
        """
        Gets HTML fixture with wanted URL.

        :param url: URL of wanted fixture.
        :return: Fixture file content as a string. If file wasn't found None is
        returned.
        """
        filename = self.url_to_filename(url)
        try:
            with open(f"{self.fixtures_path}{filename}.txt", "r") as fixture:
                return fixture.read()
        except FileNotFoundError:
            return None

    def get_scraper_objects_from_fixtures(
            self, scraper_class: Type[Scraper]) -> List[Scraper]:
        """
        Creates scraper object of ScraperClass from every HTML fixture which
        URL is valid for given ScraperClass.

        :param ScraperClass: Class to create objects from.
        :return: List with scraper objects ready for HTML parsing.
        """
        html_files_urls = self.get_urls_from_fixtures_dir("txt")
        json_files_urls = self.get_urls_from_fixtures_dir("json")
        # get URLs of all scraper objects that have both HTML and JSON file
        urls = [url for url in html_files_urls if url in json_files_urls]
        objects_to_test = []
        for url in urls:
            # add scraper object that passes URL validity check of given
            # scraper class
            try:
                # get HTML of scraper object from fixtures
                html = self.get_html_fixture(url)
                # add new scraper object that is ready for parsing to the list
                objects_to_test.append(scraper_class(url, html, False))
            except ValueError:
                pass
        return objects_to_test

    def get_urls_from_fixtures_dir(self, file_type: str) -> List[str]:
        """
        Converts filesnames with wanted type to relative URLs.

        :param file_type: File type (`txt`/`json` for now).
        :return: List of relative URLs.
        """
        html_file_paths = glob.glob(f"{self.fixtures_path}*.{file_type}")
        html_files = [f.split("/")[-1] for f in html_file_paths]
        # replace underscores by slashes and cut file type
        urls = [".".join(f.split(".")[:-1]).replace("_", "/")
                for f in html_files]
        return urls

    @staticmethod
    def url_to_filename(url: str) -> str:
        """
        Converts URL to filename (replaces slashes with underscores).

        :param url: Relative URL to convert filename from.
        :return: Filename without file type.
        """
        return url.replace("/", "_")

    @staticmethod
    def filename_to_url(filename: str) -> str:
        """
        Converts filename to relative URL (replaces underscores with slashes).

        :param filename: Filename to convert URL from (can be with file type)
        :return: relative URL.
        """
        if "." in filename:
            filename = ".".join(filename.split(".")[:-1])
        return filename.replace("_", "/")

    @staticmethod
    def _get_filename_for_parsing(scraper_obj: Scraper) -> str:
        """
        Gets filename for given scraper object from it's URL.

        :param scraper_obj: Scraper object with URL ready for HTML parsing.
        :raises ExpectedParsingError: When given scraper object isn't ready
        for HTML parsing.
        :return: Filename for given scraper object.
        """
        if scraper_obj.html is None:
            raise ExpectedParsingError("Object is not ready for HTML parsing")
        filename = FixturesUtils.url_to_filename(
            scraper_obj.normalized_relative_url())
        return filename
