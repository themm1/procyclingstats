from typing import Any

from procyclingstats import Scraper

from .fixtures_utils import FixturesUtils


def method_test(correct_method: Any, parsed_method: Any) -> None:
    """Compare correct_method against parsed_method, handling nested structures.

    This is a *missingness* check, not an exact equality check.

    It only fails on:
    - None vs non-None mismatches
    - empty list/tuple vs non-empty list/tuple mismatches

    Scalars are not compared for equality/truthiness.
    """

    def _is_seq(v: Any) -> bool:
        return isinstance(v, (list, tuple))

    def _walk(correct_v: Any, parsed_v: Any, path: str) -> None:
        assert (correct_v is None) == (parsed_v is None), (
            f"None mismatch at {path}: "
            f"correct={type(correct_v).__name__}({correct_v!r}) "
            f"parsed={type(parsed_v).__name__}({parsed_v!r})"
        )

        # If both are sequences, explicitly check empty-vs-non-empty.
        # (zip() would otherwise skip comparing anything when one side is empty).
        if _is_seq(correct_v) and _is_seq(parsed_v):
            assert (len(correct_v) == 0) == (len(parsed_v) == 0), (
                f"List emptiness mismatch at {path}: "
                f"correct has {len(correct_v)} items, parsed has {len(parsed_v)} items"
            )
            for i, (p_item, c_item) in enumerate(zip(parsed_v, correct_v)):
                _walk(c_item, p_item, f"{path}[{i}]")
            return

        # Recurse dicts by shared keys.
        if isinstance(correct_v, dict) and isinstance(parsed_v, dict):
            for k, v in parsed_v.items():
                if k in correct_v:
                    _walk(correct_v[k], v, f"{path}.{k}")
            return

        # Scalars / type mismatches: intentionally do not compare values.
        return

    _walk(correct_method, parsed_method, "value")


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
