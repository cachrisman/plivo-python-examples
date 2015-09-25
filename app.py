import os

from flask import Flask, request, make_response, Response
import plivo, plivoxml


app = Flask(__name__)

# Use the url which heroku gives you after deploying
base_url = 'https://charlieplivo.herokuapp.com'

auth_id = '***REMOVED***'
auth_token = '***REMOVED***'

# <Dial> Element attributes
dial_callerId = ''
dial_action = base_url + 'playxml/'
dial_number = ''


# <Play> Element attributes
play_url = 'http://example.com/trumpet.mp3'
play_loop = 2


@app.route("/", methods=['GET'])
def index():
    return 'Welcome to Plivo'


@app.route("/call/", methods=['POST'])
def call():
    """
    POST parameters:
        to - to phone number
        from - from phone number
        answer_url - url to call upon answer
        answer_method - method for answer url
        hangup_url - url to call on hangup( defaults to answer_url if not present)
        hangup_method - method for hangup_url
    """
    if request.method == 'POST':
        to_number = request.form['to']
        from_number = request.form['from']
        # answer_url can be 'base_url/playxml/' , 'base_url/dialxml/', or your custom XML
        answer_url = request.form['answer_url']

        try:
            answer_method = request.form['answer_method']
        except KeyError:
            answer_method = 'GET'

        try:
            hangup_url = request.form['hangup_url']
        except KeyError:
            hangup_url = answer_url

        try:
            hangup_method = request.form['hangup_method']
        except KeyError:
            hangup_method = answer_method

        p = plivo.RestAPI(auth_id, auth_token)
        call_params = {'to': to_number,
                       'from': from_number,
                       'answer_url': answer_url,
                       'answer_method': answer_method,
                       'hangup_url': hangup_url,
                       'hangup_method': hangup_method,
                       }
        status, response = p.make_call(call_params)

        if response['message'] != 'call fired':
            return 'Call Failed'
        else:
            return 'Call has been made'


@app.route("/dialxml/", methods=['GET'])
def dial_xml():
    """
    Return a <Dial> element. This element connects the caller
    to another phone. When the called party picks the call,
    the two are connected until one hangs up. If the called
    party does not pick up, or if the number doesn't exist,
    the <Dial> element will end.
    """
    if request.method == 'GET':
        r = plivo.Response()

        d = r.addDial(callerId=dial_callerId)
        d.addNumber(dial_number)

        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response


@app.route("/speakxml/", methods=['GET'])
def speak_xml():
    """
    <Speak> : This element reads the text as
    speech to the caller. It is very useful for dynamic text
    that cannot be pre-recorded.

    <Wait> : This element waits silently for a specified number of
    seconds. If <Wait> is the first element in a XML document,
    Plivo will wait the specified number of seconds before
    picking up the call
    """

    if request.method == 'GET':
        r = plivo.Response()
        r.addWait(length=2)
        r.addSpeak('Hi')

        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response


@app.route("/playxml/", methods=['GET'])
def play_xml():
    """
    Returns a <Play> element. This element plays an audio file
    back to the caller. Plivo allows playback from a remote url.
    Currently mp3 and wav file formats are supportd
    """
    if request.method == 'GET':
        r = plivo.Response()
        p = r.addPlay(play_url, loop=play_loop)

        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response


@app.route("/recordxml/", methods=['GET'])
def record_xml():
    """
    Returns a <Record> element. This element records the caller’s
    voice and stores the file containing the audio recording.
    """

    if request.method == 'GET':
        r = plivo.Response()
        r.addSpeak('Leave a message after the beep')
        r.addRecord(action=base_url + 'save_record_url/',
                    maxLength=30,
                    playBeep=True)

        response = make_response(r.to_xml())
        response.headers['Content-Type'] = 'text/xml'
        return response


@app.route("/save_record_url/", methods=['GET'])
def save_record_url():
    record_file = request.args['RecordFile']
    # Save the record_file


@app.route('/forward_sms/', methods=['GET', 'POST'])
def inbound_sms():

    # Sender's phone number
    from_number = request.values.get('From')

    # Receiver's phone number - Plivo number
    to_number = request.values.get('To')

    # The text which was received
    text = request.values.get('Text')

    # Print the message
    print 'Text received: %s - From: %s' % (text, from_number)

    # Generate a Message XML with the details of the reply to be sent

    resp = plivoxml.Response()

    # The phone number to which the SMS has to be forwarded
    to_forward = '3333333333'

    body = 'Forwarded message : %s' % (text)
    params = {
        # Sender's phone number
        'src': to_number,
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
    app.run(host='0.0.0.0', port=port)
