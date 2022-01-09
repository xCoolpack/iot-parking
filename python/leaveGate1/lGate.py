#!/usr/bin/env python3

import paho.mqtt.client as mqtt
from paho.mqtt.client import MQTTv311
import ssl
import tkinter
import random
import time
import gateClientConfig as config
### RaspberryPi version: ###

#import time
#import RPi.GPIO as GPIO
#from config import *  # pylint: disable=unused-wildcard-import
#from mfrc522 import MFRC522

#def rfidRead():
#    MIFAREReader = MFRC522()
#    counter = 0
#    uid = 0
#    while counter < 3:
#        (status, TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
#        if status == MIFAREReader.MI_OK:
#            (status, uid) = MIFAREReader.MFRC522_Anticoll()
#            if status == MIFAREReader.MI_OK:
#                num = 0
#                for i in range(0, len(uid)):
#                    num += uid[i] << (i*8)
#                print(f"Card read UID: {uid} > {num}")
#                time.sleep(0.5)
#                counter += 1
#    return uid

### END - RaspberryPi version ###

broker = config.broker
port = config.port
client_id = config.client_id
username = config.username
password = config.password
topic = f"{config.topic}/{client_id}"

caCrt = config.caCrt
clientCrt = config.clientCrt
clientKey = config.clientKey
keyPassword = config.keyPassword

client = None
window = tkinter.Tk()


def process_message(client, userdata, message):
    message_decoded = (str(message.payload.decode("utf-8")))
    split = message_decoded.split(":")
    if split[1] != "Client connected" and split[1] != "Client disconnected":
        print(message_decoded)
    else:
        print(split[1])


def call_worker(card_number):
    client.publish(topic, payload="card:"+card_number, qos=2, retain=False)


def create_main_window():
    window.geometry("300x200")
    window.title("SENDER")

    tkinter.Label(window, text="Card number").grid(row=3, padx=5, pady=5)

    e1 = tkinter.Entry(window)
    e1.grid(row=3, column=2, pady=5, ipady=7)
     
    button_send = tkinter.Button(window, text="Send",
                              command=lambda: call_worker(e1.get()))
    button_send.grid(row=4, column = 0, columnspan=3, sticky=tkinter.E, pady=5, ipady=3, ipadx=7)

    button_stop = tkinter.Button(window, text="Stop", command=window.quit)
    button_stop.grid(row=4, column = 2, columnspan=3, sticky=tkinter.W, pady=5, ipady=3, ipadx=7 )


def get_input():
    u_input = ""
    print("type 'exit' to finish")
    while u_input != "exit":
        u_input = input("Enter card id: ")
        call_worker(u_input)
        time.sleep(1)
        
        
def connect_to_broker():
    global client
    client = mqtt.Client(client_id, clean_session=False, protocol=MQTTv311, transport="tcp")
    client.username_pw_set(username, password)
    client.tls_set(ca_certs=caCrt, certfile=clientCrt, keyfile=clientKey, tls_version=ssl.PROTOCOL_TLSv1_2,
                   ciphers=None, keyfile_password=keyPassword, cert_reqs=ssl.CERT_NONE)
    client.connect(broker, port)
    client.on_message = process_message
    client.loop_start()
    channel_ret = topic + "/r"
    client.subscribe(channel_ret)


def disconnect_from_broker():
    call_worker("Client disconnected")
    client.loop_stop()
    client.disconnect()


def run_sender():
    connect_to_broker()
    # get_input() # for console input
    create_main_window()
    window.mainloop()
    disconnect_from_broker()


if __name__ == "__main__":
    run_sender()
