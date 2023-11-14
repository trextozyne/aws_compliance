from s3 import S3
from ec2 import Ec2
from iam import IAM


def lambda_handler(event): #, context
    _s3 = S3()  # initialize class
    _s3.s3_compliance(event)
    _ec2 = Ec2()  # initialize class
    _ec2.ec2_compliance(event)
    # _iam = IAM()  # initialize class
    # _iam.iam_compliance(event)
