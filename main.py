import requests
import json
import sqlite3
import twilio
import twilio.rest
import time
from threading import Thread


dbCon = sqlite3.connect('db/numbers.db')
cur = dbCon.cursor()

seconds_between_sending = 60 # Wait 60 seconds between sending messages

twilio_authkey = "f8d3153b6c2b6e8b2595f3cb3179ef93"
twilio_account_sid = "AC8f2693864aae63cd82dbd90f844e525b"

client = twilio.rest.TwilioRestClient(twilio_account_sid, twilio_authkey)

class User:
  def __init__(self, u_id, name, number, lastmessage):
    self.u_id = u_id
    self.name = name
    self.number = number
    self.last_message_sent = lastmessage

  def send_sms(self, catfact):
    client.messages.create(body=catfact,
      to=self.number,
      from_="+14848512309")
    cur.execute("UPDATE number SET last_sent_message = %s WHERE id = %s" % (time.time(), self.u_id))
    dbCon.commit()

# Return users who haven't had a message sent to them in the last seconds_between_sending minutes
def get_users_to_send():
  query = "SELECT * FROM number WHERE (%s - last_sent_message) >= %s" % (time.time(), seconds_between_sending)
  cur.execute(query)
  tmpUsers = cur.fetchall()
  users = []
  for i in tmpUsers:
    tmpUser = User(i[0], i[2], i[1], i[3])
    users.append(tmpUser)
  return users

def get_cat_fact():
  r = requests.get('http://catfacts-api.appspot.com/api/facts')
  jsonRes = json.loads(r.text)
  return jsonRes["facts"][0]

def loop():
  # Get the users I have to send to
  users = get_users_to_send()
  # If greater than one get the cat facts
  if len(users) == 0:
    return
  catfact = get_cat_fact()
  # Loop through each user and send a SMS to their phone with the cat fact
  for user in users:
    if user.last_message_sent == 0:
      # We haven't sent them a message before! Lets send them a greeting!
      user.send_sms("Greetings %s, you have been signed up to CatFacts! Enjoy your FREE catfacts hourly!" % user.name)
    print("Sending an SMS to %s" % user.name)
    user.send_sms("CatFact: " + catfact)

if __name__ == "__main__":
  while True:
    print("Looping")
    loop()
