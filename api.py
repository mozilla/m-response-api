import base64
import io
import os

from flask import Flask, make_response, request
from flask.json import jsonify

import boto3
import httplib2

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def get_credentials():
    """Fetch playstore credentials from SSM"""

    # Fetch credentials from AWS SSM
    ssm = boto3.client('ssm')
    key_response = ssm.get_parameter(
        Name='SumoPlaystoreReviewsKey', WithDecryption=True)
    account_response = ssm.get_parameter(
        Name='SumoPlaystoreReviewsAccount', WithDecryption=True)

    # Parse SSM responses
    account = account_response['Parameter']['Value']
    key = io.BytesIO(base64.b64decode(key_response['Parameter']['Value']))

    credentials = {
        'key': key,
        'account': account
    }
    return credentials


def get_reviews_service():
    """Create new instance of google play API service."""

    scope = 'https://www.googleapis.com/auth/androidpublisher'
    credentials = get_credentials()
    service_credentials = ServiceAccountCredentials.from_p12_keyfile_buffer(
        credentials['account'], credentials['key'], scopes=scope
    )
    http = httplib2.Http()
    http = service_credentials.authorize(http)
    service = build('androidpublisher', 'v2', http=http, cache_discovery=False)
    return service.reviews()


@app.route('/reviews', methods=['GET'])
def get_reviews():
    """Get playstore reviews. Proxy playstore API requests."""

    packageName = request.args.get('packageName', None)
    nextPageToken = request.args.get('token', None)

    if not packageName:
        content = jsonify(msg='Missing `packageName` from request query')
        return make_response(content, 400)

    reviews_service = get_reviews_service()
    query = reviews_service.list(packageName=packageName, token=nextPageToken)

    return make_response(jsonify(query.execute()), 200)


@app.route('/reviews', methods=['POST'])
def post_reviews():
    """Post playstore reviews."""

    return make_response(jsonify(msg='POST method not implemented'), 501)
