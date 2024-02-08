import boto3
from botocore.exceptions import NoCredentialsError
import os

def extract_layout_from_document(document_path, aws_access_key, aws_secret_key, aws_region='us-east-1'):
    # Initialize Textract client
    textract_client = boto3.client('textract', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key, region_name=aws_region)

    # Read document as bytes
    with open(document_path, 'rb') as file:
        document_bytes = file.read()

    try:
        # response = textract_client.analyze_document(
        #     Document={"Bytes": document_bytes}, FeatureTypes=['layout']
        # )
        # print(response)
        # Start the Textract analysis with the 'layout' feature

        response = textract_client.start_document_text_detection(
            Document={'Bytes': document_bytes}
        )

        # Get the JobId from the response
        job_id = response['JobId']

        # Wait for the analysis job to complete
        response = textract_client.get_document_text_detection(JobId=job_id)
        while response['JobStatus'] == 'IN_PROGRESS':
            response = textract_client.get_document_text_detection(JobId=job_id)

        # Extract layout analysis results from the response
        layout_results = response.get('Blocks', [])

        return layout_results

    except NoCredentialsError:
        print("Credentials not available")

# Replace 'your_access_key', 'your_secret_key', and 'your_document_path' with your own values
aws_access_key = os.environ['AWS_ACCESS_KEY_ID']
aws_secret_key = os.environ['AWS_SECRET_ACCESS_KEY']
document_path = 'docs/laws.pdf'

layout_results = extract_layout_from_document(document_path, aws_access_key, aws_secret_key)

# Now you can process and use the layout_results as needed
print(layout_results)
