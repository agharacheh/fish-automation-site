import os
from flask import Flask, render_template, request, redirect, url_for
from flask_babel import Babel, gettext as _, get_locale

app = Flask(__name__, template_folder="templates/active")

# -------------------------
# CONFIG
# -------------------------
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret")

LANGUAGES = ["en", "fa"]

# -------------------------
# LANGUAGE HANDLING
# -------------------------
def select_locale():
    lang = request.args.get("lang")
    if lang in LANGUAGES:
        return lang

    cookie_lang = request.cookies.get("lang")
    if cookie_lang in LANGUAGES:
        return cookie_lang

    return "en"

babel = Babel(app, locale_selector=select_locale)

@app.context_processor
def inject_globals():
    current = str(get_locale())

    def lang_url(endpoint, **values):
        lang = request.args.get("lang") or request.cookies.get("lang") or current
        values["lang"] = lang
        return url_for(endpoint, **values)

    return {
        "current_locale": current,
        "lang_url": lang_url
    }

@app.route("/setlang/<lang_code>")
def setlang(lang_code):
    if lang_code not in LANGUAGES:
        lang_code = "en"

    target = request.args.get("next") or "/"
    resp = redirect(f"{target}?lang={lang_code}")
    resp.set_cookie("lang", lang_code, max_age=60 * 60 * 24 * 30)
    return resp

# -------------------------
# ROUTES (FINAL NAV)
# -------------------------

@app.route("/")
def index():
    return render_template("index.html", page="home")

@app.route("/equipment")
def equipment():
    return render_template("equipment.html", page="equipment")

@app.route("/commercial")
def commercial():
    return render_template("commercial.html", page="commercial")

@app.route("/automation")
def automation():
    return render_template("automation.html", page="automation")

@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html", page="monitoring")

@app.route("/rnd")
def rnd():
    return render_template("rnd.html", page="rnd")

@app.route("/about")
def about():
    return render_template("about.html", page="about")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        # validate + process form
        success = True
    else:
        success = False

    return render_template(
        "contact.html",
        page="contact",
        success=success
    )

# -------------------------
# LOCAL DEV ONLY
# -------------------------
if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(debug=debug)


    
# if __name__ == "__main__":
#     app.run(debug=True)

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=10000)

