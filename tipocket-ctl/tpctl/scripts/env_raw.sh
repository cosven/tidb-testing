# WARNING: All commands connect to `tidb` container of tidb pods by default.
# 	   As tidb pod has two containers
OUTPUT_DIR=output
CASE_POD_ID=$(argo get -n argo $DEPLOY_ID -o json \
              | jq -r '.status.nodes[] | select(.type == "Pod" and .templateName != "notify") | .id')
CLUSTER_NAMESPACE=$(argo get -n argo $DEPLOY_ID -o json \
                    | jq -r '.spec.templates[-1].container.command[2]' \
                    | grep -oP '\-namespace=".*?"' \
                    | grep -o '".*"' \
                    | sed -e 's/^"//' -e 's/"$//')

function get_grafana_port {
	echo $(kubectl -n $CLUSTER_NAMESPACE get svc -o json \
		       | jq -r '.items[].spec.ports[]
			        | select(.name == "http-grafana")
				| .nodePort')
}

function t_get_grafana_addr {
	grafana_port=$(get_grafana_port)
	host_ip=$(hostname)
	if [ "$grafana_port" == "" ]; then
		echo "Grafana is not ready yet, please run t_get_grafana_addr later."
	else
		echo "Grafana is on http://$host_ip:$grafana_port, username and password are both admin."
	fi
}

echo "available commands:"
echo "- t_log_case"
echo "- t_ls_pod"
echo "- t_log_pod {pod-name}"
echo "- t_ssh_pod {pod-name}"
echo "- t_get_grafana_addr"
echo ""
echo "logs are stored in ./$OUTPUT_DIR/"
t_get_grafana_addr # Print grafana port.


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
	if is_name_tidb "$1"; then
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

	if is_name_tidb "$1"; then
		kubectl -n $CLUSTER_NAMESPACE exec --stdin --tty $1 -c tidb -- /bin/sh
	else
		kubectl -n $CLUSTER_NAMESPACE exec --stdin --tty $1 -- /bin/sh
	fi
}

