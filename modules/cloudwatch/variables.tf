variable "s3_bucket_name" {
  description = "Name to be used for S3 backend Bucket"
  type    = string
  default = ""
}

variable "aws_s3_bucket" {
  description = "s3 buckets used for cloud trail logs"
  default = ""
}

variable "s3_key_prefix" {
  default = "cloudtrail-logs"
}

variable "aws_sns_topic_arn" {
  description = "The sns function arn used for cloudwatch event target"
  default = ""
}
variable "aws_sns_topic_id" {
  description = "The sns function id used as a target"
  default = ""
}
variable "aws_sns_topic_name" {
  description = "The sns function name used as a target"
  default = ""
}
variable "aws_lambda_function_arn" {
  description = "The lambda function arn used as a target"
  default = ""
}
variable "aws_lambda_function_name" {
  description = "The lambda function id used as a target"
  default = ""
}
