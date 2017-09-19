resource "aws_iam_role_policy_attachment" "attachment" {
    role       = "${aws_iam_role.GlueNotebookRole.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceNotebookRole"
}

resource "aws_iam_role" "GlueNotebookRole" {
  name = "GlueNotebookRole"

  assume_role_policy = "${data.aws_iam_policy_document.GlueNotebookRole_trust_relationship.json}"
  policy = "${data.aws_iam_policy_document.GlueNotebookRole_policy.json}"
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
