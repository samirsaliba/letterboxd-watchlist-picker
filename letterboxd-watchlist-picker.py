from urllib.request import urlopen
from bs4 import BeautifulSoup
import random
import tkinter as tk
import requests
import shutil

def get_movies_single(profile):
    url_base = "https://letterboxd.com/"
    url_watchlist = url_base + profile + "/watchlist/page/"
    movies_list = []

    url = url_watchlist + '1/'
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    i=1
    while soup.find_all('li', class_='paginate-current') != []:

        url = url_watchlist + '{}/'.format(i)
        page = urlopen(url)
        html = page.read().decode("utf-8")
        soup = BeautifulSoup(html, "html.parser")
        films_div = soup.find_all("div",{"class":"film-poster"})
        for film in films_div:
            film_name = film['data-film-slug']
            start = len('/film/')
            film_name = film_name[start:-1]
            movies_list.append(film_name)
        i+=1

    return movies_list

def get_movies_all():
    profile1 = entry_profile1.get()
    profile2 = entry_profile2.get()
    list1 = get_movies_single(profile1)
    list2 = get_movies_single(profile2)
    choose_film(list1, list2)
    
def get_poster(movie):
    url = "https://letterboxd.com/film/" + movie + '/'
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    poster_div = soup.find('div', class_='film-poster')
    
    
    poster_div = poster_div.find('img')
    img_url = poster_div['src']
    response = requests.get(img_url, stream = True)
    if response.status_code == 200:
        response.raw.decode_content = True

        with open("{}.jpg".format(movie),'wb') as f:
            shutil.copyfileobj(response.raw, f)

def choose_film(list1, list2):
    all_movies = set(list1 + list2)
    # set() above is to make sure there are no duplicates -- since a film can be in both lists
    movie = random.choice(list(all_movies))

    window2 = tk.Toplevel(window1)
    window2.title("Result")

    get_poster(movie)

    movie_display = movie.split("-")
    movie_display = [x.capitalize() for x in movie_display]
    movie_display = ' '.join(movie_display)

    movie_img = tk.Label(window2, text=movie_display)
    movie_img.pack()
    total = tk.Label(window2, text ="Total of {} different movies".format(len(all_movies)))
    total.pack()

# Set-up the window
window1 = tk.Tk()
window1.title("Watchlist Picker")
frame = tk.Frame(pady = 10)

# Add text
title = tk.Label(text="Letterboxd Unofficial Watchlist Picker", master=frame)
title.pack()

description_txt =\
"Hello! Please input 2 different letterboxd users and the application will choose one movie \
that is in one of those two watchlists."
description = tk.Label(text=description_txt, master=frame)
description.pack()

# Create the entry for the second profile
entry_profile1 = tk.Entry(fg="#ff8000", bg="#333333", width=50, master=frame)
entry_profile1.pack()

entry_profile2 = tk.Entry(fg="#40bcf4", bg="#333333", width=50, master=frame)
entry_profile2.pack()

# Create the trigger button
button = tk.Button(text="Run", bg="#00e054", fg="#333333", master=frame, command=get_movies_all)
button.pack()

# Pack the frame & Run it
frame.pack()
window1.mainloop()
