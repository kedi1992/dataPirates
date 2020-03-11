from django.shortcuts import render
import traceback
from rest_framework.response import Response
from rest_framework.views import APIView
# Create your views here.


def index(request):
    return render(request, 'aws/index.html', context={})

class GetServices(APIView):
    def get(self, request):
        try:
            services_list = ["Amazon S3", "Amazon EC2 [Elastic Compute Cloud]", "AWS Lambda", "Amazon Glacier", "Amazon SNS", "Amazon CloudFront", "Amazon EBS [Elastic Block Store]", "Amazon Kinesis", "Amazon VPC", "Amazon SQS", " Amazon Elastic Beanstalk", "DynamoDB", "Amazon RDS [Relational Database Service]", "Amazon ElastiCache", "Amazon Redshift"]

            return Response(services_list, status=200)
        except Exception as e:
            print("Exception in getServices view : {}".format(traceback.print_exc(e)))
            return False