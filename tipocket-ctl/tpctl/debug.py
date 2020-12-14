import inspect

import click

HELP_STRING = """
generate debug environment into .env file.

    Run `source .env` to get commands.

\b
You can find argument {deploy-id} and {cluster-namespace} in slack notification:
============ Slack Notification ======================
argo workflow
tpctl-hello-test-tpctl-q948q
^^^ {DEPLOY ID} ^^^^^^^^^^^^
...
cmd
/bin/hello ... -namespace="tpctl-hello-test-tpctl" ...
               ^^^ {CLUSTER NAMESPACE} ^^^^^^^^^^^^^^^^^^
=======================================================
"""


def generate_script(deploy_id, cluster_namespace):
    variables = inspect.cleandoc("""
    DEPLOY_ID={}
    CLUSTER_NAMESPACE={}
    """.format(deploy_id, cluster_namespace))

    functions = inspect.cleandoc("""
    # WARNING: All commands connect to `tidb` container of tidb pods by default.
    # 	   As tidb pod has two containers
    OUTPUT_DIR=output
    CASE_POD_ID=$(argo get -n argo $DEPLOY_ID -o json | jq -r '.status.nodes[] | select(.type == "Pod" and .templateName != "notify") | .id')

    echo "available commands:"
    echo "- t_log_case"
    echo "- t_ls_pod"
    echo "- t_log_pod {pod-name}"
    echo "- t_ssh_pod {pod-name}"
    echo ""
    echo "logs are stored in ./$OUTPUT_DIR/"

    mkdir -p $OUTPUT_DIR

    function is_name_tidb {
        if [[ "$1" =~ .+-tidb-[0-9]+$ ]]; then
            return 0
        else
            return 1
        fi
    }

    function output_filepath {
        echo "$OUTPUT_DIR/$1"
    }

    function get_argo_steps {
        sed -n '/STEP */,$p' <(argo get -n argo $DEPLOY_ID)
    }

    function t_log_case {
        OP=$(output_filepath log_case)
        kubectl logs --namespace argo -c main $CASE_POD_ID > $OP
        echo "log stored in $OP"
    }

    function t_ls_pod {
        kubectl -n $CLUSTER_NAMESPACE get pods
    }

    function t_log_pod {
        if [ "$1" == "" ]; then
            echo "{pod-name} not set"
            echo "Usage: t_log_pod {pod-name}"
            return 1
        fi

        OP=$(output_filepath $1)
        if [[ $(is_name_tidb $1) -eq 0 ]]; then
            kubectl logs --namespace $CLUSTER_NAMESPACE $1 -c tidb > $OP
        else
            kubectl logs --namespace $CLUSTER_NAMESPACE $1 > $OP
        fi
        echo "log stored in $OP"
    }

    function t_ssh_pod {
        if [ "$1" == "" ]; then
            echo "{pod-name} not set"
            echo "Usage: t_ssh_pod {pod-name}"
            return 1
        fi

        if [[ $(is_name_tidb $1) -eq 0 ]]; then
            kubectl -n $CLUSTER_NAMESPACE exec --stdin --tty $1 -c tidb -- /bin/sh
        else
            kubectl -n $CLUSTER_NAMESPACE exec --stdin --tty $1 -- /bin/sh
        fi
    }

    """)
    return variables + '\n' + functions


def print_debug_help():
    click.echo('generate .env in current directory')
    click.echo('Run:')
    click.secho('source .env', fg='green')
    click.echo('to get debug commands.')


@click.command(help=HELP_STRING)
@click.option('--deploy-id', help='id of test argo workflow')
@click.option('--cluster-namespace', help='namespace of cluster running our test')
def debug(**params):
    """
    Dependency: argo and kubectl are installed and properly configured in current machine.
    """
    deploy_id = params['deploy_id']
    cluster_namespace = params['cluster_namespace']

    if deploy_id is None or cluster_namespace is None:
        click.echo('No deploy-id or cluster-namespace specified')
        click.echo('Refer to slack notification')
        click.echo('Or run:')
        click.secho('tpctl debug --help', fg='green')
        return

    with open(".env", 'wt') as f:
        f.write(generate_script(
            deploy_id=deploy_id,
            cluster_namespace=cluster_namespace
        ))
    print_debug_help()
