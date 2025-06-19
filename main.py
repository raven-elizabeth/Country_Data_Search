# Please note - varying user input can produce unideal results.
# I have done my best to combat this with conditional statements, error handling and by using the REST Countries API to access the Wikivoyage API so that they always align.
# However, there may still be exceptions (please let me know if you find any!)

# Primarily, I am using the REST Countries API, which does not require an API key.
# The REST Countries API contains country-specific data.

# I am also using the Wikivoyage API to provide a little further detail about the country from the ["excerpts"] data.
# This does require an API key and making a free account with an email (you can of course use a throwaway email account for this).
# This link explains how to make an account and set up an API key: https://api.wikimedia.org/wiki/Getting_started_with_Wikimedia_APIs
# Your Wikivoyage API Key and email address go in the wiki_excerpt function (look for *********** API KEY GOES IN HERE *********** above the function)

# I am using these APIs to allow a user to search and gather key information on a country.
# They can choose to either add it to a 'travels' file if they've been before, or add to a 'wishlist' file if they would like to go in the future.


# Import modules
import requests # Must be installed via IDE or with pip install requests
import datetime
import random
from csv import DictWriter


# Create past travels table with pandas:
# Install by typing pip install pandas in the terminal (if not prompted to do so by IDE)
# Pandas makes it easier to work with data; it is ideal for data manipulation and analysis.
# I am only using pandas.DataFrame(), which sorts data into a table with rows and columns.
from pandas import DataFrame


# Global scope lists
countries_visited = []
year_visited = []
memories = []
amount_visited = []
user_wishlist = []


# Introduction
user_name = input("Hello! What's your name? ")
print(f"Welcome {user_name}!\nLooking for a new place to go? Search for country information here!")
print("Please note - if searching for somewhere in the UK, please specify 'United Kingdom' or 'GB'")
file_name = user_name.replace(" ", "_") # In case user has added their full name, convert to appropriate naming style for files by replacing spaces with _


# FUNCTIONS HERE

# Function to use url to get data and convert to json
def get_json_data(country):
    country_endpoint = f"https://restcountries.com/v3.1/name/{country}" # This is a link used to search the REST Countries API by country name
    json_data = requests.get(country_endpoint).json()
    return json_data


# Function to determine if input matches API
def validate_country(message):
    if message != {'status': 404, 'message': 'Not Found'}: # This message would mean that the REST Countries API does not have this data and helps prevent the user from searching for non-existent countries (causing errors)
        return True
    else:
        return False


# Function to obtain relevant data in a list
def get_data_tuple(list_index):
    get_name = list_index["name"]["common"]
    population = list_index["population"]

    try: # Added this due to uninhabited territories with no capital city, e.g. Heard Island and Mcdonald Island
        country_capital = list_index["capital"][0] # Using the index [0] here removes the brackets surrounding the city name
    except KeyError:
        country_capital = "N/A"
    try: # Added this due to some countries lacking a subregion in the REST Countries API, e.g. South Georgia Island
        country_region = list_index["subregion"]
    except KeyError:
        country_region = list_index["region"]

    return get_name, country_capital, country_region, population # Return tuple


# STRING SLICING: Check if first three characters of user input are "yes"
def check_for_yes(user_input):
    slice_for_yes = user_input[0:3]
    return slice_for_yes


# Ask if user wants to know the currency/languages
def currency_or_languages():
    user_choice = input("Would you like to know the currency or languages of this country? ").lower()
    return user_choice


# Here I have used enumerate to return only the currency abbreviation from the currency data
def get_currency(unknown_key_dict):
    find_abbreviation = list(enumerate(unknown_key_dict))  # Enumerate creates indexes for iterables, starting at 0 by default. In this case, list converts this to a list of the index and the key.
    abbreviation = find_abbreviation[0][1]  # Retrieve second list item, which is the key (abbreviation)
    return abbreviation


# Return abbreviations of all languages from language data - I haven't done it this way for currency because there is only one currency stored in the REST Countries API, so I do not need to loop over anything and creating a list would be redundant
def get_languages(language_dictionary):
    all_languages = []
    for key, value in language_dictionary.items():
        language = key.upper()
        all_languages.append(language)
    if len(all_languages) == 1: # Remove list brackets if only one language present in data
        return all_languages[0]
    return all_languages


