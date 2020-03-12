import os
import json
import urllib3
urllib3.disable_warnings()

region_path = os.path.join(os.path.dirname(__file__), "region")

class PriceComparision:
    def __init__(self):
        try:
            self.prise_list = []
        except Exception as e:
            print("Exception in PriceComparision class : {}", e)

    def getRegionName(self, region_code):
        try:
            region_mapping = os.path.join(os.path.dirname(os.path.dirname(__file__)), "regionMapping.json")

            with open(region_mapping) as region_mapping_dp:
                region_mapping_actual: dict = json.load(region_mapping_dp)

            region_mapping_json = {v: k for k, v in region_mapping_actual.items()}

            for k, v in region_mapping_json.items():
                if k == region_code:
                    return v

            return None
        except Exception as e:
            print("Exception in getRegionName method : {}".format(e))
            return False

    def getCost(self, storageClass, storageCapacityInGB):
        try:

            for dirpath, dirnames, files in os.walk(os.path.join(os.path.dirname(__file__), "S3_data"), topdown=False):
                # Traversing for each region json
                for file in files:

                    temp_final_cost_json = {}
                    total_cost = 0
                    file_location = os.path.join(dirpath, file)

                    with open(file_location, "r+") as fd:
                        temp_file_content = json.loads(fd.read())
                    fd.close()

                    for a in temp_file_content["products"].keys():
                        storageType = temp_file_content["products"][a].get("attributes", None).get("volumeType", None)

                        if storageType:
                            if storageType == storageClass:
                                print("***************************************************")
                                print("StorageType :", storageType)
                                temp_cost_json_list = []
                                for k, v in temp_file_content["terms"]["OnDemand"][a].items():
                                    for v1 in v.get("priceDimensions").values():
                                        temp_json = {}
                                        temp_json["unit"] = v1.get("unit")
                                        temp_json["pricePerUnit"] = v1.get("pricePerUnit")
                                        temp_json["description"] = v1.get("description")
                                        temp_cost_json_list.append(temp_json)

                                # When there are multiple fairs for each category
                                if len(temp_cost_json_list) == 3:
                                    storageSizeinTB = int(storageCapacityInGB)/1000

                                    if not storageSizeinTB > 50:   # Value less then 50TB
                                        for ele in temp_cost_json_list:
                                            for keys, values in ele.items():
                                                if "first 50 TB" in values:
                                                    total_cost = total_cost + float(storageSizeinTB) * float(1024) * float(ele["pricePerUnit"]["USD"])
                                    elif not storageSizeinTB > 500:  # Value less then 500TB
                                        first_sort = storageSizeinTB - 50
                                        for ele in temp_cost_json_list:
                                            for keys, values in ele.items():
                                                if "first 50 TB" in values:
                                                    total_cost =total_cost + float(50) * float(1024) * float(ele["pricePerUnit"]["USD"])
                                                if "next 450 TB" in values:
                                                    total_cost = total_cost + float(first_sort) * float(1024) * float(ele["pricePerUnit"]["USD"])
                                    elif storageSizeinTB > 500:    # Value is greater then 500TB
                                        first_sort = storageSizeinTB - 500
                                        for ele in temp_cost_json_list:
                                            for keys, values in ele.items():
                                                if "first 50 TB" in values:
                                                    total_cost =total_cost + float(50) * float(1024) * float(ele["pricePerUnit"]["USD"])
                                                if "next 450 TB" in values:
                                                    total_cost = total_cost + float(450) * float(1024) * float(ele["pricePerUnit"]["USD"])
                                                if "over 500 TB" in values:
                                                    total_cost = total_cost + float(first_sort) * float(1024) * float(
                                                        ele["pricePerUnit"]["USD"])

                                    temp_final_cost_json["region"] = self.getRegionName(region_code=file)
                                    temp_final_cost_json["storageClass"] = storageType
                                    temp_final_cost_json["totalCost"] = total_cost

                                    self.prise_list.append(temp_final_cost_json)

                                # When there is only one fair for all categories
                                if len(temp_cost_json_list) == 1:
                                    storageSizeinTB = int(storageCapacityInGB) / 1000

                                    for ele in temp_cost_json_list:
                                        total_cost = total_cost + float(storageSizeinTB) * float(1024) * float(
                                            ele["pricePerUnit"]["USD"])

                                    temp_final_cost_json["region"] = self.getRegionName(region_code=file)
                                    temp_final_cost_json["storageClass"] = storageType
                                    temp_final_cost_json["totalCost"] = total_cost

                                    self.prise_list.append(temp_final_cost_json)
                result_data = sorted(self.prise_list, key=lambda v: v.get("totalCost"))
                return result_data
        except Exception as e:
            print("Exception ocuured in getCost method : {}", format(e))
            return False


# obj = PriceComparision()
# print(obj.getCost())
