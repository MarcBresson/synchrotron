from synchrotron.comparaison import ComparaisonSvc
from synchrotron.configuration import OneConfig
from synchrotron.filter import FilterSvc


# filter interesting paths
def main():
    config = OneConfig.model_validate({})

    filter_svc = FilterSvc(config.filters, config.left)
    comparison_svc = ComparaisonSvc(config.comparaison, config.left, config.right)

    for file_path, file_details in filter_svc.walk():
        comparison_svc.compare()
        ...
