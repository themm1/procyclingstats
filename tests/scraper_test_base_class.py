from procyclingstats import Scraper

from .fixtures_utils import FixturesUtils


class ScraperTestBaseClass:
    """
    Base class for scraper classes testing. Scraper testing class that extends
    this base class should override `ScraperClass` attribute to the class that
    it's testing e.g. `TestRider` should override to `Rider`.
    """
    ScraperClass = Scraper

    def test_parser(self, subtests) -> None:
        """
        Tests parser method of current `ScraperClass` against all data fixtures
        that are created by instances of current `ScraperClass`. HTML is always
        loaded from corresponding HTML fixture.

        :param subtests: subtests module, passed by pytest
        """
        f = FixturesUtils(fixtures_path="tests/fixtures/")
        objects_to_test = f.get_scraper_objects_from_fixtures(self.ScraperClass)
        parsed_data = []
        correct_data = []
        for obj in objects_to_test:
            # if "race/tour-de-france/2018/stage-3" in obj.url or\
            #     "ttt" in obj.url:
            #     continue
            parsed = obj.parse()
            correct = f.get_data_fixture(obj.relative_url())
            # dicts with parsed data has same keys
            assert parsed.keys() == correct.keys() # type: ignore
            parsed_data.append(parsed)
            correct_data.append(correct)

        for method in correct_data[0].keys():
            # method subtest
            with subtests.test(msg=method):
                for parsed, correct in zip(parsed_data, correct_data):
                    print(parsed['normalized_relative_url'])
                    if isinstance(correct[method], list):
                        for parsed_row, correct_row in zip(
                                parsed[method], correct[method]):
                            assert parsed_row == correct_row
                    else:
                        assert parsed[method] == correct[method]

    def url_valid(self, url: str) -> None:
        """
        Checks whether instance of current scraper class can be created when
        given URL is passed.

        :param url: URL that should be valid for current scraper class
        constructor.
        """
        passed = True
        try:
            self.ScraperClass(url, None, False)
        except ValueError:
            passed = False
        if not passed:
            assert False, f"'{url}' didn't pass when should"

    def url_invalid(self, url: str) -> None:
        """
        Checks whether current scraper class constructor raises an
        ValueError when given URL is passed.

        :param url: URL that should be invalid for current scraper class
        constructor.
        """
        passed = True
        try:
            self.ScraperClass(url, None, False)
        except ValueError:
            passed = False
        if passed:
            assert False, f"'{url}' passed when shouldn't"

    def equal(self, url1: str, url2: str) -> None:
        """
        Checks equality of two scraper objects created from given URLs.

        :param url1: URL of first object
        :param url2: URL of second object
        """
        assert self.ScraperClass(url1, None, False) == self.ScraperClass(url2,
            None, False)

    def unequal(self, url1: str, url2: str) -> None:
        """
        Checks unequality of two scraper objects created from given URLs.

        :param url1: URL of first object
        :param url2: URL of second object
        """
        assert self.ScraperClass(url1, None, False) != self.ScraperClass(url2,
            None, False)

