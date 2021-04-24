from boltiot import Bolt,Email
import json, time, requests 
import email_conf, conf  
maximum_limit = 50  #the maximum threshold of distance value 


mybolt = Bolt(email_conf.API_KEY, email_conf.DEVICE_ID)
mailer = Email(email_conf.MAILGUN_API_KEY, email_conf.SANDBOX_URL, email_conf.SENDER_EMAIL, email_conf.RECIPIENT_EMAIL)


def get_sensor_value_from_pin(pin):
    """Returns the sensor value. Returns -999 if request fails"""
    try:
        response = mybolt.analogRead(pin)
        data = json.loads(response)
        if data["success"] != 1:
            print("Request not successfull")
            print("This is the response->", data)
            return -999
        sensor_value = int(data["value"])
        return sensor_value
    except Exception as e:
        print("Something went wrong when returning the sensor value")
        print(e)
        return -999
def send_telegram_message(message):
    """Sends message via Telegram"""
    url = "https://api.telegram.org/" + conf.telegram_bot_id + "/sendMessage"
    data = {
        "chat_id": conf.telegram_chat_id,
        "text": message
    }
    try:
        response = requests.request(
            "POST",
            url,
            params=data
        )
        print("This is the Telegram URL")
        print(url)
        print("This is the Telegram response")
        print(response.text)
        telegram_data = json.loads(response.text)
        return telegram_data["ok"]
    except Exception as e:
        print("An error occurred in sending the alert message via Telegram")
        print(e)
        return False
while True: 
    print ("Reading sensor value")
    response = mybolt.analogRead('A0') 
    data = json.loads(response) 
    print ("Sensor value is: " + str(data['value']))
    try: 
        sensor_value = int(data['value']) 
        if sensor_value <  maximum_limit:
            print ("Making request to Mailgun to send an email")
            response = mailer.send_email("Alert", "Object/Enemy is closing in! " +  str(conf.threshold) + \
                  ". Someone is there " +str(sensor_value))
            response_text = json.loads(response.text)
            print ("Response received from Mailgun is: " + str(response_text['message']))
        if sensor_value >= conf.threshold: 
            print ("Sensor value has exceeded threshold")
            message = "Alert!Someone near the distance " + str(conf.threshold) + \
                  ". Protect the Plant, near the distance " + str(sensor_value)
            telegram_status = send_telegram_message(message)
            print ("This is the Telegram status:", telegram_status)
 
        if sensor_value == -999:
           print ("Request was unsuccessfull. Skipping.")
        time.sleep(10)
        continue
    except Exception as e: 
        print ("Error occured: Below are the details")
        print (e)
    time.sleep(10)
