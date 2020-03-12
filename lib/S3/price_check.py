import json
import requests
import os

class GetCostEstimateJSON():
    def __init__(self):
        try:

            self.temp_url_list = []
        except Exception as e:
            print("Exception in initializing class : {}", e)

    def getAllServiceURLs(self, serviceName = "AmazonS3"):

        service_name = serviceName
        if service_name:
            all_offerCodes_url = "https://pricing.amazonaws.com/offers/v1.0/aws/index.json"
            response = requests.get(url=all_offerCodes_url)

            if response.status_code == 200:
                all_offer_codes = response.json()

                for offer_code in all_offer_codes.get("offers").keys():
                    if service_name == offer_code:
                        '''
                        offer_code = "AmazonS3" : {
                                                  "offerCode" : "AmazonS3",
                                                  "versionIndexUrl" : "/offers/v1.0/aws/AmazonS3/index.json",
                                                  "currentVersionUrl" : "/offers/v1.0/aws/AmazonS3/current/index.json",
                                                  "currentRegionIndexUrl" : "/offers/v1.0/aws/AmazonS3/current/region_index.json"
                                                }
                        '''
                        return all_offer_codes["offers"][offer_code]

    def getRegionIndexURLs(self, serviceName="AmazonS3", region_list="all"):

        # temp_url_list will contain all the data urls for requested services
        temp_url_list = []
        all_service_urls = self.getAllServiceURLs(serviceName)

        currentRegionURLs = all_service_urls["currentRegionIndexUrl"]
        all_region_url = "https://pricing.amazonaws.com"+currentRegionURLs

        #getting data urls for all regions for requested service
        regions_response = requests.get(url=all_region_url)

        if not regions_response.status_code == 200:
            print("Unable to find urls for regions")
            return False
        regions_response_json = regions_response.json()

        if region_list == "all" or len(region_list) == 0:
            for region_value in regions_response_json["regions"].values():
                print(region_value)
                temp_url_list.append(region_value)
        else:
            for region in regions_response_json["regions"].keys():
                if region in region_list:
                    temp = {}
                    temp["regionCode"] = [regions_response_json["regions"][region]["regionCode"]]
                    temp["currentVersionUrl"] = [regions_response_json["regions"][region]["currentVersionUrl"]]
                    temp_url_list.append(temp)

        return temp_url_list

    def download_information(self, remote_url, file_name, download_location):
        base_url = "https://pricing.amazonaws.com"
        print(remote_url)
        print(file_name)
        print(download_location)
        response = requests.get(base_url + remote_url, verify=False)
        print(response.status_code)
        try:
            os.makedirs(download_location, exist_ok=True)
            download_file_location = os.path.join(download_location, file_name)

            with open(download_file_location, mode="w") as fw:
                json.dump(response.json(), fp=fw, indent=4)
        except Exception as e:
            print("Related region no information found ")
            print(remote_url)

    def getCostJSON(self, serviceName = "AmazonS3", region_list="all"):

        allCostURLs_list = self.getRegionIndexURLs(serviceName, region_list)

        for element in allCostURLs_list:
            self.download_information(element["currentVersionUrl"], element["regionCode"], os.path.join(os.path.dirname(__file__), "S3_data"))

        return True

obj = GetCostEstimateJSON()
print(obj.getCostJSON())