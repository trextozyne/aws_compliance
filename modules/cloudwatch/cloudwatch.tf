
data "aws_caller_identity" "current" {}

locals {
    account_id = data.aws_caller_identity.current.account_id
}

# ==========cloudwatch function ==========================================================
# ==========cloudwatch IAM & Role Policy ==========================================================
resource "aws_iam_role" "cloudwatch_logs_role" {
    name = "MyCloudWatchLogsRole"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Principal = {
                    Service = "cloudtrail.amazonaws.com"
                }
                Action = "sts:AssumeRole"
            }
        ]
    })
}

data "aws_iam_policy_document" "aws_iam_role_policy_cloudwatch" {

    version = "2012-10-17"
    statement {
        sid       = "AWSCloudTrailCreateLogStream2014110"
        effect    = "Allow"
        actions   = ["logs:CreateLogStream"]
#        resources = ["*"]
        resources = ["${aws_cloudwatch_log_group.log_group.arn}:*"]
    }
    statement {
        sid       = "AWSCloudTrailPutLogEvents20141101"
        effect    = "Allow"
        actions   = ["logs:PutLogEvents"]
#        resources = ["*"]
        resources = ["${aws_cloudwatch_log_group.log_group.arn}:*"]
    }

#        resources = [aws_cloudwatch_log_group.log_group.arn]
}

resource "aws_iam_role_policy" "cloudwatch_policy" {
    name   = "CloudTrailPolicy"
    role   = aws_iam_role.cloudwatch_logs_role.id
    policy = data.aws_iam_policy_document.aws_iam_role_policy_cloudwatch.json
}
# ========== cloudwatch IAM & Role Policy ==========================================================

#================= ec2 cpu, memory, and container cloudwatch alarm setup ========================

#resource "aws_cloudwatch_metric_alarm" "k8s01_cpu_used_critical" {
#
#    alarm_name = "CRITICAL CPU Usage Exceeds Threshold"
#    alarm_description = "CRITICAL alert for CPU Exceeds Threshold"
#    actions_enabled = true
#
##    alarm_actions = [aws_sns_topic.user_updates.arn]
##    ok_actions = [aws_sns_topic.user_updates.arn]
#    insufficient_data_actions = []
#
#    comparison_operator = "GreaterThanThreshold"
#    evaluation_periods = "2"
#    threshold = var.alert_critical_threshold
#    unit = "Count"
#
#    metric_query {
#        id = "m1"
#
#        metric {
#            metric_name = "cpuUsagePercentage"
#            namespace = "Insights.Container/nodes"
#            period = "120"
#            stat = "Average"
#            unit = "Count"
#
#            dimensions = var.dimensions
#        }
#    }
#}

#================= ec2 cpu, memory, and container cloudwatch alarm setup ========================

# Create a CloudWatch Logs group to receive the CloudTrail logs
resource "aws_cloudwatch_log_group" "log_group" {
    name = "/aws/lambda/${var.aws_lambda_function_name}"
    retention_in_days = 1
}

# Create the CloudWatch Event Rule to trigger the resource
resource "aws_cloudwatch_event_rule" "cloudwatch_event" {
    name        = "lambda-cloudwatch-event-rule"
    description = "Trigger Lambda function on resource creation or modification"

#    schedule_expression = "rate(1 minute)"
    event_pattern = jsonencode({
        "source": ["aws.cloudwatch", "aws.s3", "aws.iam", "aws.ec2"],
        "detail-type": ["AWS API Call via CloudTrail", "CloudWatch Alarm State Change"],
        "detail": {
            "eventSource": ["s3.amazonaws.com", "iam.amazonaws.com", "ec2.amazonaws.com"],
            "eventName": ["CreateBucket", "RunInstances", "CreateRole"]
        }
    })

#    schedule_expression = "rate(1 minute)"
#    event_pattern = jsonencode({
#        "source": ["aws.cloudwatch", "aws.s3", "aws.iam", "aws.ec2"],
#        "detail-type": ["AWS API Call via CloudTrail", "CloudWatch Alarm State Change"],
#        "detail": {
#            "eventSource": ["s3.amazonaws.com", "iam.amazonaws.com", "ec2.amazonaws.com"],
#            "eventName": ["CreateBucket", "RunInstances"],
#            "alarmName": ["${aws_cloudwatch_metric_alarm.ec2_cpu_used_critical.alarm_name}",
#                "${aws_cloudwatch_metric_alarm.ec2_memory_used_critical.alarm_name},
#                "${aws_cloudwatch_metric_alarm.ec2_memory_used_critical.alarm_name}"],
#            "state": ["ALARM"]
#        }
#    })
}


# Add the SNS topic as a target for the CloudWatch Event Rule
#resource "aws_cloudwatch_event_target" "sns_topic" {
#    rule      = aws_cloudwatch_event_rule.cloudwatch_event.name
#    target_id = var.aws_sns_topic_name
#    arn       = var.aws_sns_topic_arn
#}

# Add the Lambda function as a target for the CloudWatch Event Rule
resource "aws_cloudwatch_event_target" "lambda_function" {
    rule      = aws_cloudwatch_event_rule.cloudwatch_event.name
    target_id = var.aws_lambda_function_name
    arn       = var.aws_lambda_function_arn
}

# Add the CloudTrail log group as a target for the CloudWatch Event Rule
#resource "aws_cloudwatch_event_target" "event_target" {
#    rule      = aws_cloudwatch_event_rule.cloudwatch_event.name
#    target_id = aws_cloudwatch_log_group.log_group.name
#    arn       = aws_cloudwatch_log_group.log_group.arn
#}

# ==========cloudwatch function ==========================================================

# ==========cloudtrail function ==========================================================
# ========== Cloudtrail IAM & Role Policy ==========================================================
resource "aws_iam_role" "cloudtrail_logs_role" {
    name = "CloudtrailLogsRole"

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = "sts:AssumeRole"
                Effect = "Allow"
                Principal = {
                    Service = "cloudtrail.amazonaws.com"
                }
            }
        ]
    })
}

# ========== Cloudtrail IAM & Role Policy ==========================================================

# Create the CloudTrail to monitor resource events
resource "aws_cloudtrail" "cloud_trail_compliance" {
    name                          = "compliance-cloudtrail"
    s3_bucket_name                = var.s3_bucket_name
    s3_key_prefix                 = var.s3_key_prefix
    #  sns_topic_name                = "compliance-topic"
    include_global_service_events = true
    cloud_watch_logs_group_arn      = "${aws_cloudwatch_log_group.log_group.arn}:*"
    cloud_watch_logs_role_arn      = aws_iam_role.cloudwatch_logs_role.arn

    event_selector {
        read_write_type           = "All"
        include_management_events = true

#        data_resource {
#            type   = "AWS::S3::Object"
#            values = ["arn:aws:s3"]
#        }

#        data_resource {
#            type   = "AWS::Lambda::Function"
#            values = ["arn:aws:lambda"]
#        }
    }

    depends_on = [var.aws_s3_bucket]
}
# ==========cloudtrail function ==========================================================

