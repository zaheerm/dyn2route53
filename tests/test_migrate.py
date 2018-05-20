from .context import dyn2route53
import unittest
from unittest import mock
from dyn2route53 import migrate


class TestConvertDynToRoute53Changes(unittest.TestCase):
    def _test_subzone_raises_on_unsupported_record(self, record_type: str):
        dyn_zone = mock.MagicMock()
        record = mock.MagicMock()
        type(record).fqdn = mock.PropertyMock(return_value="blah.blah")
        type(record).rec_name = mock.PropertyMock(return_value=record_type)
        dyn_zone.get_all_records.return_value = {"1": [record]}
        with self.assertRaises(migrate.MigrationNotSupported):
            migrate.convert_dyn_to_route53_changes("blah", dyn_zone)

    def test_soa_raises(self):
        return self._test_subzone_raises_on_unsupported_record("SOA")

    def test_ns_raises(self):
        return self._test_subzone_raises_on_unsupported_record("NS")


if __name__ == '__main__':
    unittest.main()
