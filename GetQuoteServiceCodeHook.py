"""
This demonstrates an implementation of the Lex Code Hook Interface
in order to serve a  bot which manages get quote service.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'GetQuoteService' intent.

"""
from __future__ import print_function
import json
import datetime
import time
import os
import dateutil.parser
import logging
import boto3
import decimal

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


# --- Helpers that build all of the responses ---


def elicit_slot(session_attributes, intent_name, slots, slot_to_elicit, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ElicitSlot',
            'intentName': intent_name,
            'slots': slots,
            'slotToElicit': slot_to_elicit,
            'message': message
        }
    }


def confirm_intent(session_attributes, intent_name, slots, message):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'ConfirmIntent',
            'intentName': intent_name,
            'slots': slots,
            'message': message
        }
    }


def close(session_attributes, fulfillment_state, message):
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }

    return response


def delegate(session_attributes, slots):
    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Delegate',
            'slots': slots
        }
    }


# --- Helper Functions ---


def safe_int(n):
    """
    Safely convert n value to int.
    """
    if n is not None:
        return int(n)
    return n


def try_ex(func):
    """
    Call passed in function in try block. If KeyError is encountered return None.
    This function is intended to be used to safely access dictionary.

    Note that this function would have negative impact on performance.
    """

    try:
        return func()
    except KeyError:
        return None


def generate_shipping_price(pickup_city, dropoff_city, box_type):
    """
    Generates a number within a reasonable range that might be expected for a shipping
    The price is fixed for a given pair of locations.
    """

    base_location_cost = 0
    for i in range(len(pickup_city)):
        base_location_cost += ord(pickup_city.lower()[i]) - 97

    for i in range(len(dropoff_city)):
        base_location_cost += ord(dropoff_city.lower()[i]) - 97

    p=0

    if box_type == 'Envelope 1':
        p=10
    elif box_type == 'Box 2':
        p=20
    elif box_type == 'Box 3':
        p=30
    elif box_type == 'Box 4':
        p=32
    elif box_type == 'Box 5':
        p=34
    elif box_type == 'Box 6':
        p=36
    elif box_type == 'Box 7':
        p=38


    return p + ((10 + base_location_cost))


def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities

def isvalid_box(box_type):
    box_types = ["Envelope 1","Box 2","Box 3","Box 4","Box 5","Box 6","Box 7"]
    return box_type.title() in box_type

def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_get_quote(slots):

    #shipping_type = try_ex(lambda: slots['ShippingType'])
    pickup_city = try_ex(lambda: slots['PickUpCityt'])
    dropoff_city = try_ex(lambda: slots['DropOffCityt'])
    box_type = try_ex(lambda: slots['BoxType'])

    if pickup_city and not isvalid_city(pickup_city):
        return build_validation_result(
            False,
            'PickUpCityt',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(pickup_city)
        )

    if dropoff_city and not isvalid_city(dropoff_city):
        return build_validation_result(
            False,
            'DropOffCityt',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(dropoff_city)
        )

    if box_type and not isvalid_box(box_type):
        return build_validation_result(
            False,
            'BoxType',
            'We currently do not support {} as a valid box Type.  Can you choose between Envelope 1 or Box 2 or Box 3 or Box 4 or Box 5 or  Box 6 or Box 7?'.format(box_type)
        )

    return {'isValid': True}

def getquote_service(intent_request):
    """
    Performs dialog management and fulfillment for getting quote.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    slots = intent_request['currentIntent']['slots']
    pickup_city = slots['PickUpCityt']
    dropoff_city = slots['DropOffCityt']
    box_type = slots['BoxType']

    price = None
    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    last_confirmed_reservation = try_ex(lambda: session_attributes['lastConfirmedReservation'])
    if last_confirmed_reservation:
        last_confirmed_reservation = json.loads(last_confirmed_reservation)

    # Load confirmation history and track the current reservation.
    reservation = json.dumps({
        'PickUpCityt': pickup_city,
        'DropOffCityt': dropoff_city,
        'BoxType': box_type
    })

    if intent_request['invocationSource'] == 'DialogCodeHook':

        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_get_quote(intent_request['currentIntent']['slots'])

        if not validation_result['isValid']:

            slots[validation_result['violatedSlot']] = None

            return elicit_slot(
                session_attributes,
                intent_request['currentIntent']['name'],
                slots,
                validation_result['violatedSlot'],
                validation_result['message']
            )


        # Determine if the intent (and current slot settings) has been denied.  The messaging will be different
        if confirmation_status == 'None':
            if pickup_city and dropoff_city and box_type :
                price = generate_shipping_price(pickup_city, dropoff_city, box_type)
                print(price)
            return delegate(session_attributes, intent_request['currentIntent']['slots'])


    if pickup_city and dropoff_city and box_type :
        price = generate_shipping_price(pickup_city, dropoff_city, box_type)
        print(price)

    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, The price of your request becomes ${} .'.format(price)
        }
    )


# --- Intents ---

def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'GetQuoteService':
        return getquote_service(intent_request)

    raise Exception('Intent with name ' + intent_name + ' not supported')


# --- Main handler ---


def lambda_handler(event, context):
    """
    Route the incoming request based on intent.
    The JSON body of the request is provided in the event slot.
    """
    # By default, treat the user request as coming from the America/New_York time zone.
    os.environ['TZ'] = 'America/New_York'
    time.tzset()
    logger.debug('event.bot.name={}'.format(event['bot']['name']))

    return dispatch(event)
