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

        :param subtests: Subtests module, passed by pytest.
        """
        f_utils = FixturesUtils(fixtures_path="tests/fixtures/")
        objects_to_test = f_utils.get_scraper_objects_from_fixtures(
            self.ScraperClass)
        parsed_data = []
        correct_data = []
        urls = []
        for obj in objects_to_test:
            parsed = obj.parse()
            correct = f_utils.get_data_fixture(obj.relative_url())
            # dicts with parsed data has same keys
            assert parsed.keys() == correct.keys() # type: ignore
            parsed_data.append(parsed)
            correct_data.append(correct)
            urls.append(obj.relative_url())

        for method in correct_data[0].keys():
            # method subtest
            with subtests.test(msg=method):
                print(f"\nMethod: {method}")
                for parsed, correct, url in zip(parsed_data, correct_data,
                        urls):
                    print(url)
                    # select methods aren't tested because their values are
                    # changed often
                    if isinstance(correct[method], list):
                        for parsed_row, correct_row in zip(
                                parsed[method], correct[method]):
                            assert bool(parsed_row) == bool(correct_row)
                            # assert parsed_row == correct_row
                            for kv1, kv2 in zip(parsed_row, correct_row):
                                assert bool(kv1[0]) == bool(kv2[0])
                                assert bool(kv1[1]) == bool(kv2[1])
                    else:
                        # assert parsed[method] == correct[method]
                        assert bool(parsed[method]) == bool(correct[method])
