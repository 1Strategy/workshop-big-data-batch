## GlueNotebookRole
## Development endpoints and Zeppelin notebook servers will be launched with this role when created by the Glue service.
#
#  1. Create the GlueNotebookRole.
#  2. Attach the AWSGlueNotebookRole policy to the GlueNotebookRole.
#  3. Establish a trust relationship between the GlueNotebookRole and the EC2 service.
#  4. Allow S3 actions on the navigation-notebooks bucket.

resource "aws_iam_role" "GlueNotebookRole" {
  name = "GlueNotebookRole"

  assume_role_policy = "${data.aws_iam_policy_document.GlueNotebookRole_trust_relationship.json}"
  policy = "${data.aws_iam_policy_document.GlueNotebookRole_policy.json}"
}

resource "aws_iam_role_policy_attachment" "attachment" {
    role       = "${aws_iam_role.GlueNotebookRole.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceNotebookRole"
}

data "aws_iam_policy_document" "GlueNotebookRole_trust_relationship" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "GlueNotebookRole_policy" {
  statement {
    sid = "AllowAllS3Actions"
    
    actions = ["s3:*"]

    resources = [
      "arn:aws:s3:::navigation-notebooks",
      "arn:aws:s3:::navigation-notebooks/*"
    ]
  }
}
