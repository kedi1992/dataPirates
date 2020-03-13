from lib.S3.price_comparision import PriceComparision
from lib.ec2.price_check import get_all_costing


def get_best_region(input_list):
    input_list = [{"type": "ec2",
                   "memory": 3,
                   "vcpu": 30,
                   "operatingSystem": "linux"},

                  {"type": "s3",
                   "storageClass": "Standard",
                   "storageCapacityInGB": "100000000000000000000000000000000000000000000000000000000000"}]

    ec2_parameter_check = False
    s3_paramter_check = False

    s3_cost_list = []
    ec2_price_list = []
    for service in input_list:
        total_cost_region_vise_cost = []
        if service["type"] == "s3":
            s3 = PriceComparision()
            s3_cost_list = s3.getCost(storageClass=service["storageClass"],
                                      storageCapacityInGB=service["storageCapacityInGB"])

        if service["type"] == "ec2":
            ec2_price_list = get_all_costing(vcpu=int(service["vcpu"]),
                                             memory=float(service["memory"]),
                                             operating_system=service["operatingSystem"])
            # if not ec2_price_list:
            #     return []

    print(s3_cost_list)
    print(ec2_price_list)

    # for s3_service in s3_cost_list:
    #     for ec2_service in ec2_price_list:
    #         if s3_service["region"] == ec2_service["region"]:
    #             consolidated_cost = {}
    #             consolidated_cost["conslidateCost"] = ec2_service["onDemandMonthlyCost"] + s3_service[""]
    #             total_cost_region_vise_cost.append()


get_best_region("")
