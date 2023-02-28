import unittest
from io import StringIO

import numpy as np

from ginan.io.sinex import snx_np_date, snx_date_np
from ginan.io.sinex.sinex import  Sinex



testdataset="""
+SATELLITE/IDENTIFIER
*
*SVN_ COSPAR ID SatCat Block__________ Comment__________________________________
*
 G001 1978-020A  10684 GPS-I           Launched 1978-02-22; NAVSTAR 1
 G002 1978-047A  10893 GPS-I           Launched 1978-05-13; NAVSTAR 2
 G003 1978-093A  11054 GPS-I           Launched 1978-10-07; NAVSTAR 3
 G004 1978-112A  11141 GPS-I           Launched 1978-12-11; NAVSTAR 4
*
-SATELLITE/IDENTIFIER
*
*-------------------------------------------------------------------------------
*
+SATELLITE/PRN
*
*SVN_ Valid_From____ Valid_To______ PRN Comment_________________________________
*
 G001 1978:053:00000 1985:199:00000 G04
 G002 1978:133:00000 1988:044:00000 G07
 G003 1978:279:00000 1992:140:00000 G06
 G004 1978:344:00000 1989:288:00000 G08
 G005 1980:040:00000 1984:133:00000 G05
 G006 1980:117:00000 1991:066:00000 G09
 G008 1983:195:00000 1993:125:00000 G11
 G009 1984:165:00000 1994:172:00000 G13
*
-SATELLITE/PRN
*
*-------------------------------------------------------------------------------
*
+SATELLITE/FREQUENCY_CHANNEL
*
*SVN_ Valid_From____ Valid_To______ chn Comment________________________________
*
 R701 2003:344:00000 2009:258:86399   1 [FC10]
 R701 2009:259:00000 2010:057:86399  -4 [Const_090916.glo]
 R711 2001:335:34200 2006:084:86399   2 [FC02]
 R711 2006:085:00000 2008:010:86399   7 [Const_060326.glo]
 R712 2004:361:00000 2007:037:86399   4 BSW
*
-SATELLITE/FREQUENCY_CHANNEL
*
*-------------------------------------------------------------------------------
*
+SATELLITE/MASS
*
*SVN_ Valid_From____ Valid_To______ Mass_[kg] Comment___________________________
*
 G001 1978:053:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G002 1978:133:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G003 1978:279:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G004 1978:344:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G005 1980:040:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G006 1980:117:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G008 1983:195:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G009 1984:165:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G010 1984:252:00000 0000:000:00000   455.000 GPS-I; [MA01]
 G011 1985:282:00000 0000:000:00000   455.000 GPS-I; [MA01]
*
-SATELLITE/MASS
*
*-------------------------------------------------------------------------------
*
+SATELLITE/TX_POWER
*
*SVN_ Valid_From____ Valid_To______ P[W] Comment________________________________
*
 G046 1999:280:00000 0000:000:00000   60  GPS-IIR-A; [TP01]; block mean
 G047 2003:355:00000 0000:000:00000   60  GPS-IIR-B; [TP01]; block mean
 G048 2008:075:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G049 2009:083:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G050 2009:229:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G051 2000:132:00000 0000:000:00000   60  GPS-IIR-A; [TP01]; block mean
 G052 2006:268:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G053 2005:269:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G054 2001:030:00000 0000:000:00000   60  GPS-IIR-A; [TP01]; block mean
 G055 2007:290:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
 G056 2003:029:00000 0000:000:00000   60  GPS-IIR-A; [TP01]; block mean
 G057 2007:354:00000 0000:000:00000  145  GPS-IIR-M; [TP01]; block mean
-SATELLITE/TX_POWER
+SATELLITE/YAW_BIAS_RATE
*
*SVN_ Valid_From____ Valid_To______   YB Yaw Rate  Comment________________________________
 G001 1978:053:00000 1985:199:00000    U   0.1999  Launched 1978-02-22; NAVSTAR 1; mass 453800. in previous svnav.dat.allgnss
 G002 1978:133:00000 1988:044:00000    U   0.1990  Launched 1978-05-13; NAVSTAR 2
 G003 1978:279:00000 1992:140:00000    U   0.1990  Launched 1978-10-07; NAVSTAR 3; mass 453800. and end date 1992-171 in previous svnav.dat.allgnss
 G004 1978:344:00000 1989:288:00000    U   0.1990  Launched 1978-12-11; NAVSTAR 4; mass 440900. in previous svnav.dat.allgnss
 G005 1980:040:00000 1984:133:00000    U   0.1990  Launched 1980-02-09; NAVSTAR 5; mass 462600. and end date 1993-125 in previous svnav.dat.allgnss
 G006 1980:117:00000 1991:066:00000    U   0.1990  Launched 1980-04-26; NAVSTAR 6; mass 462600. in previous svnav.dat.allgnss
 G008 1983:195:00000 1993:125:00000    U   0.1990  Launched 1983-07-14; NAVSTAR 8; mass 522200. and start date 1983-222 in previous svnav.dat.allgnss
 G009 1984:165:00000 1994:157:00000    U   0.1990  Launched 1984-06-13; NAVSTAR 9; mass 520400. and start date 1984-201 in previous svnav.dat.allgnss
-SATELLITE/YAW_BIAS_RATE
"""

class TestSinex(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sinex =Sinex()
        cls.sinex.read(StringIO(testdataset))

        pass
    #
    # @classmethod
    # def tearDown(cls) -> None:
    #     pass

    def test_sinexStrDateConvertor(self) -> None:
        input_str = "2010:058:25610"
        out = snx_date_np(input_str)
        self.assertEqual(out, np.datetime64('2010-02-27T07:06:50'))

    def test_sinexDateStrConvertor(self) -> None:
        input = np.datetime64('2010-02-27T07:06:50')
        output = snx_np_date(input)
        self.assertEqual(output,'2010:058:25610')

    def test_sinexMass(self) -> None:
        self.assertEqual(self.sinex.blocks['SATELLITE/MASS']['G005']['mass'],455.000)
        self.assertEqual(self.sinex.blocks['SATELLITE/MASS']['G001']['startDate'],  np.datetime64('1978-02-22T00:00:00'))


    def test_sinexTxPower(self) -> None:
        print(self.sinex.blocks)
        self.assertEqual(self.sinex.blocks['SATELLITE/TX_POWER']['G046']['power'], 60)
        self.assertEqual(self.sinex.blocks['SATELLITE/TX_POWER']['G048']['power'],145.000)
        self.assertEqual(self.sinex.blocks['SATELLITE/TX_POWER']['G046']['startDate'], np.datetime64('1999-10-07T00:00:00'))
        self.assertTrue(np.isnan(self.sinex.blocks['SATELLITE/TX_POWER']['G046']['endDate']))

