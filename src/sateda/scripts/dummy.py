import argparse


def plot_measurements(args):
    print("Plotting measurements...")
    print(args)


def show_state(args):
    print("Showing state...")
    print(args)


def main():
    # Create a parent parser for the main options
    main_parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot satellite related fittings",
        epilog="Text at the bottom of help",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False,
    )

    main_parser.add_argument(
        "--db",
        default="127.0.0.1",
        type=str,
        help="Mongo database url [default 127.0.0.1]",
    )
    main_parser.add_argument("--coll", type=str, required=True, help="Mongo collection to plot")
    main_parser.add_argument("--sat", type=str, nargs="+", required=True, help="Satellite name")
    main_parser.add_argument("--site", type=str, nargs="+", required=True, help="Site name")
    main_parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")

    # Create the main parser with no arguments
    parser = argparse.ArgumentParser(
        prog=__file__,
        description="Plot measurements related fittings",
        add_help=False,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Create subparsers for each subcommand
    subparsers = parser.add_subparsers(help="sub-command help")

    # Create the 'meas' subparser
    meas_parser = subparsers.add_parser(
        "meas",
        parents=[main_parser],
        add_help=False,
        help="plotting measurements",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    meas_parser.add_argument("--field", type=str, required=True, nargs="+")
    meas_parser.set_defaults(func=plot_measurements)

    # Create the 'state' subparser
    state_parser = subparsers.add_parser(
        "state",
        parents=[main_parser],
        add_help=False,
        help="show state",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    state_parser.set_defaults(func=show_state)

    # Add a --help option to each subparser
    for subparser in [parser, meas_parser, state_parser]:
        subparser._positionals.title = "positional arguments"
        subparser._optionals.title = "optional arguments"
        # subparser._optionals.description = None

        # subparser.set_defaults(func=lambda args: subparser.print_help() if args.help else None)

    args = parser.parse_args()
    print(args)

    if args.func:
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
