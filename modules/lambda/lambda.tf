# ==========Lambda function ==========================================================

resource "aws_lambda_permission" "allow_cloudwatch_to_invoke_lambda" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.resource_compliance_function.function_name
  principal     = "events.amazonaws.com"
#  source_arn    = var.sns_call_lambda_arn
  source_arn    = var.cloudwatch_event_rule_arn
}

# Zip the lambda code
data "archive_file" "lambda_function_zip" {
  type        = "zip"

  source_dir = "${path.module}/../../${var.folder_name}"
  output_path = "${path.module}/../../env/dev/${var.lambda_filename}"
#  output_path = "${path.module}/../../${var.lambda_filename}"
}

# Create the Lambda function

resource "aws_lambda_function" "resource_compliance_function" {
  filename         = var.lambda_filename
  function_name    = var.function_name
  handler          = "lambda_function.lambda_handler"
  runtime          = var.runtime
  timeout          = 60
  role             = aws_iam_role.lambda.arn
  source_code_hash = data.archive_file.lambda_function_zip.output_base64sha256
}

# Create the IAM role for the Lambda function
resource "aws_iam_role" "lambda" {
  name = var.lambda_iam_role_name

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}


# Create the IAM policy for the Lambda function
resource "aws_iam_policy" "lambda" {
  name        = "compliance-lambda-policy"
  policy      = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        "Action": [
          "s3:*"
        ]
        Resource = "arn:aws:s3:::*"
      },
      {
        Effect = "Allow"
        Action = [
          "cloudtrail:LookupEvents"
        ]
        Resource = "*"
      },
      {
        "Sid": "EC2DescribeInstances",
        "Effect": "Allow",
        "Action": [
          "ec2:DescribeInstances",
          "autoscaling:DescribeAutoScalingGroups",
          "ec2:RunInstances",
          "autoscaling:CreateLaunchConfiguration",
          "autoscaling:CreateAutoScalingGroup",
          "autoscaling:AttachInstances",
          "autoscaling:UpdateAutoScalingGroup",
          "ec2:DescribeVolumes",
          "ec2:DescribeSnapshots",
          "ec2:DeleteSnapshot"
        ],
        "Resource": "*"
#        "Resource": "arn:aws:autoscaling:us-east-2:${var.aws_caller_identity_accountid}:launchConfiguration:*"
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_function" {
  policy_arn = aws_iam_policy.lambda.arn
  role       = aws_iam_role.lambda.name
}
# ==========Lambda function ==========================================================

