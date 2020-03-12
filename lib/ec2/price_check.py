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
from pprint import pprint as pp
import glob

region_path = os.path.join(os.path.dirname(__file__), "region")
os.makedirs(region_path, exist_ok=True)


# glob.glob()

def get_all_region_related_ec2():
    url = "https://calculator.aws/pricing/1.0/ec2/manifest.json"
    response = requests.get(url, verify=False)
    result = response.json()["ec2"]
    # print(result)
    # result = ['ap-south-1', 'eu-north-1']
    return result


def get_all_download_path():
    result = []
    for dirpath, dirnames, files in os.walk(os.path.join(os.path.dirname(__file__), "region"), topdown=False):
        for file in files:
            file_location = os.path.join(dirpath, file)
            if os.path.isfile(file_location) and ".json" in file_location:
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

        with open(download_file_location, mode="w") as fw:
            json.dump(response.json(), fp=fw, indent=4)
    except Exception as e:
        print("Related region no information found ")
        print(remote_url)


def download_all_region_related_info(operating_system='linux'):
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
    # print(type(product))

    if product["attributes"].get("aws:ec2:memory"):
        product_memory = float(product["attributes"]["aws:ec2:memory"].replace("GiB", "").strip())
        return product_memory
    # print("It don't have aws:ec2:memory")
    return 0


def get_vcpu(product):
    if product["attributes"].get("aws:ec2:vcpu"):
        product_vcpu = float(product["attributes"]["aws:ec2:vcpu"].strip())
        print(product_vcpu)
        return product_vcpu
    # print("It don't have aws:ec2:memory")

    return 0


def get_product_price(product):
    if product.get("price") or product["price"].get("USD"):
        return float(product["price"].get("USD"))
    return 0


def compare_against_price(price_list, compair_product):
    best_result = compair_product
    for product in price_list:
        if not get_product_price(product) <= get_product_price(best_result):
            continue

        if not get_ram(product) >= get_ram(best_result):
            continue

        best_result = product

    return best_result


def filter_result(price_list, ram=9, vcpu=None):
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

            print("Best match set")

            if (product_memory < get_ram(best_match)) \
                    and ((product_memory - ram) <= (get_ram(best_match) - ram)) \
                    and (ram <= get_ram(product)) \
                    and (vcpu <= get_vcpu(best_match)) \
                    and ((product_vcpu - vcpu) <= (get_vcpu(best_match) - vcpu)) \
                    and (vcpu <= get_vcpu(product)):
                best_match = product

        # compare against ram
        if ram:
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
                print("comparing with vcpu")
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
            best_match = compare_against_price(price_list, best_match)

    return best_match


if __name__ == '__main__':
    # download_information(remote_url="https://calculator.aws/pricing/1.0/ec2/region/ap-northeast-1/ondemand/linux/index.json",
    #                      file_name="ondemand.json",
    #                      download_location=os.path.dirname(__file__))

    # print(get_all_region_related_ec2())
    # download_all_region_related_info()
    # pp(get_all_download_path())

    import json

    with open(
            "C:\\Users\\chetan.k\\PycharmProjects\\aws\\dataPirates\\lib\\ec2\\region\\ap-east-1\\linux-onedemand.json") as on_dem:
        on_demand = json.load(on_dem)

    with open(
            "C:\\Users\\chetan.k\\PycharmProjects\\aws\\dataPirates\\lib\\ec2\\region\\ap-east-1\\linux-reserved-instance.json") as on_dem:
        reserved = json.load(on_dem)

    print(len(on_demand["prices"]))
    print(len(reserved["prices"]))
    pp(filter_result(on_demand["prices"]))
