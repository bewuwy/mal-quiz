from flask import Flask, request, redirect, render_template, session, make_response
from os import environ
import requests
import random
import json


app = Flask(__name__)
app.secret_key = environ.get("secret_key")


@app.route("/")
def index():
    if "lastmode" in session:
        if session["lastmode"] == "popular":
            return redirect("/popular")
        elif session["lastmode"] == "season":
            return redirect("/season")
        else:
            return redirect("/mal")
    else:
        return redirect("/mal")


@app.route("/mal")
def mal():
    session["lastmode"] = "mal"

    user = ""
    if "user" in session and session["user"]:
        user = session["user"]

    return render_template("mal.html", user=user)


@app.route("/popular")
def popular():
    session["lastmode"] = "popular"

    return render_template("popular.html")


@app.route("/season")
def season():
    session["lastmode"] = "season"

    return render_template("season.html")


@app.route("/start")
def play():
    mode = request.args.get("mode")
    user = None
    if mode == "mal":
        user = request.args.get("user")
        if not user:
            return redirect("/")

        r = requests.get(f"https://themes.moe/api/mal/{user}")
        qTitle = f"{user} mal quiz"
    elif mode == "popular":
        r = requests.get("https://themes.moe/api/themes/popular/100")
        qTitle = "popular anime quiz"
    elif mode == "season":
        time = request.args.get("time")
        r = requests.get("https://themes.moe/api/seasons/").json()
        year = r[-1]["year"]
        seas = r[-1]["season"]

        if time == 'season':
            r = requests.get(f"https://themes.moe/api/seasons/{year}/{seas}")
            qTitle = f"{seas} {year} anime quiz"
        else:
            r = requests.get(f"https://themes.moe/api/seasons/{year}/")
            qTitle = f"{year} anime quiz"
    else:
        return redirect("/")

    anime_list = list(r.json())
    questions = int(request.args.get("n"))
    themes = []

    statuses = []
    if mode == "mal":
        statuses = request.args.to_dict(flat=False)["s"]
    themeTypes = request.args.to_dict(flat=False)
    if "type" not in themeTypes:
        return redirect("/")
    themeTypes = themeTypes["type"]

    spoiler = False
    if "spoiler" in request.args and request.args.get("spoiler") == "on":
        spoiler = True

    nsfw = False
    if "nsfw" in request.args and request.args.get("nsfw") == "on":
        nsfw = True

    while len(themes) != questions and anime_list:
        anime = random.choice(anime_list)
        anime_list.remove(anime)

        if mode != "mal" or str(anime["watchStatus"]) in statuses:
            th = random.choice(anime["themes"])
            i = [[th["themeType"], th["themeName"], th["mirror"]["mirrorURL"]],
                 [anime["name"], anime["malID"]], []]

            if th["mirror"]["notes"].lower().find("spoiler") > -1:
                if not spoiler:
                    continue
                else:
                    i[2].append("spoiler")
            if th["mirror"]["notes"].lower().find("nsfw") > -1:
                if not nsfw:
                    continue
                else:
                    i[2].append("nsfw")

            if "OP" in themeTypes and th["themeType"].find("OP") > -1:
                themes.append(i)
            elif "ED" in themeTypes and th["themeType"].find("ED") > -1:
                themes.append(i)

    resp = make_response(render_template("playstart.html", user=user, title=qTitle))

    session["user"] = user
    session["options"] = {}
    session["options"]["video"] = request.args.get("video") == "on"
    session["themes"] = json.dumps(themes)
    session["title"] = qTitle

    return resp


@app.route("/play/<n>")
def quiz(n):
    n = int(n)
    if "themes" not in session or not session["themes"]:
        return redirect("/start")

    themes = json.loads(session["themes"])

    if n >= len(themes):
        return redirect(f"/finish")

    th = themes[n]

    return render_template("play.html", video=session["options"]["video"], anime=th[1], theme=th[0], n=n,
                           qn=len(themes), warning=th[2], title=session["title"])


@app.route("/finish")
def finish():
    return render_template("finish.html")
