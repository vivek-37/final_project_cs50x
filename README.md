# MediLog - An online log for all your medical records

## Table of Contents

- [Video Demo](#video-demo)
- [Description](#description)
- [Technologies Used](#technologies-used)
- [Project Structure & Details](#project-structure--details)
- [Improvements & Compromises](#improvements--compromises)
- [Contact](#contact)

## Video Demo: https://youtu.be/8sJufBqwcac

## Description:
For the CS50 Final Project, I decided to make a website that can be used to simplify the process of keeping track with all your medical records.
Medical records can be a pain (sometimes more than the reason you ended up seeing a doctor), to track them just for yourself or for your whole family altogether. This piece of software attempts to easen this specific task and can help save time due to prior messy self-organisation.
The main webpages of this website includes a login-register page, an account/user/family management page, a page where you can add, store and easily access medical records like appointments, diagnosis, receipts, prescribed drug dosage, etc, based on type of injury/condition.

## Technologies Used:
- Flask
- Python
- Jinja
- HTML
- CSS
- Javascript
- Bootstrap
- SQL (SQLite)

## Project Structure & Details:
All files are stored in the root project directory.

### requirements.txt
Text file containing required software.

### medilog.db
Database containing 3 tables, namely, users, families and logs.
- Table users contains all the user account information (passwords are hashed first and then stored). The fields are:
    - id : unique user id (primary key)
    - username : unique username
    - password : hashed password
- Table families is used to store information about each family member.
    - user_id : user id as foreign key
    - member_id : unique id (primary key)
    - member_name
    - member_dob
    - member_gender
    - color : favourite color stored in hex format
    - health_status : 0 if healthy, 1 if unwell, 2 if critical condition
- Table logs is used to store the actual medical record in the database.
    - user_id : user id as foreign key
    - member_id : member id as foreign key
    - log_id : unique id (primary key)
    - title: log title
    - date_added
    - dofsi : date of first symptoms or injury
    - health_issue : o for ongoing, r for recovered
    - condition : s for stable, c for critical
    - diagnosed : n for no, y for yes
    - hospital_info
    - doctors
    - diagnosis_result
    - recovery_advice
    - prescription

### static
Contains 2 stylesheets, one used for the login, register pages and one used throughout the website

### templates
- #### login.html, register.html
    Simple design, login page has 2 input fields, register has 3. they both occupy the right half of the screen. The left half of the screen is supposed to be a carousel of banner images.

- #### layout.html, layoutDisabled.html
    These files contain all the header information linke links to bootrap, imported fonts, icons from google fonts and also have a navbar containing the logo and a button to access the main menu. The logo acts as a link to the homepage. The main menu option is disabled in layoutDisabled.html, nearly all other html files extend from these 2 files. The main menu is an offcanvas menu containing information about the users family (displays their name and health in terms of a smiley or a neutral or a frown with a background colour of their selected favourite colour), a button to add new family members, a button to change account settings and a button to log out.

- #### apology.html
    Page to display an error message with the help of a grumpy cat. (Provided by CS50).

- #### home.html
    The hompage is split into 3 cards, 1 main card with a short description of medilog and a button to navigate to the logs page, 1 card under it that gives you quick information about how many family members are unwell and finally the last card that contains a list of family members (4 at max) as smaller cards that displays their name, health in terms of a smiley or a neutral or a frown and the most recent log about them (if any) with a background colour of their selected favourite colour.

- #### firstMember.html, addMember.html, editMember.html
    These 3 pages are nearly identical. It contains a form in the centre of the page. A family member has a name, dob, gender and a favourite color. All fields are required.

- #### logs.html
    This page allow you to effectively search and store your medical records. All logs are shown as rectangular containers having a title and 3 action buttons.
    One button is to view the log, one button is to edit the log and one button is to delete the log. If a log is to be deleted there is always a confirmation modal that makes sure you don't accidentally delete a record. To add a log, the user can click on the big button under the last log or click on the secondary navbar header 'Logs'.

- #### createLog.html, viewLog.html, editLog.html
    These pages are nearly identical to each other. They all contain the same form. The first field is the log title, after that the patient is to be selected from a select menu which is dynamically updated. The date of first symptoms or first injury is asked, then the user is asked if the patient has recovered or not, if the condition is ongoing, the form length is increased and another a new field asking for the patient's current health status appears. The following field asks if the patient has been formally diagnosed, if yes, the form length is further increased and the user is asked information like hospital/clinic visited, name and info of doctor(s), diagnosis result, recovery advice and medical prescriptions.

- #### settings.html
    Settings page has a centred container with some stats about the user's account and displays the list of family members, with each member having a remove button. There are also buttons to reset password and to delete the account entirely. Any number of family members can be removed as long as one member is present in the family, if only one member is there in the family, the members remove button is disabled. There is always a confirmation modal to ensure no accidental removals or account deletions

- #### resetPassword.html
    A simple page asking for the existing username, new password and confirmation of new password. Similar to how the settings page looks in terms of layout.

### app.py
Contains the main code required to run the website. The list of all function/routes in app.py are:
- #### "/login" `login()`, "/register" `register()`, "/firstMember" `firstMemberForm()` and "/logout" `logout()`
    A standard login page asking for a username and a password, a password reset feature is offered if the user has forgotten their password. If a new account is to be registered, the user must fill in account details first, after verification they are redirected to a page where they must fill in the details of the first family member of the account, only then are they allowed to enter the main website. After filling in the required forms the user is redirected to the home screen. Session is cleared when the user wants to logout.

- #### "/" or `home()`
    Throughout the website there is a menu button which opens an offcanvas menu to help with website navigation.
    In the homepage, the cards containing family data are displayed by using the database, they have to be updated each time the user enters the homepage and the user should see the unwell members first and healthy members as a last priority. Bottom card also is rendered appropriately with accurate numbers.

- #### "/addMember" `addMember()` and "/editMember/:member_id" `editMemberForm(member_id)`
    The user can add family members by entering details into a form very similar to the first member form. The family database is updated accordingly. The user can also edit any family members details at any time.
    While adding or editing family members, the program does not let all data fields of one member be equal to all data fields of another family member.

- #### "/logs" `logs()`:
    In the logs page, the user can add logs and navigate through previous logs easily by using the search bar.
    Each log has 3 buttons on it, 1 to view, 1 to edit and 1 delete it.

    - "/logs/create" `logCreate()`
    - "/logs/delete/:log_id" `logDelete(log_id)`
    - "/logs/edit/:log_id" `logEdit(log_id)`
    - "/logs/view/:log_id" `logView(log_id)`

    To create a log, we need to fill in a form related to the patients health, the form fields increase/decrease based on what some form options. All fields being displayed on the screen are required.

    Viewing, editing and deleting work somewhat similarly as they all require a log ID as a url parameter. The program only allows users having the same user id according to session as the user id connected to the log via database.

- #### "/settings" `settings()`, "/delete/:user_id" `delete(user_id)` and "/deleteMember/:member_id" `deleteMember(member_id)`:
    In the settings page, the user can remove family members (removing them from the database along with any logs associated with them), reset account password or delete the whole account itself removing ALL account data from the database. The program only allows users having the same user id according to session as the user id obtained from querying the database with given id.

- #### "/reset" `reset()`:
    Asks the user to provide the username and reconfirm new password.

### helpers.py
It contains code for 2 functions, a function that displays error messages `apology()` and a wrapper function `login_required()` that checks if the user has a session token and if they have filled out the first member form while registering

## Improvements & Compromises:
Firstly, this is my first README so please bare with me if it is not upto standard or there are somethings to be desired.

Secondly, there were a lot of choices made on the fact that a working website is more important than a half made perfect one.
The deadline for this project was admittedly mismanaged by me, mainly due to me persuing 2 college degrees.

Nonetheless, I wanted to go over some unpleasant choices I made which I would like to go over. A lot of flawed design choices, some icons too big, inconsistent use of fonts, some buttons not obvious in their function, some spaces left too empty, not enough ways to navigate around the website; the list goes on.
Some features that I wanted to implement but didn't because of time issues or I just didn't know how to include a filter menu to search for logs based on specific filters, a way to star a log or mark as important, a way to store images in the database and display them as people much prefer to upload images of information than to type it all out.

Another thing that I tried but could not complete was to use Unsplash API to give me images that I could display as banners in my login and register pages.

## Contact:
If anyone even reads this and for some reason wants to contact me, here's my email: vivekra.0703@gmail.com
