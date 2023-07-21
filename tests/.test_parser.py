import argparse
import unittest


def split_args(args_str):
    return args_str.split(",")


class TestArgumentParser(unittest.TestCase):
    def test_parser(self):
        parser = argparse.ArgumentParser(
            prog=__file__,
            description="Plot measurements related fittings",
            epilog="Text at the bottom of help",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("common_args", nargs=argparse.REMAINDER, help="common arguments")
        parser.add_argument("--db", default="127.0.0.1", type=str, help="Mongo database url [default 127.0.0.1]")
        parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
        parser.add_argument("--sat", type=split_args, required=True, help="Satellite name")
        parser.add_argument("--site", type=split_args, required=True, help="Site name")

        subparser = parser.add_subparsers(help="sub-command help")
        parser_meas_option = subparser.add_parser("meas", help="plotting measurements")
        parser_meas_option.add_argument("--field", type=split_args, required=True)
        # parser_meas_option.set_defaults(func=plot_measurements)

        args = parser.parse_args(
            [
                "meas",
                "--coll=ex41",
                "--sat=E13,E15,E?4,E11,G*",
                "--site=AGGO,ALIC",
                "--field=L125-Postfit,P125-Postfit",
            ]
        )

        self.assertEqual(args.coll, "ex41")
        self.assertEqual(args.sat, ["E13", "E15", "E?4", "E11", "G*"])
        self.assertEqual(args.site, ["AGGO", "ALIC"])
        self.assertEqual(args.field, ["L125-Postfit", "P125-Postfit"])
        self.assertEqual(args.common_args, [])
        self.assertEqual(args.db, "127.0.0.1")
        # self.assertEqual(args.func, plot_measurements)


if __name__ == "__main__":
    unittest.main()
