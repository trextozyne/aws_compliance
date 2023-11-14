variable "s3_bucket_name" {
  description = "Name to be used for S3 Bucket to use for cloud trail logs"
  type    = string
  default = ""
}

variable "s3_prefix" {
  description = "The s3 prefix to use use bucket for cloudtrail logs"
  default = ""
}

variable "cloudtrail_arn" {
  description = "The cloudtrail arn"
  default = ""
}

variable "aws_caller_identity_accountid" {
  description = "Get the account id from Aws caller identity current value"
  type    = string
  default = ""
}
