


class JiraResponseBuilder(object):

    def __init__(self, event, fulfillment_state=None, message=None):
        self._event = event
        self._fulfillment_state = fulfillment_state
        self._message = message

    def with_fulfillment_state(self, fulfillment_state):
        return JiraResponseBuilder(self._event, fulfillment_state=fulfillment_state,
                                   message=self._message)

    def with_message(self, message):
        return JiraResponseBuilder(self._event, fulfillment_state=self._fulfillment_state,
                                   message=message)

    def build(self):
            return {
            'sessionAttributes': self._event['sessionAttributes'],
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': self._fulfillment_state,
                'message': {
                    'contentType': 'PlainText',
                    'content': self._message
                }
            }
        }
