import unittest
from io import StringIO

import numpy as np


from sateda.io.grace import gracetime_converter
from sateda.io.grace.sca import GraceSCA
from sateda.io.grace.acc import GraceACC


class TestGrace(unittest.TestCase):
    def setUp(self) -> None:
        print("In method", self._testMethodName)

    def test_checkingTime(self):
        time = gracetime_converter(694267200)
        self.assertEqual(time, np.datetime64("2022-01-01T00:00:00"))
        time = gracetime_converter(336657595.000000)
        self.assertEqual(time, np.datetime64("2010-09-01T23:59:55.00"))

    def test_readSCA(self):
        # Just a small part of a file.
        input_data = StringIO(
            "header:\n"
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
        self.assertEqual(data_sca.data[2]["gps_time"], np.datetime64("2022-01-01T00:00:02"))
        self.assertEqual(data_sca.data[2]["GFO_id"], "C")
        self.assertEqual(data_sca.data[2]["quaternioni"], 0.4809815362327415)
        self.assertEqual(data_sca.data[2]["quaternionj"], -0.2611458377574534)
        self.assertEqual(data_sca.data[3]["flag"], 128 + 2)

    def test_readACC(self):
        # Just a small part of a file.
        input_data = StringIO(
            "header:\n"
            "  dimensions:\n"
            "    num_records: 86400\n"
            "  global_attributes:\n"
            "    acknowledgement: GRACE-FO is a joint mission of the US National Aeronautics and Space Administration and the German Research Center for Geosciences.  Use the digital object identifier provided in the id attribute when citing this data.  See https://podaac.jpl.nasa.gov/CitingPODAAC\n"
            "    conventions: CF-1.6, ACDD-1.3, ISO 8601\n"
            "    creator_email: gracefo@podaac.jpl.nasa.gov\n"
            "# End of YAML header\n"
            "674222400 D 3.059866044861098e-07 1.096720902532043e-05 -1.773003005771745e-07 0 0 0 -7.68132765143681e-10 -3.563725846862561e-10 -7.784822128559752e-11  00000000\n"
            "674222401 D 3.059841566157722e-07 1.096717634478874e-05 -1.772833088009533e-07 0 0 0 8.635580550224249e-12 -9.769324531450915e-10 1.168896320486214e-10  00000000\n"
            "674222402 D 3.059811077799194e-07 1.096715720100721e-05 -1.772686063383453e-07 0 0 0 2.042349118566648e-10 -3.933115137983394e-10 1.705342913611084e-10  00000000\n"
            "674222403 D 3.059772845019512e-07 1.0967159650143e-05 -1.77257500980131e-07 0 0 0 -6.17492130507471e-10 -6.064094966343696e-10 -9.02837103928093e-10  00000000\n"
            "674222404 D 3.059724824652382e-07 1.096719191898319e-05 -1.772512750432691e-07 0 0 0 1.954234948570116e-10 -7.709326090718179e-10 1.812147159862322e-10  00000000\n"
            "674222405 D 3.059664939493353e-07 1.096726152302472e-05 -1.772510597492892e-07 0 0 0 -5.698028435870924e-10 8.393763507179747e-10 1.428284675742983e-11  00000000\n"
            "674222406 D 3.05959142257784e-07 1.096737423467364e-05 -1.772576892938087e-07 0 0 0 1.270115447288669e-09 -4.286852259720905e-10 1.250419995253998e-10  00000000\n"
            "674222407 D 3.059503203771148e-07 1.096753297572507e-05 -1.772715446698303e-07 0 0 0 -6.125790179584634e-10 1.493257028648671e-10 4.883913191622128e-10  00000000\n"
            "674222408 D 3.059400302328715e-07 1.096773673236969e-05 -1.772924009726744e-07 0 0 0 -1.090919401530215e-09 3.155740089783152e-10 2.456737180212459e-10  00000000\n"
        )
        data_acc = GraceACC()
        data_acc.read(file_or_string=input_data)
        self.assertEqual(data_acc.yaml_dict["header"]["dimensions"]["num_records"], 86400)
        self.assertEqual(data_acc.data[4]["gps_time"], np.datetime64("2021-05-14T00:00:04"))
        self.assertEqual(data_acc.data[2]["GFO_id"], "D")
        self.assertEqual(data_acc.data[2]["lin_accl_x"], 3.059811077799194e-07)
        self.assertEqual(data_acc.data[2]["lin_accl_y"], 1.096715720100721e-05)


if __name__ == "__main__":
    unittest.main()
