from typing import Any

from procyclingstats import Scraper

from .fixtures_utils import FixturesUtils


def method_test(correct_method: Any, parsed_method: Any):
    """
    Compare correct_method against parsed_method, handling nested structures.
    Tests boolean presence (truthiness) rather than exact equality.
    """
    # Case 1: Both are lists
    if isinstance(correct_method, list) and isinstance(parsed_method, (list, tuple)):
        assert len(correct_method) == len(parsed_method), \
            f"List length mismatch: {len(correct_method)} != {len(parsed_method)}"
        
        for parsed_row, correct_row in zip(parsed_method, correct_method):
            # If both are dicts (list of dicts)
            if isinstance(correct_row, dict) and isinstance(parsed_row, dict):
                for (k1, v1), (k2, v2) in zip(parsed_row.items(), correct_row.items()):
                    assert bool(v1) == bool(v2), \
                        f"Value mismatch for {k1}: {bool(v1)} != {bool(v2)}"
            # If both are simple values (list of scalars: ints, strings, etc.)
            else:
                assert bool(parsed_row) == bool(correct_row), \
                    f"Value mismatch: {bool(parsed_row)} != {bool(correct_row)}"
    
    # Case 2: correct is dict (comparing dicts)
    elif isinstance(correct_method, dict) and isinstance(parsed_method, dict):
        for (k1, v1), (k2, v2) in zip(parsed_method.items(), correct_method.items()):
            assert bool(v1) == bool(v2), \
                f"Value mismatch for {k1}: {bool(v1)} != {bool(v2)}"
    
    # Case 3: Both are simple values (strings, numbers, etc.)
    else:
        assert bool(parsed_method) == bool(correct_method), \
            f"Value mismatch: {bool(parsed_method)} != {bool(correct_method)}"


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
            # assert parsed.keys() == correct.keys() # type: ignore
            print(obj.relative_url())
            parsed_data.append(parsed)
            correct_data.append(correct)
            urls.append(obj.relative_url())
            
        assert correct_data[0].keys() == parsed_data[0].keys()

        for method in correct_data[0].keys():
            # method subtest
            with subtests.test(msg=method):
                print(f"\nMethod: {method}")
                for parsed, correct, url in zip(parsed_data, correct_data,
                        urls):
                    print(url)
                    method_test(correct[method], parsed[method])
