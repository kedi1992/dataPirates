import os
import json

print(os.path.dirname(__file__))

class PriceComparision:
    def __init__(self):
        try:
            self.prise_list = []
        except Exception as e:
            print("Exception in PriceComparision class : {}", e)


    def getCost(self, storageClass="Standard", storageCapacityInGB="600000"):
        try:
            path_of_S3_data = os.path.join(os.path.dirname(__file__), "S3_data")
            for dirpath, dirnames, files in os.walk(os.path.join(os.path.dirname(__file__), "S3_data"), topdown=False):
                # Traversing for each region json
                for file in files:
                    print("-------------------------------------------------------------------------",file)
                    temp_final_cost_json = {}
                    total_cost = 0
                    file_location = os.path.join(dirpath, file)
                    print("]]]]]]]]]",file_location)
                    with open(file_location, "r+") as fd:
                        temp_file_content = json.loads(fd.read())
                    fd.close()
                    print(type(temp_file_content))
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


                                    print("++++",total_cost)
                                    # temp_cost_json_list["region"] =



                                    print("?????", temp_cost_json_list)





                    exit(1)

        except Exception as e:
            print("Exception ocuured in getCost method : {}", format(e))
            return False


obj = PriceComparision()
obj.getCost()