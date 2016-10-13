

class KubeStateProcessor:
    def __init__(self, kubernetes_check):
        self.kube_check = kubernetes_check

    def process(self, message):
        """
        Search this class for a method with the same name of the message and
        invoke it. Log some info if method was not found.
        """
        try:
            getattr(self, message.name)(message)
        except AttributeError:
            self.kube_check.log.debug("Unable to handle metric: {}".format(message.name))

    def _eval_metric_condition(self, metric):
        """
        Some metrics contains conditions, labels that have "condition" as name and "true", "false", or "unknown"
        as value. The metric value is expected to be a gauge equal to 0 or 1 in this case.

        This function acts as an helper to iterate and evaluate metrics containing conditions
        and returns a tuple containing the name of the condition and the boolean value.
        For example:

        metric {
          label {
            name: "condition"
            value: "true"
          }
          # other labels here
          gauge {
            value: 1.0
          }
        }

        would return `("true", True)`.

        Returns `None, None` if metric has no conditions.
        """
        val = bool(metric.gauge.value)
        for label in metric.label:
            if label.name == 'condition':
                return label.value, val

        return None, None

    def _extract_label_value(self, name, labels):
        """
        Search for `name` in labels name and returns
        corresponding value.
        Returns None if name was not found.
        """
        for label in labels:
            if label.name == name:
                return label.value
        return None

    def kube_node_status_capacity_cpu_cores(self, message):
        metric_name = 'kubernetes.node.cpu_capacity'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(metric.label[0].value)]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_capacity_memory_bytes(self, message):
        metric_name = 'kubernetes.node.memory_capacity'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_capacity_pods(self, message):
        metric_name = 'kubernetes.node.pods_capacity'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_allocateable_cpu_cores(self, message):
        metric_name = 'kubernetes.node.cpu_allocatable'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_allocateable_memory_bytes(self, message):
        metric_name = 'kubernetes.node.memory_allocatable'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_allocateable_pods(self, message):
        metric_name = 'kubernetes.node.pods_allocatable'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_deployment_status_replicas_available(self, message):
        metric_name = 'kubernetes.deployment.replicas_available'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['{}:{}'.format(label.name, label.value) for label in metric.label]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_deployment_status_replicas_unavailable(self, message):
        metric_name = 'kubernetes.deployment.replicas_unavailable'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['{}:{}'.format(label.name, label.value) for label in metric.label]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_deployment_status_replicas_updated(self, message):
        metric_name = 'kubernetes.deployment.replicas_updated'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['{}:{}'.format(label.name, label.value) for label in metric.label]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_deployment_spec_replicas(self, message):
        metric_name = 'kubernetes.deployment.replicas_desired'
        for metric in message.metric:
            val = metric.gauge.value
            tags = ['{}:{}'.format(label.name, label.value) for label in metric.label]
            self.kube_check.publish_gauge(self, metric_name, val, tags)

    def kube_node_status_ready(self, message):
        service_check_name = 'kube_node_status_ready'
        for metric in message.metric:
            name, val = self._eval_metric_condition(metric)
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            if name == 'true' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.OK, tags=tags)
            elif name == 'false' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.CRITICAL, tags=tags)
            elif name == 'unknown' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.UNKNOWN, tags=tags)

    def kube_node_status_out_of_disk(self, message):
        service_check_name = 'kube_node_status_out_of_disk'
        for metric in message.metric:
            name, val = self._eval_metric_condition(metric)
            tags = ['host:{}'.format(self._extract_label_value("node", metric.label))]
            if name == 'true' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.CRITICAL, tags=tags)
            elif name == 'false' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.OK, tags=tags)
            elif name == 'unknown' and val:
                self.kube_check.service_check(service_check_name, self.kube_check.UNKNOWN, tags=tags)
