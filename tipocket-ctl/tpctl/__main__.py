from tpctl.app import cli
from tpctl.debug import debug
from tpctl.prepare import prepare


def main():
    cli.add_command(prepare)
    cli.add_command(debug)
    cli()


if __name__ == '__main__':
    main()
