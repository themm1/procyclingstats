import pytest
from pcs_scraper import Scraper
from pytest_subtests import subtests

from .fixtures_utils import FixturesUtils


class ScraperTestBaseClass:
    """
    Base class for scraper classes testing. Scraper testing class that extends
    this base class should override `ScraperClass` attribute to the class that
    it's testing e.g. `TestRider` should override to `Rider`.
    """
    ScraperClass = Scraper

    def test_parser(self, subtests: subtests) -> None:
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
            parsed = obj.parse()
            correct = f.get_data_fixture(obj.relative_url())
            # dicts with parsed data has same keys
            assert parsed.keys() == correct.keys()
            parsed_data.append(parsed)
            correct_data.append(correct)

        for method in correct_data[0].keys():
            # method subtest
            with subtests.test(msg=method):
                for parsed, correct in zip(parsed_data, correct_data):
                    if isinstance(correct[method], list):
                        for parsed_row, correct_row in zip(
                                parsed[method], correct[method]):
                            assert parsed_row == correct_row
                    else:
                        assert parsed[method] == correct[method]
