"""
This demonstrates an implementation of the Lex Code Hook Interface
in order to serve a bot which manages shipping service.
Bot, Intent, and Slot models which are compatible with this sample can be found in the Lex Console
as part of the 'ShippingService' intent.

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


def close(session_attributes, fulfillment_state, message,tracking_id):
    """
    response = {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }
    """

    # Replace sender@example.com with your "From" address.
    # This address must be verified with Amazon SES.
    sender = "kanthedgaurav@gmail.com"

    # Replace recipient@example.com with a "To" address. If your account
    # is still in the sandbox, this address must be verified.
    recipient = "kanthedgaurav@gmail.com"

    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    awsregion = "us-east-1"

    # The subject line for the email.
    subject = "Mail From DHL Service Application -- Confirmation of shipping"

    # The HTML body of the email.
    htmlbody = """<h1>DHL Shipping Service</h1><p>Thanks for Visitng DHL shipping service, We have placed your reservation and you can use tracking# """ + tracking_id + """. </p>"""
    # The email body for recipients with non-HTML email clients.
    textbody = "Thanks for Visitng DHL shipping service, We have placed your reservation and you can use " + tracking_id + " to track the shipment"

    # The character encoding for the email.
    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client('ses',region_name=awsregion)
    print (htmlbody)
    print (textbody)
    # Try to send the email.
    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                   'ToAddresses': [
                    recipient,
                ],
           },
           Message={
               'Body': {
                   'Html': {
                       'Charset': charset,
                       'Data': htmlbody,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': textbody,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except Exception as e:
        print ("Error: ", e)
    else:
        print ("Email sent!")

    return {
        'sessionAttributes': session_attributes,
        'dialogAction': {
            'type': 'Close',
            'fulfillmentState': fulfillment_state,
            'message': message
        }
    }


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


def generate_shipping_price(location, days, drop_location):
    """
    Generates a number within a reasonable range that might be expected for a flight.
    The price is fixed for a given pair of locations.
    """

    base_location_cost = 0
    for i in range(len(location)):
        base_location_cost += ord(location.lower()[i]) - 97

    for i in range(len(drop_location)):
        base_location_cost += ord(drop_location.lower()[i]) - 97

    #age_multiplier = 1
    # Select economy is car_type is not found
    """if car_type not in car_types:
        car_type = car_types[0]
     """
    return days * ((10 + base_location_cost))

def isvalid_city(city):
    valid_cities = ['new york', 'los angeles', 'chicago', 'houston', 'philadelphia', 'phoenix', 'san antonio',
                    'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'san francisco', 'indianapolis',
                    'columbus', 'fort worth', 'charlotte', 'detroit', 'el paso', 'seattle', 'denver', 'washington dc',
                    'memphis', 'boston', 'nashville', 'baltimore', 'portland']
    return city.lower() in valid_cities

def isvalid_date(date):
    try:
        dateutil.parser.parse(date)
        return True
    except ValueError:
        return False


def get_day_difference(later_date, earlier_date):
    later_datetime = dateutil.parser.parse(later_date).date()
    earlier_datetime = dateutil.parser.parse(earlier_date).date()
    return abs(later_datetime - earlier_datetime).days


def add_days(date, number_of_days):
    new_date = dateutil.parser.parse(date).date()
    new_date += datetime.timedelta(days=number_of_days)
    return new_date.strftime('%Y-%m-%d')


def build_validation_result(isvalid, violated_slot, message_content):
    return {
        'isValid': isvalid,
        'violatedSlot': violated_slot,
        'message': {'contentType': 'PlainText', 'content': message_content}
    }


def validate_shipping(slots):
    pickup_city = try_ex(lambda: slots['PickUpCity'])
    pickup_date = try_ex(lambda: slots['PickUpDate'])
    dropoff_city = try_ex(lambda: slots['DropOffCity'])
    dropoff_date = try_ex(lambda: slots['DropOffDate'])


    if pickup_city and not isvalid_city(pickup_city):
        return build_validation_result(
            False,
            'PickUpCity',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(pickup_city)
        )

    if dropoff_city and not isvalid_city(dropoff_city):
        return build_validation_result(
            False,
            'PickUpCity',
            'We currently do not support {} as a valid destination.  Can you try a different city?'.format(pickup_city)
        )

    if pickup_date:
        if not isvalid_date(pickup_date):
            return build_validation_result(False, 'PickUpDate', 'I did not understand your pickup date.  When would you like to pick up your Shipment?')
        if datetime.datetime.strptime(pickup_date, '%Y-%m-%d').date() <= datetime.date.today():
            return build_validation_result(False, 'PickUpDate', 'Shipment must be scheduled at least one day in advance.  Can you try a different date?')

    if dropoff_date:
        if not isvalid_date(dropoff_date):
            return build_validation_result(False, 'DropOffDate', 'I did not understand your DropOff date.  When would you like to DropOff your shipment?')
        if datetime.datetime.strptime(dropoff_date, '%Y-%m-%d').date() <= datetime.date.today() or datetime.datetime.strptime(dropoff_date, '%Y-%m-%d').date() <= datetime.datetime.strptime(add_days(datetime.date.today().strftime('%Y-%m-%d'), 4), '%Y-%m-%d').date():
            return build_validation_result(False, 'DropOffDate', 'Drop off must be scheduled at least 5 days in advance.  Can you try a different date?')

    if pickup_date and dropoff_date:
        if dateutil.parser.parse(pickup_date) >= dateutil.parser.parse(dropoff_date):
            return build_validation_result(False, 'DropOffDate', 'Your Drop off date must be after your pick up date.  Can you try a different drop off date?')

        if get_day_difference(pickup_date, dropoff_date) > 60:
            return build_validation_result(False, 'DropOffDate', 'You can reserve a shipment for up to sixtey days.  Can you try a different drop off date?')

    return {'isValid': True}
""" --- Functions that control the bot's behavior --- """

def shipping_service(intent_request):
    """
    Performs dialog management and fulfillment for shipping a package.

    Beyond fulfillment, the implementation for this intent demonstrates the following:
    1) Use of elicitSlot in slot validation and re-prompting
    2) Use of sessionAttributes to pass information that can be used to guide conversation
    """
    slots = intent_request['currentIntent']['slots']
    pickup_city = slots['PickUpCity']
    pickup_date = slots['PickUpDate']
    dropoff_city = slots['DropOffCity']
    dropoff_date = slots['DropOffDate']

    confirmation_status = intent_request['currentIntent']['confirmationStatus']
    session_attributes = intent_request['sessionAttributes'] if intent_request['sessionAttributes'] is not None else {}
    last_confirmed_reservation = try_ex(lambda: session_attributes['lastConfirmedReservation'])
    if last_confirmed_reservation:
        last_confirmed_reservation = json.loads(last_confirmed_reservation)

    # Load confirmation history and track the current reservation.
    reservation = json.dumps({
        'PickUpCity': pickup_city,
        'PickUpDate': pickup_date,
        'DropOffCity': dropoff_city,
        'DropOffDate': dropoff_date
    })

    if pickup_city and pickup_date and dropoff_city and dropoff_date :
        # Generate the price of the package in case it is necessary for future steps.
        price = generate_shipping_price(pickup_city, get_day_difference(pickup_date, dropoff_date), dropoff_city)
        session_attributes['currentReservationPrice'] = price

    if intent_request['invocationSource'] == 'DialogCodeHook':
        # Validate any slots which have been specified.  If any are invalid, re-elicit for their value
        validation_result = validate_shipping(intent_request['currentIntent']['slots'])
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
            return delegate(session_attributes, intent_request['currentIntent']['slots'])


    # Helper class to convert a DynamoDB item to JSON.
    class DecimalEncoder(json.JSONEncoder):
        def default(self, o):
            if isinstance(o, decimal.Decimal):
                if o % 1 > 0:
                    return float(o)
                else:
                    return int(o)
            return super(DecimalEncoder, self).default(o)

    dynamodb = boto3.resource("dynamodb", region_name='us-east-1', endpoint_url="http://dynamodb.us-east-1.amazonaws.com")

    table = dynamodb.Table('Shipping')


    now = datetime.datetime.now()
    tracking_id = str(now.microsecond)+str(now.month)+str(now.day)+str(now.minute)+str(now.second)
    response = table.put_item(
       Item={
            'tracking_id':tracking_id,
            'pickupcity': pickup_city,
            'pickupdate': pickup_date,
            'dropoffcity': dropoff_city,
            'dropoffdate': dropoff_date
        }
    )

    print("PutItem succeeded:")
    print(json.dumps(response, indent=4, cls=DecimalEncoder))
    return close(
        session_attributes,
        'Fulfilled',
        {
            'contentType': 'PlainText',
            'content': 'Thanks, I have placed your reservation.'
        },
        tracking_id
    )


# --- Intents ---


def dispatch(intent_request):
    """
    Called when the user specifies an intent for this bot.
    """

    logger.debug('dispatch userId={}, intentName={}'.format(intent_request['userId'], intent_request['currentIntent']['name']))

    intent_name = intent_request['currentIntent']['name']

    # Dispatch to your bot's intent handlers
    if intent_name == 'ShippingService':
        return shipping_service(intent_request)

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
