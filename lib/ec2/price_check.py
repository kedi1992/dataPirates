"""
https://calculator.aws/pricing/1.0/ec2/manifest.json
https://calculator.aws/pricing/1.0/ec2/region/ap-northeast-1/ondemand/linux/index.json
https://calculator.aws/pricing/1.0/ec2/region/ap-northeast-1/reserved-instance/linux/index.json

https://calculator.aws/pricing/1.0/datatransfer/index.json
https://calculator.aws/pricing/1.0/ec2/region/ap-east-1/ebs/index.json

https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-instance-savings-plan-ec2-calc/t3.xlarge/Asia%20Pacific%20(Hong%20Kong)/Linux/NA/Shared/index.json
https://b0.p.awsstatic.com/pricing/2.0/meteredUnitMaps/computesavingsplan/USD/current/compute-instance-savings-plan-ec2-calc/c5.2xlarge/Asia%20Pacific%20(Hong%20Kong)/Linux/NA/Shared/index.json

"""
import requests
import os
import json
import urllib3
urllib3.disable_warnings()
region_path = os.path.join(os.path.dirname(__file__), "region")
region_mapping = os.path.join(os.path.dirname(os.path.dirname(__file__)), "regionMapping.json")

with open(region_mapping) as region_mapping_dp:
    region_mapping_actual: dict = json.load(region_mapping_dp)

region_mapping_json = {v: k for k, v in region_mapping_actual.items()}

print(region_mapping)


# with open(os.path.dirname(__file__))


# glob.glob()

def get_all_region_related_ec2():
    url = "https://calculator.aws/pricing/1.0/ec2/manifest.json"
    response = requests.get(url, verify=False)
    result = response.json()["ec2"]
    # print(result)
    # result = ['ap-south-1', 'eu-north-1']
    return result


def get_all_download_path(operating_system=None, region=None, pricing_strategy=None):
    result = []
    for dirpath, dirnames, files in os.walk(os.path.join(os.path.dirname(__file__), "region"), topdown=False):
        for file in files:
            file_location = os.path.join(dirpath, file)
            if not (os.path.isfile(file_location) and ".json" in file_location):
                continue

            if operating_system and not (operating_system.lower() + "-" in file_location):
                continue

            if region and not (region.lower() == os.path.basename(os.path.dirname(file_location))):
                continue

            if pricing_strategy and not (pricing_strategy.lower() in file_location):
                continue

            result.append(file_location)

    return result


def download_information(remote_url, file_name, download_location):
    print(remote_url)
    print(file_name)
    print(download_location)
    response = requests.get(remote_url, verify=False)
    print(response.status_code)
    try:
        os.makedirs(download_location, exist_ok=True)
        download_file_location = os.path.join(download_location, file_name)
        result_json = response.json()
        if result_json:
            with open(download_file_location, mode="w") as fw:
                json.dump(result_json, fp=fw, indent=4)
    except Exception as e:
        print("Related region no information found ")
        print(remote_url)


def download_all_region_related_info(operating_system='linux'):
    print(region_path)
    if os.path.exists(region_path):
        print("No need to download data")
        return

    os.makedirs(region_path, exist_ok=True)
    all_region = get_all_region_related_ec2()
    for region in all_region:
        ondemand_url = "https://calculator.aws/pricing/1.0/" \
                       "ec2/region/{region}/{category}/{os}/index.json".format(region=region,
                                                                               category="ondemand",
                                                                               os=operating_system)
        reserved_url = "https://calculator.aws/pricing/1.0/" \
                       "ec2/region/{region}/{category}/{os}/index.json".format(region=region,
                                                                               category="reserved-instance",
                                                                               os='linux')

        download_location = os.path.join(region_path, region)

        download_information(remote_url=ondemand_url,
                             file_name=operating_system + "-onedemand.json",
                             download_location=download_location,
                             )

        download_information(remote_url=reserved_url,
                             file_name=operating_system + "-reserved-instance.json",
                             download_location=download_location,
                             )


def get_ram(product):
    if product["attributes"].get("aws:ec2:memory"):
        product_memory = float(product["attributes"]["aws:ec2:memory"].replace("GiB", "").strip())
        return product_memory
    # print("It don't have aws:ec2:memory")
    return 0


def get_vcpu(product):
    if product["attributes"].get("aws:ec2:vcpu"):
        product_vcpu = int(product["attributes"]["aws:ec2:vcpu"].strip())
        print(product_vcpu)
        return product_vcpu
    # print("It don't have aws:ec2:memory")

    return 0


