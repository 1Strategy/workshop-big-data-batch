## GlueResourceRole
## The Glue service will assume this role when it runs crawlers, launches jobs, and builds supporting infrastructure.
#
#  1. Create the GlueResourceRole.
#  2. Attach the AWSGlueServiceRole policy to the GlueResourceRole.
#  3. Establish a trust relationship between the GlueResourceRole and the Glue service.
#  4. Allow S3 actions on the galactic-map-tiles bucket.


resource "aws_iam_role" "GlueResourceRole" {
  name = "GlueResourceRole"

  assume_role_policy = "${data.aws_iam_policy_document.GlueResourceRole_trust_relationship.json}"
  policy = "${data.aws_iam_policy_document.GlueResourceRole_policy.json}"
}

resource "aws_iam_role_policy_attachment" "GlueResourceRole_attachment" {
    role       = "${aws_iam_role.GlueResourceRole.name}"
    policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

data "aws_iam_policy_document" "GlueResourceRole_trust_relationship" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "GlueResourceRole_policy" {
  statement {
    sid = "AllowAllS3Actions"

    actions = ["s3:*"]

    resources = [
      "arn:aws:s3:::galactic-map-tiles",
      "arn:aws:s3:::galactic-map-tiles/*"
    ]
  }
}
