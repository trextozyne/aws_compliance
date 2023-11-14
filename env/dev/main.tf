module "Cloudwatch" {
  source                   = "../../modules/cloudwatch"
  aws_lambda_function_arn  = module.Lambda.aws_lambda_function_arn
  aws_lambda_function_name = module.Lambda.aws_lambda_function_name
  aws_s3_bucket            = module.S3.aws_s3_bucket
  aws_sns_topic_arn        = module.SNS.sns_topic_arn
  aws_sns_topic_name       = module.SNS.sns_topic_name
  s3_bucket_name           = module.S3.aws_s3_bucket_name
  s3_key_prefix            = var.s3_prefix
  aws_sns_topic_id         = module.SNS.sns_topic_id
}

module "Lambda" {
  source                    = "../../modules/lambda"
  aws_caller_identity_accountid                = module.Cloudwatch.account_id
  filename                  = var.lambda_filename
  folder_name               = var.folder_name
  function_name             = var.function_name
  lambda_filename           = var.lambda_filename
  lambda_iam_role_name      = var.lambda_iam_role_name
  runtime                   = var.runtime
  cloudwatch_event_rule_arn = module.Cloudwatch.cloudwatch_event_rule_arn
  sns_call_lambda_arn       = module.SNS.sns_topic_arn
}

module "S3" {
  source                        = "../../modules/s3"
  s3_bucket_name                = "${var.s3_bucket_name}-${module.Cloudwatch.account_id}"
  aws_caller_identity_accountid = module.Cloudwatch.account_id
  s3_prefix                     = var.s3_prefix
  cloudtrail_arn                = module.Cloudwatch.cloudtrail_arn
}

module "SNS" {
  source              = "../../modules/sns"
  sns_topic_email     = var.sns_topic_email
  sns_topic_name      = var.sns_topic_name
  lambda_function_arn = module.Lambda.aws_lambda_function_arn
}

module "vpc" {
  source                   = "../../../AWS_IAC/modules/vpc"
  vpc_id                   = module.vpc.vpc_ids
  env                      = var.env
  project                  = var.project
  main_vpc_cidr            = var.main_vpc_cidr
  public_subnets           = var.public_subnets
  private_subnets          = var.private_subnets
  vpc_cidr                 = var.vpc_cidr
  subnet_cidr_bits         = var.subnet_cidr_bits
  availability_zones_count = var.availability_zones_count
}


#{
#"Version": "2012-10-17",
#"Statement": [
#{
#"Sid": "AWSCloudTrailAclCheck20150319",
#"Effect": "Allow",
#"Principal": {"Service": "cloudtrail.amazonaws.com"},
#"Action": "s3:GetBucketAcl",
#"Resource": "arn:aws:s3:::${ct_bucket_name}"
#},
#{
#"Sid": "AWSCloudTrailWrite20150319",
#"Effect": "Allow",
#"Principal": {"Service": "cloudtrail.amazonaws.com"},
#"Action": "s3:PutObject",
#"Resource": "arn:aws:s3:::${ct_bucket_name}/**${prefix}**/AWSLogs/myAccountID/*",
#"Condition": {"StringEquals": {"s3:x-amz-acl": "bucket-owner-full-control"}}
#}
#]
#}