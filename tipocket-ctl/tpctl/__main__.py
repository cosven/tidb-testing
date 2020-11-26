from tpctl.app import cli
from tpctl.prepare import prepare


def main():
    cli.add_command(prepare)
    cli()


if __name__ == '__main__':
    main()
