# Okta Custom Login and Registration Form

This project was built using Python 2.7

This is a very rudimentary/simple case for using the Okta API to login/register and MFA verify via sms.
NOTE: The code is not set up to catch edge cases nor perform robust validation and is meant to serve as a simple example of how to use the Okta API for custom login screens

## Requirements
* Python 2.7
* Okta domain
* Okta API Token

## Dependencies
You can run all the dependencies via the requirements.txt
`pip install -r requirements.txt`

Or run them individually

**linter - flake8**

`pip install flake8`

**Web Framework - flask**

`pip install flask`

**HTTP Framework - Update requests**

Needed to install an update to fix a compatability issue

`pip install requests --upgrade`