# Display further information if it exists
def further_information(list_index):
    try: # Added due to uninhabited territories having no data on languages/currency, e.g. Heard Island and Mcdonald Island
        languages = list_index["languages"]
        currency = list_index["currencies"]
        which_info = currency_or_languages()
        if check_for_yes(which_info) == "yes" or which_info == "y":
            print(f"Official languages spoken: {languages}")
            print(f"Currency: {currency}")
        elif which_info == "languages":
            print(f"Languages spoken: {languages}")
        elif which_info == "currency":
            print(currency)

        language_abbreviation = get_languages(languages)
        currency_abbreviation = get_currency(currency)

    except KeyError:
        language_abbreviation = "N/A"
        currency_abbreviation = "N/A"

    return language_abbreviation, currency_abbreviation


# STRING SLICING: Slice string number to get first two characters
def slice_century(string_date):
    century = int(string_date[0:2])
    return century


# STRING SLICING: Slice string number to get last two characters
def slice_decade(string_date):
    decade = int(string_date[-2:])
    return decade


# Function to ask if user has been to country before
def user_visited():
    already_visited = input("Have you been to this country before? ")
    if check_for_yes(already_visited) == "yes" or already_visited == "y":
        return True
    else:
        return False


# Which year did user go to country before
def year_of_visit():
    which_year = input("Which year did you go? ")
    return which_year


# Determine how many times they have visited
def repeat_visits(place):
    repeat_trip = 0
    while repeat_trip <= 0:
        repeat_trip = int(input(f"Please enter the number of times you have you been to {place}: "))
    return repeat_trip


# Ask user for their favourite memory of the country
def fav_memory():
    memory = input("What is your favourite memory from visiting this country? ")
    return memory


# Add previous visits data to lists
def store_travels(index, travel_year, place):
    countries_visited.append(get_data_tuple(index)[0]) # Access first item (get_name) from function's return tuple
    year_visited.append(travel_year)
    memories.append(fav_memory())
    amount_visited.append(repeat_visits(place))


# Determine if it is possible for user to have been to the country already
def validate_year(travel_year):
    today = str(datetime.datetime.now().year)
    present_century = slice_century(today)
    present_decade = slice_decade(today)
    travel_century = slice_century(travel_year)
    travel_decade = slice_decade(travel_year)
    if travel_century > present_century or (travel_century == present_century and travel_decade > present_decade):
        print("You haven't been there yet!")
        return False
    elif (int(today) - int(travel_year)) > 117:
        print("That's impossible! The oldest person alive was born in 1908!")
        return False
    else:
        print("Added to past travels")
        return True


# Join together all functions checking if user has visited the country before
def visited_before(index, place):
    if user_visited():
        year = year_of_visit()
        if validate_year(year):
            store_travels(index, year, place)
            return True
    else:
        return False


# Ask user if they want to add country to their wishlist
def wishlist_choice():
     add_country = input("Would you like to add this country to your wishlist? ").lower()
     if check_for_yes(add_country) == "yes" or add_country == "y":
         return True
     else:
         return False


# Store wishlist data
def store_wishlist(main_data, language_data, currency_data):
    main_data.update({"Official Languages": language_data, "Currency": currency_data}) # Add to existing dictionary
    user_wishlist.append(main_data)


# Wishlist result
def wishlist(main_data, language_data, currency_data):
    if wishlist_choice():
        store_wishlist(main_data, language_data, currency_data)
        print("Added to wishlist")
    else:
        print("Not added to wishlist")


# Get quote on country from Wikipedia using Wikivoyage API  *********** API KEY GOES IN HERE ***********
def wiki_excerpt(rest_api_name):
    print("\nHere is an excerpt from Wikipedia:\n")
    url = f"https://api.wikimedia.org/core/v1/wikivoyage/en/search/page" # Searches for Wiki page
    parameters = f"q={rest_api_name}" # Searches for name of country from REST countries API rather than from user input to ensure both API results match


    # Your API key goes after Authorization: Bearer (remove the square brackets[]!)
    # Your email goes inside the brackets after User-Agent: country_search (keep the regular brackets!)
    headers = {
        "Authorization": "Bearer [REPLACE_THIS_WITH_YOUR_API_KEY]",
        "User-Agent": "country_search (YOUR_EMAIL_GOES_HERE@EMAIL.COM)"
    }


    retrieve_data = requests.get(url, headers=headers, params=parameters) # Headers contain API key, params are what we are searching for
    json_dict_data = retrieve_data.json()
    data = json_dict_data['pages'][0]['excerpt'] # Gets quote from Wiki page

    # Format quote so it is presented better
    remove_unnecessary = ['<span class="searchmatch">', "</span>", "&quot;"] # I had to use single quotes here as double quotes are required inside, '&quot;' is used in the South Korea excerpt
    for unnecessary in remove_unnecessary:
        data = data.replace(unnecessary, "")

    print(f"'...{data}...'\n") # The '...'s are there as the excerpt may start/cut off in an awkward place


