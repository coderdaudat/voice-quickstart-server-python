import os
from flask import Flask, request, redirect
from twilio.jwt.access_token import AccessToken, VoiceGrant
from twilio.rest import Client
import twilio.twiml
from __future__ import with_statement   # Only necessary for Python 2.5
from twilio.twiml.voice_response import VoiceResponse

ACCOUNT_SID = 'ACebd7d3a78e2fdda9e51239bad6b09f97'
API_KEY = 'SK028e5bbb3d0b19cb333dfe99ba10c35f'
API_KEY_SECRET = 'Um8JRwIztNvOFED19jRxubSAZXgTmOmH'
PUSH_CREDENTIAL_SID = 'CRfb350e6ad971569433db08ecff29f636'
APP_SID = 'AP5d46bf675557ec0f73b1d08afcfcdc75'

IDENTITY = '+17606215500'
CALLER_ID = 'quick_start'

app = Flask(__name__)

callers = {
    "+14158675309": "Curious George",
    "+14158675310": "Boots",
    "+14158675311": "Virgil",
}

@app.route('/accessToken')
def token():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)
  push_credential_sid = os.environ.get("PUSH_CREDENTIAL_SID", PUSH_CREDENTIAL_SID)
  app_sid = os.environ.get("APP_SID", APP_SID)

  grant = VoiceGrant(
    push_credential_sid=push_credential_sid,
    outgoing_application_sid=app_sid
  )

  token = AccessToken(account_sid, api_key, api_key_secret, IDENTITY)
  token.add_grant(grant)

  return str(token)

@app.route('/outgoing', methods=['GET', 'POST'])
def outgoing():
  resp = twilio.twiml.Response()
  resp.say("Congratulations! You have made your first oubound call! Good bye.")
  return str(resp)

@app.route('/incoming', methods=['GET', 'POST'])
def incoming():
  resp = twilio.twiml.Response()
  resp.say("Congratulations! You have received your first inbound call! Good bye.")
  return str(resp)

@app.route('/placeCall', methods=['GET', 'POST'])
def placeCall():
  account_sid = os.environ.get("ACCOUNT_SID", ACCOUNT_SID)
  api_key = os.environ.get("API_KEY", API_KEY)
  api_key_secret = os.environ.get("API_KEY_SECRET", API_KEY_SECRET)

  client = Client(api_key, api_key_secret, account_sid)
  call = client.calls.create(url=request.url_root + 'incoming', to='client:' + IDENTITY, from_='client:' + CALLER_ID)
  return str(call.sid)

@app.route('/', methods=['GET', 'POST'])
def welcome():
  from_number = request.values.get('From', None)
    if from_number in callers:
        caller = callers[from_number]
    else:
        caller = "Monkey"

    resp = VoiceResponse()
    # Greet the caller by name
    resp.say("Hello " + caller)
    # Play an mp3
    resp.play("http://demo.twilio.com/hellomonkey/monkey.mp3")

    # Gather digits.
    with resp.gather(numDigits=1, action="/handle-key", method="POST") as g:
        g.say("""To speak to a real monkey, press 1. 
                 Press 2 to record your own monkey howl.
                 Press any other key to start over.""")

    return str(resp)
  
@app.route("/handle-key", methods=['GET', 'POST'])
def handle_key():
    """Handle key press from a user."""

    digit_pressed = request.values.get('Digits', None)
    if digit_pressed == "1":
        resp = VoiceResponse()
        # Dial (310) 555-1212 - connect that number to the incoming caller.
        resp.dial("+18052284394")
        # If the dial fails:
        resp.say("The call failed, or the remote party hung up. Goodbye.")

        return str(resp)

    elif digit_pressed == "2":
        resp = VoiceResponse()
        resp.say("Record your monkey howl after the tone.")
        resp.record(maxLength="30", action="/handle-recording")
        return str(resp)

    # If the caller pressed anything but 1, redirect them to the homepage.
    else:
        return redirect("/")

@app.route("/handle-recording", methods=['GET', 'POST'])
def handle_recording():
    """Play back the caller's recording."""

    recording_url = request.values.get("RecordingUrl", None)

    resp = VoiceResponse()
    resp.say("Thanks for howling... take a listen to what you howled.")
    resp.play(recording_url)
    resp.say("Goodbye.")
    return str(resp)

if __name__ == "__main__":
  port = int(os.environ.get("PORT", 5000))
  app.run(host='0.0.0.0', port=port, debug=True)
