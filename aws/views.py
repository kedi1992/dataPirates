from django.shortcuts import render
import traceback
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK
import requests
from lib.ec2.price_check import get_all_costing


# Create your views here.


def index(request):
    return render(request, 'aws/index.html', context={})


def cart_info(request):
    return render(request, 'aws/cart_info.html', context={})


def ec2(request):
    return render(request, 'aws/vm.html', context={})


def category(request):
    category_name = str(request.path).split("/")[-1]
    print("category_name : ", category_name)
    service_name = request.GET.get('type')
    return render(request, 'aws/{page_name}.html'.format(page_name=category_name), context={"serviceName": service_name})


def result(request):
    key = request.GET.get("key", None)
    service_type = request.GET.get("type", None)
    category_name = str(request.path).split("/")[-1].replace("type=", "")
    info_list = []
    tmp = str(request.path).split("/")[-2].replace("type=", "")
    if "vm" == tmp:
        # info_list.append(request.GET.get("type", None))
        info_list.append("OS : " + request.GET.get("os_type", ""))

        data = get_all_costing(vcpu=10, operating_system="linux", memory=float(10.0))
        print(">>>>>>>>>>>>>>>>>>>>>>>> : ", len(data))

        # info_list.append("CPU : " + request.GET.get("cpu", ""))
        # info_list.append("RAM : " + request.GET.get("ram", ""))
    elif "storage" == tmp:
        info_list.append(request.GET.get("key", ""))
    print("service_type :", service_type)
    print("category_name : ", category_name)
    print("key : ", key)
    print("tmp : ", tmp)
    print("info : ", info_list)
    return render(request, 'aws/result.html', context={"type": service_type,
                                                       "key": key, "category": category_name,
                                                       "info": info_list})


class GetAllOfferCodes(APIView):
    def get(self, request):
        try:
            all_offerCodes_url = "https://pricing.amazonaws.com/offers/v1.0/aws/index.json"
            response = requests.get(url=all_offerCodes_url)
            if response.status_code == 200:
                all_offer_codes = response.json()
                return Response(all_offer_codes, status=200)
            else:
                return Response("Something went wrong", status=400)
        except Exception as e:
            print("Exception in getRegionIndex view : {}".format(traceback.print_exc(e)))
            return False


class GetServices(APIView):
    def get(self, request):
        try:
            services_list = ["Amazon S3", "Amazon EC2 [Elastic Compute Cloud]", "AWS Lambda", "Amazon Glacier",
                             "Amazon SNS", "Amazon CloudFront", "Amazon EBS [Elastic Block Store]", "Amazon Kinesis",
                             "Amazon VPC", "Amazon SQS", "Amazon Elastic Beanstalk", "DynamoDB",
                             "Amazon RDS [Relational Database Service]", "Amazon ElastiCache", "Amazon Redshift"]

            return Response(services_list, status=200)
        except Exception as e:
            print("Exception in getServices view : {}".format(traceback.print_exc(e)))
            return False


class GetEc2Instance(APIView):
    """Return the list of best instance from all region
    HTTP Method      :               POST
    URL              :              /api/common/systemUpgrade
    Request Body     :       {

                                    "os"  : "linux/windows",
                                    "vCpu"  : "1 to 128",
                                    "memory" : "1 to 500 ",
                            }
    Response         :      {

                            }
    Error Codes      :              200(OK)
                                    400(BadRequest)
    """

    def post(self, request):
        try:
            request_body: dict = request.data
            print(request_body)
            operating_system = request_body.get("os", None)
            vcpu = request_body.get("vCpu", None)
            memory = request_body.get("memory", None)

            result = get_all_costing(vcpu=int(vcpu), memory=float(memory), operating_system=operating_system)
            # result = get_all_costing(vcpu=4, memory=5, operating_system="linux")

            return Response(result, status=HTTP_200_OK)

        except Exception as e:
            print(e)
            raise
