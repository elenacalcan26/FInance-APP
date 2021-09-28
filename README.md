# FInance-APP

Web app built with Flask microframework in which users can "buy" and "sell" stocks by querying IEX for stocks’ prices. 
It uses IEX API to get stocks data in real time. The informations about users, their owned stocks and 
their transactions history are stored in a SQLite database. 
The UI is designed using HTML, CSS and Bootstrap framework.


## Functionalities:

#### 1. index
-----------------------------------

  - shows a table summarizing the user currently logged in, which stocks the user owns, the numbers of shares owned, 
the current price of each stock, and the total value of each holding
  - also shows user’s current cash balance along with a grand total (i.e., stocks’ total value plus cash)

![index_page](https://user-images.githubusercontent.com/62752433/134942236-5ff28279-66bc-4e2a-aaa0-e72c3d2e4fc1.png)


&nbsp;

#### 2. login 
----------------------------

  - let the user log in to his account if it exists

![login](https://user-images.githubusercontent.com/62752433/134965207-a0c1ceed-7f14-465a-941e-0f7bf660c431.png)

&nbsp;

#### 3. register
-----------------------------

  - the user creates an account via a form which requiers an unique username and a password
  - the password must be introduced two times for confirmation
  - the password is hashed using Werkzeug Security Helpers
  - after registering, the user will receive 10000$ in his account by default

![register](https://user-images.githubusercontent.com/62752433/134965432-6b559ebb-d4aa-4613-80e8-01b94f92309c.png)


&nbsp;

#### 4. quote
------------------------------

  - give user latest price after inputing a US stock symbol

![quote](https://user-images.githubusercontent.com/62752433/134965466-1ad0e108-457f-417d-9ac1-d64d682d1bad.png)

![quoted](https://user-images.githubusercontent.com/62752433/134965618-b49785e1-b7c8-447f-8b2f-3b4994aec935.png)

&nbsp;

#### 5. buy
--------------------------------

  - enables user to purchase a symbol stock with an amount of shares

![buy](https://user-images.githubusercontent.com/62752433/134965498-cb538657-af43-4b18-9aec-e266844fb1fb.png)


&nbsp;

#### 6. sell
--------------------------------

  - allows user to sell shares of a stock the he owns
  - the stocks owned by the user can be choosen from a drop down menu

![sell](https://user-images.githubusercontent.com/62752433/134965546-db3d6ea4-7bce-4896-bb08-96fd886c1d7d.png)


&nbsp;

#### 7. history
------------------------------

  - summaries all user's transactions

![history](https://user-images.githubusercontent.com/62752433/134965587-a4a04e6b-240d-4b19-ba68-53b258ab4e9c.png)


&nbsp;

#### 8. change password
-----------------------------

  - enables existent users to change password
  - requires the username and the old password the check user's existence
  - the new password must be introduced two times for confirmation

![change-pass](https://user-images.githubusercontent.com/62752433/134965255-6d3bce20-29ed-4819-88dc-b46c9765a4ab.png)

&nbsp;

#### 9. logout
------------------------
  - clears the sessions and takes the user out the application

&nbsp;

## References:

  - the static folder, helpers.py, layout.html and login.html files and the two functionalities, logout and login, are provided by https://cs50.harvard.edu/x/2021/psets/9/finance/
