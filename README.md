# BERND

> Made for the [TOSTI API](https://github.com/KiOui/TOSTI)

![Bernd the Bread](.\static\images\Bernd_NB.png)

**Have you ever wanted to be the first to enjoy a delicious tosti? Are you tired of waiting?**


Introducing BERND the Beautified Eating Retrieval Network for Desirable toasties! With BERND, you can order your favorite tostis in seconds and always be the fastest to get your cravings satisfied. Don't wait any longer; experience the future of tosti ordering today!

## Usage
1. **Clone the Repository:**
    - Run the following command to clone this repository to your local machine:
        ```bash
        git clone git@github.com:Shepherd-ITSec/BERND.git
        ```

2. **Create a Bot account:**
    - Go to [Oauth Credentials](https://tosti.science.ru.nl/users/account/?active=oauth_credentials) tab in your Tosti account
    - Create a new application and add `https://localhost:5000/callback` to the Redirect uris. Please write down your Credentials safely.

2. **Insert Your Secrets:**
    - Add your API secrets from the Tosti website to the configuration file.
    - Change the setting to your liking
        > Node: please keep the polling interval reasonably small to not stress the tosti api. 


3. **Rename the Configuration Template:**
    - Rename config.template to config.ini:
        ```bash
        mv config.template config.ini
        ```

4. **Execute the Script:**
    - Start the application shortly before the lunch break using the following command:
        ```bash
        python tosti_BERNT.py
        ```
    - Accept the certificate waring (the tosti API forces us to enter a https redirection website, so we do on the fly https)
    - Authenticate your Bot (you may have to login first)

5. **Enjoy Your Tostis!:**
    - Sit back, relax, and indulge in delicious tostis!

## Disclaimer
*Please use on own risk*
All images used are licensed under public license.
The [TOSTI API](https://github.com/KiOui/TOSTI) is not written or maintained by me.

