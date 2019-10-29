FROM lachlanevenson/k8s-kubectl:{{ k8s_kubectl_version }} AS k8scli

FROM rancher/cli2:{{ rancher_cli_version }}

COPY --from=k8scli /usr/local/bin/kubectl /usr/local/bin

ENTRYPOINT []