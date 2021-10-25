## General info
The main goal of the market notifications app is to notify the user of any new listings, as specified by the user, in a given marketplace.

Currently, the app is limited to Craigslist's motorcycle listings, the original testing domain. Additionally, the app sends text messages to a T-Mobile phone number via a Google mail account.

## How to Use
1. In the 'market_notifications.py' file, type your T-Mobile phone number and Google email address into the 'settings' dictionary.
2. Change 'max_price' in settings to the maximum price of a new listing that you will be notified of.
3. Run 'python market_notifications.py' in the terminal.
4. Your email password will be prompted for, in order to connect to your email address.
5. The app is running and will notify you of any new listings.

## Current Inconveniences
1. You may have to change the [SMS gateway email client](https://en.wikipedia.org/wiki/SMS_gateway#Email_clients) to match your cell service provider, as it is currently set for T-Mobile.
2. You may have to change 'smtp_server' to match the [SMTP](https://en.wikipedia.org/wiki/Simple_Mail_Transfer_Protocol) server address of your email service, as it is currently set for Google Mail.
3. You are limited to Craigslist motorcycle listings, and you can only set the maximum price for notifications.

## Possible Future Directions
1. Ideally, the email client would be automatically detected. However, the user could also be prompted for a cell provider.
2. Create a local SMTP server, so user does not have to rely on an external service or enter passwords.
3. Provide an interface for different markets and their listings. Notification filtering should also be expanded and customizable.
