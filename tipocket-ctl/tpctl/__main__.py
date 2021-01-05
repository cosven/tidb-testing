from tpctl.app import cli
from tpctl.debug import debug
from tpctl.deploy import deploy


def main():
    cli.add_command(deploy)
    cli.add_command(debug)
    cli()


if __name__ == '__main__':
    main()