def get_product_price(product):
    if product.get("price") or product["price"].get("USD"):
        return float(product["price"].get("USD"))
    return 0


def compare_against_price(price_list, compair_product, filter_ondemand=None):
    best_result = compair_product
    for product in price_list:

        if filter_ondemand:
            print("on demand filter acitvated")
            if product.get("calculatedPrice") and best_result.get("calculatedPrice"):
                if not (float(product["calculatedPrice"]["onDemandRate"]["USD"]) \
                        < float(best_result["calculatedPrice"]["onDemandRate"]["USD"])):
                    continue
            else:
                continue
        elif not get_product_price(product) <= get_product_price(best_result):
            continue

        if not get_ram(product) >= get_ram(best_result):
            continue

        if not get_vcpu(product) >= get_vcpu(best_result):
            continue

        best_result = product

    return best_result


def filter_result(price_list, ram=9, vcpu=4, filter_ondemand=None):
    best_match = None
    product: dict
    for product in price_list:
        if not product.get("attributes"):
            continue

        if ram and vcpu:
            product_memory = get_ram(product)
            product_vcpu = get_vcpu(product)

            if best_match is None:
                if (ram < get_ram(product)) and (vcpu < get_vcpu(product)):
                    best_match = product
                    continue
                continue

            # print("Best match set")
            # print(product_vcpu)
            # print(get_vcpu(best_match))
            # print()

            if (product_memory < get_ram(best_match)) \
                    and ((product_memory - ram) <= (get_ram(best_match) - ram)) \
                    and (ram <= get_ram(product)) \
                    and (vcpu <= get_vcpu(best_match)) \
                    and ((product_vcpu - vcpu) <= (get_vcpu(best_match) - vcpu)) \
                    and (vcpu <= get_vcpu(product)):
                best_match = product

        # compare against ram
        if ram and vcpu is None:
            if product["attributes"].get("aws:ec2:memory"):
                product_memory = get_ram(product)

                if best_match is None:
                    if ram <= get_ram(product):
                        best_match = product
                        continue
                    continue

                if (product_memory <= get_ram(best_match)) \
                        and ((product_memory - ram) <= (get_ram(best_match) - ram)) \
                        and (ram <= get_ram(product)):
                    best_match = product

        # comparision against vcpu
        if vcpu and (ram is None):
            if product["attributes"].get("aws:ec2:vcpu"):
                # print("comparing with vcpu")
                product_vcpu = get_vcpu(product)

                # compare against vcpu
                if best_match is None:
                    if product_vcpu < get_vcpu(product):
                        best_match = product
                        continue
                    continue

                if (vcpu < get_vcpu(best_match)) \
                        and ((product_vcpu - vcpu) < (get_vcpu(best_match) - vcpu)) \
                        and (vcpu < get_vcpu(product)):
                    best_match = product

    if best_match is not None:
        if filter_ondemand:
            best_match = compare_against_price(price_list, best_match, filter_ondemand)
        else:
            best_match = compare_against_price(price_list, best_match)
    return best_match


def one_year_std_reserved(product_list, compare_product):
    best_result = None
    id_sep = compare_product["id"].split(".")
    part_1 = id_sep[0]
    part_2 = id_sep[2]

    for product in product_list:
        if not (part_1 in product.get("id") and part_2 in product.get("id")):
            continue

        if not (product["attributes"].get("aws:offerTermLeaseLength") == "1yr"):
            continue

        if not (product["attributes"].get("aws:offerTermOfferingClass") == "standard"):
            continue

        if not (product["attributes"].get("aws:offerTermPurchaseOption") == "No Upfront"):
            continue

        best_result = product

    return best_result


def three_year_std_reserved(product_list, compare_product):
    best_result = None
    id_sep = compare_product["id"].split(".")
    part_1 = id_sep[0]
    part_2 = id_sep[2]

    print(id_sep)
    print(part_1, part_2)

    for product in product_list:
        if not (part_1 in product.get("id") and part_2 in product.get("id")):
            continue

        print("match found")
        if not (product["attributes"].get("aws:offerTermLeaseLength") == "3yr"):
            continue

        print("Second match found")
        if not (product["attributes"].get("aws:offerTermOfferingClass") == "standard"):
            continue

        if not (product["attributes"].get("aws:offerTermPurchaseOption") == "No Upfront"):
            continue

        best_result = product

    return best_result


