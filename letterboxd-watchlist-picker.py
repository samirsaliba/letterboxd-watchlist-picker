import urllib.request
from bs4 import BeautifulSoup
from PIL import ImageTk, Image
import random
import tkinter as tk
import requests
import shutil
import threading, time
import os
import webbrowser
import io

class Threader(threading.Thread):
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)
        self.daemon = True
        self.start()

    def run(self):
        button.config(state=tk.DISABLED)
        button.config(text="Running...", cursor='wait')
        full_routine()
        button.config(state=tk.NORMAL)
        button.config(text="Run again", cursor='arrow')
        
def get_films_single(profile):
    url_base = "https://letterboxd.com/"
    url_watchlist = url_base + profile + "/watchlist/page/"
    films_list = []

    url = url_watchlist + '1/'
    page = urllib.request.urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    i=1
    while soup.find_all('li', class_='paginate-current') != []:

        url = url_watchlist + '{}/'.format(i)
        page = urllib.request.urlopen(url)
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

def get_film_details(film):
    url = "https://letterboxd.com/film/" + film[1]
    page = urllib.request.urlopen(url)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")
    
    # getting the film poster
    poster_div = soup.find('div', class_='film-poster')
    poster_div = poster_div.find('img')
    poster_url = poster_div['src']
    
    # getting the rating
    rating = soup.find(attrs={"name": "twitter:data2"})['content']

    # header for requesting website data
    hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
       'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
       'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
       'Accept-Encoding': 'none',
       'Accept-Language': 'en-US,en;q=0.8',
       'Connection': 'keep-alive'}

    req = urllib.request.Request(poster_url, headers=hdr)

    # getting the image
    raw_data = urllib.request.urlopen(req).read()
    im = Image.open(io.BytesIO(raw_data))
    image = ImageTk.PhotoImage(im)
    
    return image, rating, url

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
            film = random.choice(list(intersection_films))
        else:
            # no films in intersection, display text
            film = random.choice(list(all_films))
    else:
        film = random.choice(list(all_films))

    # download the poster
    img, rating, url = get_film_details(film)

    # add the second frame with the chosen film
    window.geometry("500x800")
    
    # load and display the image poster
    poster = tk.Label(master=frame2, image=img)
    poster.image = img
    poster.pack()

    # display the film name hyperlink
    link1 = tk.Label(frame2, text=film[0], fg="blue", cursor="hand2")
    link1.pack()
    link1.bind("<Button-1>", lambda e: webbrowser.open_new(url))

    # display the rating
    rating_label = tk.Label(master=frame2, text=rating)
    rating_label.pack()

    # display the total of different films
    total_label = tk.Label(master=frame2, text ="Total of {} different films on at least one of the watchlists.".format(len(all_films)))
    total_label.pack()

    intersection_label = tk.Label(master=frame2, text ="{} films on both watchlists.".format(len(intersection_films)))
    intersection_label.pack()
    
    frame2.pack()

# Global variables to auxiliate the proccess
all_films, intersection_films = [], []
first_time = True
profile1, profile2 = '', ''

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
button = tk.Button(text="Run", bg="#00e054", fg="#333333", master=frame, cursor="hand2", command= lambda: Threader(name='Start-Routine'))
button.pack(pady=5)

# Pack the frame & Run it
frame.pack()
window.mainloop()
