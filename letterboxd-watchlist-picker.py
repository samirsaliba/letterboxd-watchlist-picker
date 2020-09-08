from urllib.request import urlopen
from bs4 import BeautifulSoup
from PIL import ImageTk, Image
import random
import tkinter as tk
import requests
import shutil
import threading, time
import os

class Threader(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.start()

    def run(self):
        button.config(state=tk.DISABLED)
        full_routine()
        button.config(state=tk.NORMAL)
        button.config(text="Run again")
        
def get_films_single(profile):
    url_base = "https://letterboxd.com/"
    url_watchlist = url_base + profile + "/watchlist/page/"
    films_list = []

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

        poster_container = soup.find_all('li',{'class':'poster-container'})

        for poster in poster_container:
            # get the proper film name
            img_tag = poster.find('img')
            film_name = img_tag['alt']

            # get the slug for the movie link
            films_div = poster.find("div",{"class":"film-poster"})
            film_link = films_div['data-film-slug'][len('/film/'):-1]

            film = (film_name, film_link)
            films_list.append(film)

        i+=1

    return films_list

def full_routine():
    global first_time
    global all_films, intersection_films
    global profile1, profile2
    global frame2

    if not first_time:
        for widget in frame2.winfo_children():
            widget.destroy()
    
    if(first_time or (profile1 != entry_profile1.get() or profile2 != entry_profile2.get())):
        profile1 = entry_profile1.get()
        profile2 = entry_profile2.get()
        list1 = get_films_single(profile1)
        list2 = get_films_single(profile2)

        # set() below just to make sure there are no duplicates -- since a film can be in both lists
        all_films = set(list1 + list2)
        intersection_films = [film for film in list1 if film in list2] 
        first_time=False

    # choose the film
    if(intersection_priority.get()==1):
        if intersection_films:
            # get film from intersection list
            total = tk.Label(master=frame2, text ="Total of {} different films".format(len(intersection_films)))
            film = random.choice(list(intersection_films))
        else:
            # no films in intersection, display text
            total = tk.Label(master=frame2, text ="Total of {} different films".format(len(intersection_films)))
            film = random.choice(list(all_films))
    else:
        total = tk.Label(master=frame2, text ="Total of {} different films".format(len(all_films)))
        film = random.choice(list(all_films))

    # download the poster
    get_poster(film)

    # add the second frame with the chosen film
    window.geometry("500x800")
    
    # load and display the image poster
    load = Image.open('{}.jpg'.format(film[1]))
    render = ImageTk.PhotoImage(load)
    poster = tk.Label(master=frame2, image=render)
    poster.image = render
    poster.pack()

    # display the film name and total of different films
    film_name = tk.Label(master=frame2, text=film[0])
    film_name.pack()
    total.pack()
    frame2.pack()

def get_poster(film):
    global images_downloaded
    url = "https://letterboxd.com/film/" + film[1]
    page = urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    poster_div = soup.find('div', class_='film-poster')
    
    
    poster_div = poster_div.find('img')
    img_url = poster_div['src']
    response = requests.get(img_url, stream = True)
    if response.status_code == 200:
        response.raw.decode_content = True
        filename = "{}.jpg".format(film[1])
        with open(filename,'wb') as f:
            images_downloaded.add(filename)
            shutil.copyfileobj(response.raw, f)

def clean_images():
    for file in images_downloaded:
        os.remove(file)
    exit()


# Global variables to auxiliate the proccess
all_films, intersection_films = [], []
first_time = True
profile1, profile2 = '', ''
images_downloaded = set()

# Set-up the window
window = tk.Tk()
window.title("Watchlist Picker")
window.resizable(False, False)
frame = tk.Frame(pady = 20, padx = 20)
frame2 = tk.Frame(pady = 20, padx = 20)

# Add text
title = tk.Label(text="Letterboxd Unofficial Watchlist Picker", master=frame)
title.pack()

description_txt =\
"Hello! Please input 2 different letterboxd users on each box below and the application will choose one movie\
that is one one of the users' watchlists."
description = tk.Label(text=description_txt, wraplength=200, justify='left', master=frame)
description.pack(pady=5)

# Create the entry for the second profile
entry_profile1 = tk.Entry(fg="#ff8000", bg="#333333", width=33, master=frame)
entry_profile1.pack()

entry_profile2 = tk.Entry(fg="#40bcf4", bg="#333333", width=33, master=frame)
entry_profile2.pack()

# Create the "Give priority to films in both watchlists"
intersection_priority = tk.IntVar()
check = tk.Checkbutton(master=frame, text="Give priority to films in both watchlists", variable=intersection_priority)
check.pack()

# Create the trigger button
button = tk.Button(text="Run", bg="#00e054", fg="#333333", master=frame, command= lambda: Threader(name='Start-Routine'))
button.pack(pady=5)

# Pack the frame & Run it
frame.pack()
window.protocol("WM_DELETE_WINDOW", clean_images)
window.mainloop()
