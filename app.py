import re
import datetime
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, render_template, flash, request
from db import Database


logPath = r'log\registrationApp-log.log'
# Set the name of the object we are logging for
_logger = logging.getLogger("RegistrationApp")
_logger.setLevel(logging.DEBUG)
handler = RotatingFileHandler(logPath, maxBytes=20971520, backupCount=10)
# Format the log message to display the time, object name, the logging level, and the message.
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
_logger.addHandler(handler)

app = Flask(__name__)

"""Flask Framework methods to handle routing between the different pages"""


@app.route("/")
def register():
    _logger.info('Accessing Home Page.')
    # returns the main registration page.
    return render_template('register.html')

# url used to post the data from the the form.
# Handles receiving the data, validating the data, and writing
# to the SQLite Database.


@app.route('/submit-form', methods=['POST'])
def registration():
    _logger.info('POST has been received, processing data.')
    try:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        address1 = request.form['address1']
        address2 = request.form['address2']
        city = request.form['city']
        state = request.form['state']
        zip = request.form['zip']
        country = request.form['country']

        # Perform some minor validation to the data. In reality if time
        # was not a factor, the validation for the address would be donw
        # against a Address Validation API.
        # Make sure the first and last names don't contain digits.
        _logger.info('Validating Data.')
        if re.search(r'\d', first_name) or re.search(r'\d', last_name):
            flash('Names Cannot contain numbers')
        # Makes sure at least one address field contains text.
        elif not address1 and not address2:
            flash('Must include an address!')
        # Make sure city, state and zip are all there.
        elif not city or not state or not zip:
            flash('Must include city, state, and zip!')
        elif zip:
            zip = re.sub('[^0-9]', '', zip)
        # Validate that the country is US.
        elif country.upper() == 'USA' or country.upper == 'UNITED STATES' or country.upper() == 'UNITED STATES OF AMERICA':
            country = 'US'
        elif country != 'US':
            flash('Only accapting US registrations!')

        # Get the current date to use as a timestamp for the Database,
        # and convert it to a string since we are using SQLite for simplicity's
        # sake.
        date = datetime.datetime.now()
        date = date.strftime('%m/%d/%Y')

        # Generate the query to be used with the database call.
        query = "values ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (first_name, last_name,
                                                                                   address1, address2, city,
                                                                                   state, zip, country, date)
        # Create an instance of the database object and post the new user.
        _logger.info('Sending data to Database.')
        db_obj = Database(_logger)
        result = db_obj.post_to_db(query)

        # If the post is successfull, return the thank you page.
        if result == 'Success':
            _logger.info('Data Stored Successfully!')
            return render_template('thank-you.html')
        # Otherwise return an error message.
        else:
            _logger.info('Unable Store Data!')
            flash('Something Went Wrong! Unable to process Registration')
            return None
    except Exception as e:
        _logger.info('Error processing data: %s' % str(e))
        flash('Something Went Terribly Wrong!')
        return render_template('register.html')


@app.route('/admin/reports', methods=['GET'])
# Handler for the admin/reports page. Gets the data from the DB, and
# returns it to a table in the html file.
def getReport():
    _logger.info('Accessing Database')
    db_obj = Database(_logger)
    _logger.info('Fetching registered users.')
    registered_users = db_obj.fetch_from_db()

    if registered_users:
        _logger.info('Users Fetched Successfully!')
        return render_template('reportsPage.html', data=registered_users)
    else:
        _logger.info('Unable to fetch users.')
        return render_template('reportsPage.html', data=None)


if __name__ == '__main__':
    _logger.info('Server is Listening.....')
    app.run(debug=True)
