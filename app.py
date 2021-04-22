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
    anime_list = list(r.json())

    questions = int(request.args.get("n"))
    themes = []

    statuses = []
    themeTypes = []
    for i in request.args:
        if i.startswith("s"):
            statuses.append(int(i[1]))
        elif i == "op":
            themeTypes.append("OP")
        elif i == "ed":
            themeTypes.append("ED")

    while len(themes) != questions and anime_list:
        anime = random.choice(anime_list)
        anime_list.remove(anime)

        th = random.choice(anime["themes"])
        if anime["watchStatus"] in statuses:
            if "OP" in themeTypes and th["themeType"].find("OP") > -1:
                themes.append([th, [anime["name"], anime["malID"]]])
            elif "ED" in themeTypes and th["themeType"].find("ED") > -1:
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

    return render_template("play.html", video=session["options"]["video"], anime=th[1], theme=th[0], n=n,
                           qn=len(themes))


@app.route("/finish")
def finish():
    return render_template("finish.html")
