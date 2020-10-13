from bs4 import BeautifulSoup
import requests


class Film:
    def __init__(self, title, year_released, genre, runtime):
        self.title = title
        self.year_released = year_released
        self.genre = genre
        self.runtime = runtime


def create_url_dict():
    dictionary = {}
    az_page = requests.get('https://www.finder.com/a-z-of-international-netflix-tv-and-movie-lists').text
    az_soup = BeautifulSoup(az_page, 'lxml')
    for i in az_soup.body.find_all('tr'):
        links = i.find_all('a')
        for link in links:
            if 'movies' in str(link):
                dictionary[i.td.text] = link['href']
    dictionary['United Kingdom'] = 'https://www.finder.com/uk/netflix-movies'
    return dictionary


def handle_user_request():
    country_number_dict = {i: country for i, country in enumerate(url_dict, 1)}
    print("Welcome to international Netflix Comparison! We have film listings for the following countries:\n")
    for key, value in country_number_dict.items():
        print(key, value)
    print("\nPlease enter the numbers of the two countries you would like to compare, separated by a whitespace.")
    return [country_number_dict[int(i)] for i in input().split()]


def get_film_data(country):
    source = requests.get(url_dict[country]).text
    soup = BeautifulSoup(source, 'lxml')
    titles = [i.text for i in soup.find_all('td', attrs={"data-title": "Title"})]
    years_of_release = [i.text for i in soup.find_all('td', attrs={"data-title": "Year of release"})]
    genres = [i.text for i in soup.find_all('td', attrs={"data-title": "Genres"})]
    runtimes = [i.text for i in soup.find_all('td', attrs={"data-title": "Runtime (mins)"})]

    return [Film(titles[i], years_of_release[i], genres[i], runtimes[i]) for i in range(len(titles))]


def get_combined_list(list_a, list_b):
    return [film for film in list_a if (film.title, film.year_released) in  # Compares lists
            [(film.title, film.year_released) for film in list_b]]


def filter_genres():
    genres = list(set([film.genre for film in combined_list]))
    genres.sort()
    print("The following genres are on your list:\n")
    for i, genre in enumerate(genres, 1):
        print(f"{i}.) {genre} -- {[film.genre for film in combined_list].count(genre)} results.")

    print("\nTo remove genres from your list enter 'remove' followed by the number of the genres you would like to "
          "remove, each separated by whitespace.\nTo specify the genres you would like to see enter 'select' followed "
          "by the associated number.")

    while True:
        filter_command = input().split()

        if filter_command[0] == "remove":
            rejected_genres = [genres[int(i) - 1] for i in filter_command[1:]]
            return [film for film in combined_list if film.genre not in rejected_genres]
        elif filter_command[0] == "select":
            selected_genres = [genres[int(i) - 1] for i in filter_command[1:]]
            return [film for film in combined_list if film.genre in selected_genres]
        else:
            print("Command not recognised.")


def display_results():
    global combined_list
    i = 0
    while True:
        for film in combined_list[i: i + 20]:
            print(f"{combined_list.index(film) + 1}.) {film.title} ({film.year_released}) -- Genre: {film.genre} "
                  f"-- Runtime: {film.runtime} minutes")

        print()
        command = input("Please enter 'next' or 'previous' to cycle through results. "
                        "Enter a letter to search alphabetically. If you would like to filter by genre "
                        "\nenter 'filter'. To exit enter 'exit': ")
        print()

        if command == "next":
            i += 20
        elif command == "previous":
            i -= 20
        elif len(command) == 1 and command.isalpha():
            i = [film.title[0] for film in combined_list].index(command.upper())
        elif command == "filter":
            combined_list = get_combined_list(country_a_films, country_b_films)
            combined_list = filter_genres()
            i = 0
        elif command == "exit":
            break
        else:
            print("\nCommand not recognised")


url_dict = create_url_dict()  # Scrape list of available countries from source

while True:
    country_a, country_b = handle_user_request()  # User selects countries to compare
    country_a_films, country_b_films = [get_film_data(c) for c in [country_a, country_b]]  # Scrapes film data
    combined_list = get_combined_list(country_a_films, country_b_films)  # Compares lists
    if len(combined_list) == 0:
        "We're sorry. There are no films shared by both countries."
    else:
        break

print(f"Netflix {country_a} has {len(country_a_films)} films. Netflix {country_b} has {len(country_b_films)} films.\n"
      f"\nWe have found {len(combined_list)} films on both Netflix {country_b} and Netflix {country_a}!\n")

if input("Would you like to filter by genre? ") == "yes":
    print()
    combined_list = filter_genres()
    print(f"After filtering there are {len(combined_list)} films remaining on your list.\n")

display_results()
