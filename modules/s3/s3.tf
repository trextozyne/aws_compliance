# ==========S3 function ==========================================================
resource "aws_s3_bucket" "compliance_bucket" {
  bucket        = var.s3_bucket_name
  force_destroy = true
}

resource "aws_s3_bucket_policy" "compliance_bucket_policy" {
  bucket = aws_s3_bucket.compliance_bucket.id

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Sid": "AWSCloudTrailAclCheck",
        "Effect": "Allow",
        "Principal": {
          "Service": "cloudtrail.amazonaws.com"
        },
        "Action": "s3:GetBucketAcl",
        "Resource": "arn:aws:s3:::${aws_s3_bucket.compliance_bucket.bucket}",
#        "Condition": {
#          "StringEquals" : {
#            "aws:SourceArn" : var.cloudtrail_arn
#          }
#        }
      },
      {
        "Sid": "AWSCloudTrailWrite",
        "Effect": "Allow",
        "Principal": {
          "Service": "cloudtrail.amazonaws.com"
        },
        "Action": "s3:PutObject",
        "Resource": "arn:aws:s3:::${aws_s3_bucket.compliance_bucket.bucket}/**${var.s3_prefix}**/AWSLogs/${var.aws_caller_identity_accountid}/*",
        "Condition": {
          "StringEquals": {
            "s3:x-amz-acl": "bucket-owner-full-control",
#            "aws:SourceArn": var.cloudtrail_arn
          }
        }
      }
    ]
  })
}
# ==========S3 function ==========================================================
