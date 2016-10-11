

class KubeStateProcessor:
    def __init__(self, kubernetes_check):
        self.kube_check = kubernetes_check

    def process(self, metric):
        try:
            getattr(self, metric.name)()
        except AttributeError:
            self.kube_check.log.debug("Unable to handle metric: {}".format(metric.name))
