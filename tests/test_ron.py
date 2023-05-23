import unittest


def gen_sampling_rate(file_ext, analysis_center, solution_type):
    """
    IGS files following the long filename convention require a content specifier
    Given the file extension, generate the content specifier
    """
    file_ext = file_ext.upper()
    sampling_rates = {
        "ERP": "01D",
        "BIA": "01D",
        "SP3": {
            ("COD", "GFZ", "GRG", "IAC", "JAX", "MIT", "WUM"): "05M",
            "ESA": {"FIN": "05M", "RAP": "15M", None: "15M"},
            None: "15M",
        },
        "CLK": {
            ("EMR", "IGS", "MIT", "SHA", "USN"): "05M",
            ("ESA", "GFZ", "GRG"): {"FIN": "30S", "RAP": "05M", None: "30S"},
            None: "30S",
        },
        "OBX": {"GRG": "05M", None: "30S"},
        "TRO": {"JPL": "30S", None: "01H"},
        "SNX": "01D",
    }
    if file_ext in sampling_rates:
        file_rates = sampling_rates[file_ext]
        if isinstance(file_rates, dict):
            center_rates = file_rates.get(analysis_center, file_rates.get(None))
            if isinstance(center_rates, dict):
                return center_rates.get(solution_type, center_rates.get(None))
            else:
                return center_rates
        else:
            return file_rates
    else:
        return "01D"


def gen_cddis_repro_specifiers(analysis_center, version, project, solution):
    center_mapping = {
        "ESA": {"version": "3"},
        "GFZ": {"version": "2"},
        "GRG": {"version": "6", "project": "RE3"},
        "IGS": {"solution": "SNX"},
        "JPL": {"project": "R3T"},
        "MIT": {"solution": "GE-"} if solution == "FIN" else {},
        "ULR": {"project": "TST"},
        "WHU": {"version": "2"},
    }

    center_specs = center_mapping.get(analysis_center, {})
    version = center_specs.get("version", version)
    project = center_specs.get("project", project)
    solution = center_specs.get("solution", solution)

    return version, project, solution


class tests_RON(unittest.TestCase):
    def testERP(self):
        self.assertEqual(gen_sampling_rate("ERP", "", ""), "01D")

    def testTROP(self):
        self.assertEqual(gen_sampling_rate("TRO", "JPL", ""), "30S")

    def testCLK(self):
        self.assertEqual(gen_sampling_rate("CLK", "GFZ", "FIN"), "30S")


if __name__ == "__main__":
    unittest.main()
