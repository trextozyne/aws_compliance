variable "s3_bucket_name" {
  description = "Name to be used for S3 Bucket to use for cloud trail logs"
  type        = string
  default     = "compliance-bucket-the-rexy-project"
}

variable "s3_prefix" {
  description = "The s3 prefix to use use bucket for cloudtrail logs"
  default     = "cloudtrail-logs-the-rexy-project"
}

variable "sns_topic_name" {
  description = "Name to be used for SnS topic"
  type        = string
  default     = "call-lambdas-topic-the-rexy-project"
}

variable "sns_topic_email" {
  description = "Email to be used with SnS topic"
  type        = string
  default     = "daleks1987@gmail.com"
}

variable "function_name" {
  description = "The name the file or folder would be call on AWS lambda"
  default     = "compliance-lambda-function"
}
variable "runtime" {
  description = "The runtime environment the code is run i.e python3.8"
  default     = "python3.8"
}

variable "lambda_iam_role_name" {
  description = "The name provided for the lambda iam role"
  default     = "compliance-lambda-role"
}

variable "folder_name" {
  description = "The folder of the written code resides"
  default     = "Compliance_lambda"
}

variable "lambda_filename" {
  description = "The name of the written lambda code"
  default     = "service_compliance.zip"
}

// =========================================VPC=================================
variable "region" {
  default = ["us-east-2"]
}

variable "main_vpc_cidr" {
  default = "192.168.0.0/16"
}

variable "public_subnets" {
  default = "192.168.0.0/24"
}

variable "private_subnets" {
  default = "192.168.1.0/24"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC. Default value is a valid CIDR, but not acceptable by AWS and should be overridden"
  type        = string
  default     = "192.168.0.0/16"
}

variable "subnet_cidr_bits" {
  description = "The number of subnet bits for the CIDR. For example, specifying a value 8 for this parameter will create a CIDR with a mask of /24."
  type        = number
  default     = 8
}

variable "availability_zones_count" {
  description = "The number of AZs."
  type        = number
  default     = 2
}

variable "project" {
  description = "Name to be used on all the resources as identifier. e.g. Project name, Application name"
  # description = "Name of the project deployment."
  type    = string
  default = "rex-useast2-dev"
}

variable "env" {
  description = "ENV NAME"
  type        = string
  default     = "dev"
}

variable "ami_id" {
  default = "ami-0149b2da6ceec4bb0"
}

variable "instance_type" {
  default = "t2.small"
}

variable "associate_public_ip_ec2" {
  default = "true"
}