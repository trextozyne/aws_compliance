output "aws_s3_bucket" {
  value = try(aws_s3_bucket.compliance_bucket, "")
}

output "aws_s3_bucket_arn" {
  value = try(aws_s3_bucket.compliance_bucket.arn, "")
}

output "aws_s3_bucket_name" {
  value = try(aws_s3_bucket.compliance_bucket.bucket, "")
}
