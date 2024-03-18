import unittest
from io import StringIO

import numpy as np


from sateda.io.grace import gracetime_converter
from sateda.io.grace.sca import GraceSCA
from sateda.io.grace.acc import GraceACC
from sateda.io.grace.gnv import GraceGNV


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


    def test_readGNV(self):
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
            "754660800 C E 1011395.732245176 4745559.70202079 -4868027.183942866 0.0005786928411060063 0.0008524530942478945 0.0009432241422033113 -962.3168374296575 -5291.898128867633 -5378.369613978083 1.458292364860945e-06 2.109387396220108e-06 2.220017789318375e-06  00000000\n"
            "754660801 C E 1010432.412795031 4740264.981018713 -4873402.562407305 0.0005786292461106121 0.0008520563168698022 0.0009438202366416082 -964.3219718804309 -5297.542700599725 -5372.386186615314 1.458158702443524e-06 2.108723556941607e-06 2.219032918037747e-06  00000000\n"
            "754660802 C E 1009467.088396263 4734964.618861085 -4878771.954184867 0.0005785658496668229 0.0008516595751533996 0.0009444154080211907 -966.3267357167714 -5303.180438477671 -5366.396241532046 1.458025160371547e-06 2.108059404549736e-06 2.218052662467699e-06  00000000\n"
            "754660803 C E 1008499.759421174 4729658.622385069 -4884135.35276159 0.0005785026526794063 0.0008512628657403702 0.0009450096499537609 -968.3311255344032 -5308.81133588869 -5360.39978623118 1.457891738274815e-06 2.107394989218136e-06 2.217077064680048e-06  00000000\n"
            "754660804 C E 1007530.426245447 4724346.998434445 -4889492.751631006 0.0005784396560541673 0.0008508661852748058 0.0009456029561272788 -970.3351379286656 -5314.435386229177 -5354.396828222976 1.457758435766647e-06 2.106730361122204e-06 2.216106166236744e-06  00000000\n"
            "754660805 C E 1006559.089248149 4719029.753859594 -4894844.144294167 0.0005783768606979533 0.000850469530402273 0.0009461953203068284 -972.3387694945203 -5320.052582904714 -5348.387375025052 1.457625252444493e-06 2.106065570415661e-06 2.215140008158726e-06  00000000\n"
            "754660806 C E 1005585.748811733 4713706.895517494 -4900189.524259648 0.0005783142675186589 0.0008500728977687824 0.0009467867363355334 -974.3420168265583 -5325.662919330061 -5342.371434162368 1.457492187890553e-06 2.105400667207068e-06 2.214178630894792e-06  00000000\n"
            "754660807 C E 1004610.405322041 4708378.430271698 -4905528.885043546 0.0005782518774252374 0.0008496762840196977 0.0009473771981355078 -976.3448765190088 -5331.266388929182 -5336.349013167213 1.457359241672388e-06 2.104735701536623e-06 2.21322207429096e-06  00000000\n"
            "754660808 C E 1003633.05916831 4703044.364992348 -4910862.2201695 0.0005781896913277083 0.0008492796857986105 0.0009479666997088195 -978.3473451657476 -5336.862985135232 -5330.320119579205 1.457226413343503e-06 2.104070723353624e-06 2.212270377560947e-06  00000000\n"
            "754660809 C E 1002653.710743172 4697704.706556134 -4916189.523168691 0.0005781277101371689 0.0008488830997462224 0.0009485552351384488 -980.3494193603037 -5342.452701390573 -5324.28476094528 1.457093702443894e-06 2.103405782494939e-06 2.211323579258277e-06  00000000\n"
        )
        data_gnv = GraceGNV()
        data_gnv.read(file_or_string=input_data)
        self.assertEqual(data_gnv.yaml_dict["header"]["dimensions"]["num_records"], 86400)
        self.assertEqual(data_gnv.data[4]["gps_time"], np.datetime64("2023-12-01T00:00:04"))
        self.assertEqual(data_gnv.data[2]["GFO_id"], "C")
        self.assertEqual(data_gnv.data[2]["xpos"], 1009467.088396263)
        self.assertEqual(data_gnv.data[2]["ypos"], 4734964.618861085)



if __name__ == "__main__":
    unittest.main()