def get_all_costing(vcpu=4, memory=5, operating_system="linux"):
    result_data = []
    all_region = get_all_region_related_ec2()

    for region in all_region:

        ondemand_path = get_all_download_path(operating_system=operating_system, region=region,
                                              pricing_strategy="onedemand")

        if not ondemand_path:
            reserved_path = get_all_download_path(operating_system=operating_system, region=region,
                                                  pricing_strategy="reserved")

            with open(reserved_path[0]) as on_dem:
                reserved = json.load(on_dem)

            reserver_result = filter_result(price_list=reserved["prices"],
                                            ram=memory,
                                            vcpu=vcpu,
                                            filter_ondemand=True)
            if reserver_result:
                # result_data.append(reserver_result)

                new_result = one_year_std_reserved(reserved["prices"], reserver_result)
                if new_result:
                    result_data.append(get_required_field(new_result))
            continue

        print(ondemand_path)
        with open(ondemand_path[0]) as on_dem:
            on_demand = json.load(on_dem)

        result = filter_result(price_list=on_demand["prices"],
                               ram=memory,
                               vcpu=vcpu)

        # return result

        # result_data.append(result)

        reserved_path = get_all_download_path(operating_system=operating_system, region=region,
                                              pricing_strategy="reserved")

        if not reserved_path and result:
            result_data.append(get_required_field(result))

        if reserved_path and not result:
            with open(reserved_path[0]) as on_dem:
                reserved = json.load(on_dem)

            reserver_result = filter_result(price_list=reserved["prices"],
                                            ram=memory,
                                            vcpu=vcpu,
                                            filter_ondemand=True)
            print("Calling reserver result")
            if reserver_result:
                result_data.append(get_required_field(reserver_result))

        if reserved_path and result:
            print(reserved_path)
            with open(reserved_path[0]) as on_dem:
                reserved = json.load(on_dem)

            if result is not None:
                print("Getting one year data")
                new_result = one_year_std_reserved(reserved["prices"], result)
                if new_result:
                    result_data.append(get_required_field(new_result))

                print(new_result)

    result_data = sorted(result_data, key=lambda v: v.get("onDemandHourlyCost"))
    return result_data


def get_required_field(product):
    result = {
        "vCpu": get_vcpu(product=product),
        "memory": get_ram(product=product),
        "instanceType": product["attributes"].get("aws:ec2:instanceType", "NA"),
        "onDemandHourlyCost": get_product_price(product=product),
        "onDemandMonthlyCost": "NA",
        "onDemandYearlyCost": "NA",
        "1yrStdReservedHourlyCost": "NA",
        "region": region_mapping_json.get(product["attributes"].get("aws:region"), "NA")
    }

    if product.get("calculatedPrice"):
        result["onDemandHourlyCost"] = product["calculatedPrice"]["onDemandRate"]["USD"]
        result["onDemandMonthlyCost"] = float(result["onDemandHourlyCost"]) * 730
        result["onDemandYearlyCost"] = float(result["onDemandMonthlyCost"]) * 365
        result["1yrStdReservedHourlyCost"] = product["calculatedPrice"]["effectiveHourlyRate"]["USD"]

    return result


if __name__ == '__main__':
    # download_information(remote_url="https://calculator.aws/pricing/1.0/ec2/region/ap-northeast-1/ondemand/linux/index.json",
    #                      file_name="ondemand.json",
    #                      download_location=os.path.dirname(__file__))

    # print(get_all_region_related_ec2())
    # download_all_region_related_info()
    # pp(get_all_download_path(operating_system="linux", region="us-west-2",
    #                          pricing_strategy="reserved"))

    import json

    with open(
            "C:\\Users\\chetan.k\\PycharmProjects\\aws\\dataPirates\\lib\\ec2\\region\\ap-east-1\\linux-onedemand.json") as on_dem:
        on_demand = json.load(on_dem)

    with open(
            "C:\\Users\\chetan.k\\PycharmProjects\\aws\\dataPirates\\lib\\ec2\\region\\ap-east-1\\linux-reserved-instance.json") as on_dem:
        reserved = json.load(on_dem)

    # print(len(on_demand["prices"]))
    # print(len(reserved["prices"]))
    # result = filter_result(on_demand["prices"])
    # pp(result)
    #

    # if result is not None:
    #     print("Getting one year data")
    #     new_result = three_year_std_reserved(reserved["prices"], result)
    #     print(new_result)

    # pp(get_all_costing())
