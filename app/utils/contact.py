import boto3


def contact_us(name: str, email: str, message: str):
    sns_client = boto3.client("sns", region_name="ap-southeast-2")

    message = f"Dear Admin, \n {name.upper()} is wanting to get in touch with you. \n{message}\nreply-to: {email}"
    subject = f"[CONTACT] by {name.upper()}"
    topic_arn = "<<TODO: Replace with ARN of your SNS TOPIC>>"

    sns_client.publish(TopicArn=topic_arn, Message=message, Subject=subject)
