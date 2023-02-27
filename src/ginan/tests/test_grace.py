import unittest
from io import StringIO

import numpy as np


from ginan.io.grace import gracetime_converter
from ginan.io.grace.sca import GraceSCA

class TestGrace(unittest.TestCase):
    def setUp(self) -> None:
        print("In method", self._testMethodName)

    def test_checkingTime(self):
        time = gracetime_converter(694267200)
        self.assertEqual(time, np.datetime64('2022-01-01T00:00:00'))
        time = gracetime_converter(336657595.000000)
        self.assertEqual(time, np.datetime64('2010-09-01T23:59:55.00'))

    def test_readSCA(self):
        #Just a small part of a file.
        input_data = StringIO("header:\n"
                              "  dimensions:\n"
                              "    num_records: 86400\n"
                              "  global_attributes:\n"
                              "    acknowledgement: GRACE-FO is a joint mission of the US National Aeronautics and Space Administration and the German Research Center for Geosciences.  Use the digital object identifier provided in the id attribute when citing this data.  See https://podaac.jpl.nasa.gov/CitingPODAAC\n"
                              "    conventions: CF-1.6, ACDD-1.3, ISO 8601\n"
                              "    creator_email: gracefo@podaac.jpl.nasa.gov\n"
                              "# End of YAML header\n"
                              "694267200 C 23 0.4808017050541642 -0.2620552641913284 -0.1627298892823009 -0.8207775228342311 8.773424053941323e-07 00000000\n"
                              "694267201 C 23 0.4808916770459788 -0.261600538986203 -0.1624636205713502 -0.8209226059770532 8.773424053941323e-07 00000000\n"
                              "694267202 C 23 0.4809815362327415 -0.2611458377574534 -0.1621972689526377 -0.8210673901758849 8.773424054650244e-07 00000000\n"
                              "694267203 C 23 0.4810714452303146 -0.2606910513742197 -0.1619308900264623 -0.8212118041251759 8.773424054650244e-07 10000010\n"
                              )
        data_sca = GraceSCA()
        data_sca.read(file_or_string=input_data)
        self.assertEqual(data_sca.yaml_dict["header"]["dimensions"]["num_records"], 86400)
        self.assertEqual(data_sca.data[2]['gps_time'], np.datetime64('2022-01-01T00:00:02'))
        self.assertEqual(data_sca.data[2]['GFO_id'], 'C')
        self.assertEqual(data_sca.data[2]['quaternioni'], 0.4809815362327415)
        self.assertEqual(data_sca.data[2]['quaternionj'], -0.2611458377574534)
        self.assertEqual(data_sca.data[3]['flag'], 128+2)





if __name__ == '__main__':
    unittest.main()