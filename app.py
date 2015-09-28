import os

from flask import Flask, request, make_response, Response
import plivo, plivoxml

app = Flask(__name__)

# Use the url which heroku gives you after deploying
base_url = 'https://charlieplivo.herokuapp.com'

@app.route("/", methods=['GET'])
def index():
    return 'Welcome to Plivo'


@app.route('/forward_sms/', methods=['GET', 'POST'])
def inbound_sms():
    # Sender's phone number
    from_number = request.values.get('From')

    # Receiver's phone number - Plivo number
    plivo_number = request.values.get('To')

    # number which to forward message to
    to_forward = request.values.get('forward')

    # The text which was received
    text = request.values.get('Text')

    # Print the message
    print 'Text received: %s - From: %s' % (text, from_number)

    # Generate a Message XML with the details of the reply to be sent
    resp = plivoxml.Response()
    body = '(From: %s) %s' % (from_number, text)
    params = {
        # Sender's phone number
        'src': plivo_number,
        # Receiver's phone number
        'dst': to_forward,
    }

    # Message added
    resp.addMessage(body, **params)

    # Prints the XML
    print resp.to_xml()
    # Returns the XML
    return Response(str(resp), mimetype='text/xml')


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, debug=True)
    app.run(host='0.0.0.0', port=port)
