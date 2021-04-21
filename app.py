from flask import Flask, request, redirect, render_template, session
from os import environ
import requests
import random


app = Flask(__name__)
app.secret_key = environ.get("secret_key")


@app.route("/")
def index():
    user = ""
    if "user" in session:
        user = session["user"]

    return render_template("index.html", user=user)


@app.route("/start")
def play():
    user = request.args.get("user")
    if not user:
        return redirect("/")

    r = requests.get(f"https://themes.moe/api/mal/{user}")
    anime_list = r.json()

    questions = int(request.args.get("n")) * int(len(anime_list) > int(request.args.get("n")))
    themes = []

    statuses = []
    for i in request.args:
        if i.startswith("s"):
            statuses.append(int(i[1]))

    while len(themes) != questions:
        anime = random.choice(anime_list)

        th = random.choice(anime["themes"])
        if anime["watchStatus"] in statuses and th["themeType"].find("OP") > -1\
                and [th, [anime["name"], anime["malID"]]] not in themes:
            themes.append([th, [anime["name"], anime["malID"]]])

    session["themes"] = themes
    session["user"] = user
    session["options"] = {}
    session["options"]["video"] = request.args.get("video") == "on"

    return render_template("playstart.html", user=user)


@app.route("/play/<n>")
def quiz(n):
    n = int(n)
    if "themes" not in session or not session["themes"]:
        return redirect("/start")

    themes = session["themes"]
    if n >= len(themes):
        return redirect(f"/finish")

    th = themes[n]

    return render_template("play.html", src=th[0]["mirror"]["mirrorURL"], video=session["options"]["video"],
                           anime=th[1], songTitle=th[0]["themeName"], next=n+1)


@app.route("/finish")
def finish():
    return render_template("finish.html")
