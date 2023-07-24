import datetime

import boto3


def save_to_ip_list(ip_address: str, browser: str):
    dynamodb = boto3.resource("dynamodb", region_name="ap-southeast-2")
    table = dynamodb.Table("<<TODO: Replace with your dynamodb table>>")

    current_date = datetime.datetime.now().strftime("%Y-%m-%d")

    table.put_item(
        Item={
            "ip": ip_address,
            "browser": browser,
            "date": current_date
        }
    )

    print("Data successfully written to DynamoDB.")
