import os

from flask import Flask, make_response, request
from flask.json import jsonify

from mozapkpublisher.common.googleplay import connect


app = Flask(__name__)


# Settings
PLAY_ACCOUNT = os.getenv('PLAY_ACCOUNT')
PLAY_CREDENTIALS_PATH = os.getenv('PLAY_CREDENTIALS_PATH')


def get_reviews_service():
    """Create new instance of google play API service."""
    service = connect(PLAY_ACCOUNT, PLAY_CREDENTIALS_PATH)
    return service.reviews()


@app.route('/reviews', methods=['GET'])
def get_reviews():
    """Get playstore reviews. Proxy playstore API requests."""
    packageName = request.args.get('packageName', None)
    nextPageToken = request.args.get('nextPageToken', None)

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
