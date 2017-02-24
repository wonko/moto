from __future__ import unicode_literals
from six.moves.urllib.parse import parse_qs

import boto
from freezegun import freeze_time
import sure  # noqa

from moto.packages.responses import responses
from moto import mock_sns, mock_sns_deprecated, mock_sqs_deprecated


@mock_sqs_deprecated
@mock_sns_deprecated
def test_publish_to_sqs():
    conn = boto.connect_sns()
    conn.create_topic("some-topic")
    topics_json = conn.get_all_topics()
    topic_arn = topics_json["ListTopicsResponse"][
        "ListTopicsResult"]["Topics"][0]['TopicArn']

    sqs_conn = boto.connect_sqs()
    sqs_conn.create_queue("test-queue")

    conn.subscribe(topic_arn, "sqs",
                   "arn:aws:sqs:us-east-1:123456789012:test-queue")

    conn.publish(topic=topic_arn, message="my message")

    queue = sqs_conn.get_queue("test-queue")
    message = queue.read(1)
    message.get_body().should.equal('my message')


@mock_sqs_deprecated
@mock_sns_deprecated
def test_publish_to_sqs_in_different_region():
    conn = boto.sns.connect_to_region("us-west-1")
    conn.create_topic("some-topic")
    topics_json = conn.get_all_topics()
    topic_arn = topics_json["ListTopicsResponse"][
        "ListTopicsResult"]["Topics"][0]['TopicArn']

    sqs_conn = boto.sqs.connect_to_region("us-west-2")
    sqs_conn.create_queue("test-queue")

    conn.subscribe(topic_arn, "sqs",
                   "arn:aws:sqs:us-west-2:123456789012:test-queue")

    conn.publish(topic=topic_arn, message="my message")

    queue = sqs_conn.get_queue("test-queue")
    message = queue.read(1)
    message.get_body().should.equal('my message')


@freeze_time("2013-01-01")
@mock_sns
@mock_sns_deprecated
def test_publish_to_http():
    responses.add(
        method="POST",
        url="http://example.com/foobar",
    )

    conn = boto.connect_sns()
    conn.create_topic("some-topic")
    topics_json = conn.get_all_topics()
    topic_arn = topics_json["ListTopicsResponse"][
        "ListTopicsResult"]["Topics"][0]['TopicArn']

    conn.subscribe(topic_arn, "http", "http://example.com/foobar")

    response = conn.publish(
        topic=topic_arn, message="my message", subject="my subject")
    message_id = response['PublishResponse']['PublishResult']['MessageId']
