from flask import Flask, request, redirect, render_template, session
from os import environ
import requests
import random


app = Flask(__name__)
app.secret_key = environ.get("secret_key")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/play")
def play():
    user = request.args.get("user")
    if not user:
        return redirect("/")

    r = requests.get(f"https://themes.moe/api/mal/{user}")
    anime_list = r.json()

    questions = int(request.args.get("n")) * int(len(anime_list) > 10)
    themes = []
    while len(themes) != questions:
        anime = random.choice(anime_list)

        th = random.choice(anime["themes"])
        if anime["watchStatus"] != 6 and th["themeType"].find("OP") > -1\
                and [th, [anime["name"], anime["malID"]]] not in themes:
            themes.append([th, [anime["name"], anime["malID"]]])

    session["themes"] = themes
    session["options"] = {}
    session["options"]["video"] = request.args.get("video") == "on"

    return render_template("playstart.html")


@app.route("/play/<n>")
def quiz(n):
    n = int(n)
    if "themes" not in session or not session["themes"]:
        return redirect("/play")

    themes = session["themes"]
    if n >= len(themes):
        return redirect(f"/play/{len(themes)-1}")

    th = themes[n]

    return render_template("play.html", src=th[0]["mirror"]["mirrorURL"], video=session["options"]["video"],
                           animeTitle=th[1][0], songTitle=th[0]["themeName"], next=n+1)
