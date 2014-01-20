from kamboo.utils import unique_list_of_dict
from kamboo.utils import compare_list_of_dict
from kamboo.utils import clean_null_items
from kamboo.utils import wait_to_complete

from kamboo.exceptions import ValidationError
from kamboo.exceptions import TimeOutException

from tests import unittest


class TestUtils(unittest.TestCase):
    """
    Unit Test for Utility of Kamboo
    """

    def test_unique_list_of_dict(self):

        input_normal = [{"A": "a"}, {"A": "a"}, {"A": "b"}]
        output_normal = [{"A": "a"}, {"A": "b"}]
        self.assertEquals(output_normal, unique_list_of_dict(input_normal))

        input_exception = {"A": "a"}
        with self.assertRaises(ValidationError):
            unique_list_of_dict(input_exception)

    def test_compare_list_of_dict(self):

        input_normal_1 = [{"A": "a"}, {"A": "b"}]
        input_normal_2 = [{"A": "a"}, {"B": "b"}]
        output_normal = {"Add": [{"B": "b"}], "Remove": [{"A": "b"}]}
        self.assertEquals(output_normal, compare_list_of_dict(
            input_normal_1, input_normal_2))

        input_normal_1 = [{"A": "a"}, {"A": "b"}]
        input_normal_2 = [{"A": "a"}, {"A": "b"}]
        output_normal = {"Add": [], "Remove": []}
        self.assertEquals(output_normal, compare_list_of_dict(
            input_normal_1, input_normal_2))

        input_normal = [{"A": "a"}, {"A": "b"}]
        input_exception = {"A": "a"}
        with self.assertRaises(ValidationError):
            compare_list_of_dict(input_exception, input_normal)

    def test_clean_null_items(self):

        input_normal = {"A": None, "B": [], "C": False, "D": 0}
        output_normal = {"C": False, "D": 0}
        self.assertEquals(output_normal, clean_null_items(input_normal))

    def test_wait_to_complete(self):

        class A(object):
            @property
            def status(self):
                return "pending"
        a = A()

        with self.assertRaises(TimeOutException):
            wait_to_complete(resource=a, expected_status="available",
                             unit=0.1, timeout=0.1)
