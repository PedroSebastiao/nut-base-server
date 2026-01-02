import unittest

from nut_base_server.adapter.dummy_adapter import DummyAdapter
from nut_base_server.nut_server import NutServer


class TestNutServer(unittest.IsolatedAsyncioTestCase):
    def _mock_adapter(self):
        return DummyAdapter()

    def _mock(self):
        return NutServer(self._mock_adapter())

    async def test_build_var_list(self):
        server = self._mock()

        variables = await server._build_var_list()

        self.assertIn('VAR name device.mfr "Manufacturer"', variables)
