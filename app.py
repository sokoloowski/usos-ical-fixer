from flask import Flask, make_response, render_template, request
from flaskext.markdown import Markdown
from ics import Calendar
import requests
import re

app = Flask(__name__)
Markdown(app)


@app.route('/')
def help():
    with open(app.root_path + "/README.md", "r") as f:
        content = f.read()

    return render_template("main.html", content=content)


@app.route("/webcal:/<path:usos_ical_url>")
def fixer(usos_ical_url):
    # Fetch original iCal
    r = requests.get(f"http://{usos_ical_url}", params={
        "lang": request.args.get("lang"),
        "user_id": request.args.get("user_id"),
        "key": request.args.get("key")
    })

    c = Calendar(r.text)
    for e in c.events:
        # Fix timezone in imported iCal
        e.begin = e.begin.replace(tzinfo="Europe/Warsaw")
        e.end = e.end.replace(tzinfo="Europe/Warsaw")

        # Replace address with building and room number from description
        e.location = re.sub(r"Sala: (.+)\n(.+)\n\n.+\n",
                            r"\g<2> \g<1>",
                            e.description)

        # Leave only URL to USOS
        e.description = re.sub(r"Sala: .+\n.+\n\n(.+)",
                               r"\g<1>",
                               e.description)

    # Serialize modified calendar to iCal and return with original Content-Type header
    res = make_response(c.serialize())
    res.headers["Content-Type"] = r.headers["Content-Type"]

    return res


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8100, debug=False, threaded=True)
