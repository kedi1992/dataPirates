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

region_path = os.path.join(os.path.dirname(__file__), "region")
os.makedirs(region_path, exist_ok=True)


def get_all_region_related_ec2():
    url = "https://calculator.aws/pricing/1.0/ec2/manifest.json"
    # response = requests.get(url, verify=False)
    # result = response.json()["ec2"]
    # print(result)
    result = ['ap-south-1', 'eu-north-1']
    return result


def download_information(remote_url, file_name, download_location):
    print(remote_url)
    print(file_name)
    print(download_location)
    response = requests.get(remote_url, verify=False)
    print(response.status_code)
    os.makedirs(download_location, exist_ok=True)
    download_file_location = os.path.join(download_location, file_name)

    with open(download_file_location, mode="w") as fw:
        json.dump(response.json(), fp=fw, indent=4)


def download_all_region_related_info():
    all_region = get_all_region_related_ec2()
    for region in all_region:
        ondemand_url = "https://calculator.aws/pricing/1.0/" \
                       "ec2/region/{region}/{category}/{os}/index.json".format(region=region,
                                                                               category="ondemand",
                                                                               os='linux')
        reserved_url = "https://calculator.aws/pricing/1.0/" \
                       "ec2/region/{region}/{category}/{os}/index.json".format(region=region,
                                                                               category="reserved-instance",
                                                                               os='linux')

        download_location = os.path.join(region_path, region)

        download_information(remote_url=ondemand_url,
                             file_name="onedemand.json",
                             download_location=download_location)

        download_information(remote_url=reserved_url,
                             file_name="reserved-instance.json",
                             download_location=download_location)


if __name__ == '__main__':
    # download_information(remote_url="https://calculator.aws/pricing/1.0/ec2/region/ap-northeast-1/ondemand/linux/index.json",
    #                      file_name="ondemand.json",
    #                      download_location=os.path.dirname(__file__))

    print(get_all_region_related_ec2())
    download_all_region_related_info()