from django.shortcuts import render
import traceback
from rest_framework.response import Response
from rest_framework.views import APIView
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


class GetServices(APIView):
    def get(self, request):
        try:
            services_list = ["Amazon S3", "Amazon EC2 [Elastic Compute Cloud]", "AWS Lambda", "Amazon Glacier", "Amazon SNS", "Amazon CloudFront", "Amazon EBS [Elastic Block Store]", "Amazon Kinesis", "Amazon VPC", "Amazon SQS", " Amazon Elastic Beanstalk", "DynamoDB", "Amazon RDS [Relational Database Service]", "Amazon ElastiCache", "Amazon Redshift"]

            return Response(services_list, status=200)
        except Exception as e:
            print("Exception in getServices view : {}".format(traceback.print_exc(e)))
            return False