# Country search function
def search_countries(country):
    index = 0
    if country == "georgia":
        index = 1  # Georgia is the second country in the list for this search in the REST Countries API, South Georgia Island would be at [0]
    elif country == "korea":
        which_one = input("North, or South? ") # Will display North Korea data at [0] if just 'Korea' typed otherwise
        if which_one.lower() == "south":
            index = 1

    rest_countries_result = get_json_data(country)
    if validate_country(rest_countries_result):
        access_dict = rest_countries_result[index]
        country_name, capital, region, population = get_data_tuple(access_dict)
        wiki_excerpt(country_name)
        country_dict = {"Country": country_name, "Capital City": capital, "Region": region, "Population": population}
        for key, value in country_dict.items(): # Prints all key value pairs in dictionary in a presentable list
            print(f"{key}: {value}")
        country_language, country_currency = further_information(access_dict)
        if not visited_before(access_dict, country_name):
            wishlist(country_dict, country_language, country_currency)

    else:
        print("Error. Please enter a country name.")


# Get user input on country of their choice
def choose_country():
    chosen_country = input("Enter a country to search for: ").lower()
    return chosen_country


# Select random country data from API
def random_choice():
    all_country_names = "https://restcountries.com/v3.1/all?fields=name"
    json_country_names = requests.get(all_country_names).json()
    get_random = random.choice(json_country_names)
    suggested_country = get_random["name"]["common"]
    print(suggested_country)
    search_countries(suggested_country)


# Check if user wants to search themselves
def user_search():
    search_choice = input("Would you like to search for a country? y/n ").lower()
    if check_for_yes(search_choice) == "yes" or search_choice == "y":
        return True
    else:
        return False


# Check if user wants a random country to be chosen
def random_search():
    suggestion = input("Would you like a suggestion? ")
    if check_for_yes(suggestion) == "yes" or suggestion == "y":
        return True
    else:
        return False


# Let user choose search method
def search_method():
    if user_search():
        search_countries(choose_country())
        return True
    elif random_search():
        random_choice()
        return True
    else:
        return False


# Create wishlist file
def create_wishlist():

    field_names = [
        "Country",
        "Capital City",
        "Region",
        "Population",
        "Official Languages",
        "Currency"
    ]

    with open(f"{file_name}_wishlist.csv", "w+") as wishlist_file: # 'with open()' closes the file automatically
        wishlist_spreadsheet = DictWriter(wishlist_file, fieldnames=field_names)
        wishlist_spreadsheet.writeheader()
        wishlist_spreadsheet.writerows(user_wishlist)


# Here, I have used pandas.DataFrame (imported just DataFrame) to make a table from the user's past travels data, then I've added the table to a separate csv file.
# You can specify your own index, but I have chosen to stick with the default.
def add_travels_with_pandas():
    with open(f"{file_name}_travels.csv", "a") as travels_file:
        travels_table = DataFrame({"Country": countries_visited, "Year Visited (most recent)": year_visited, "Times Visited": amount_visited, "Favourite Memory": memories})
        travels_table.to_csv(travels_file)


# While loop to keep searching for more countries
def continuous_search():
    keep_searching = True
    while keep_searching: # While loop for ongoing requests
        search_method()
        keep_searching = search_method()
    create_wishlist()
    add_travels_with_pandas()
    print("Thank you for using this program!")


# Main program
continuous_search()


# Notes:
# I have isolated getting user input into separate functions.
# I have put almost everything into functions just to try this out.
# I realise pandas is better for larger datasets, but I wanted to practise with it.
# In the future I would maybe look into using additional APIs with the language/currency data.
# I have added extra detailed notes in some areas - this is mostly just for me in the future to help reinforce my learning.

# I created this program early on in my learning, so I know now that it can be made more efficient. For example:
# The functions should be more aligned with Single Responsibility and could be separated into different files/classes based on their purpose.
# The API key data could be contained in a separate file.
# Some of the code is unnecessary and can be simplified/reduced.
# I would also prevent the core lists used from being on the global scope.