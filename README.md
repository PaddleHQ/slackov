# Slackov
Slackov is a Slack bot that uses [Markov chains](http://setosa.io/ev/markov-chains/) to generate random and funny sentences based on users' past posts.

The initial version of Slackov was created during the 2018 Q1 hackathon by [Rob Aiken](https://github.com/robaiken) and [Anna Wittrup](https://github.com/annawittrup). The project won the best use of Technology. 

Paddle is hiring; please look at our [careers page](https://paddle.com/careers/) for more information.

## Set up
*Note: This build was designed to run on a Heroku instance.*

[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Generate a Slack Legacy token
[Click here to generate a legacy token for slack](https://api.slack.com/custom-integrations/legacy-tokens)

### Slackov
1. Clone this repo
2. Set the database credentials and Stack token in [settings.cfg](https://github.com/PaddleHQ/slackov/blob/master/settings.cfg.example) or set up the environment variables.
3. Deploy to a host of choice

This will create 4 endpoints:
* `/generate/user` - This generates a Slackov based on user
* `/generate/channel` - This generates a Slackov based on channel
* `/generate/combination` - This generates a Slackov based on 2 or more users
* `/employee/toggle` - This allows users to disable the ability to generate a Slackov on them

#### Env Variables
* `DB_SYSTEM` - Slackov supports PostgreSQL, MySQL and SQLite
* `DB_USERNAME` - Databases username
* `DB_PASSWORD`  - Databases password
* `DB_HOST` - Databases host
* `DB_DATABASE`  - The name of Databases username
* `SLACK_TOKEN` - Slack Legacy token

### Run the crawler
1. cd into the Slackov directory
2. run `python crawl.py`,  this will populate your database - this might take a while
3. (optional) Set up a cron job to run this command or use [Heroku Scheduler](https://devcenter.heroku.com/articles/scheduler)

### Slackbot
1. (Create a slack app)[https://api.slack.com/slack-apps]
2. On the Slackapp page go to: Features -> Slash Commands
3. Create the following commands (remember to uncheck "Escape channels, users, and links sent to your app")
    - `/slackov_user` - Request URL: https://example.com/generate/user
    - `/slackov_channel` - Request URL: https://example.com/generate/channel
    - `/slackov_combine` - Request URL: https://example.com/generate/combination
    - `/slackov_toggle` - Request URL: https://example.com/employee/toggle
    
## Usage
Here is how to use the Slack commands

### /slackov_user
`/slackov_user @user [channel name|sentence starts with]`

1. `/slackov_user @user`
2. `/slackov_user user #random`
3. `/slackov_user user hello`

### /slackov_channel
`/slackov_channel #channel`

1. `/slackov_channel #random`
2. `/slackov_channel random`

### /slackov_combine
`/slackov_combine #channel`

1. `/slackov_combine @user1 user2`
2. `/slackov_combine @user1 @user2 user3 @user4`

### /slackov_toggle
`/slackov_toggle [enable|disable]`

1. `/slackov_toggle enable`
2. `/slackov_toggle disable`
