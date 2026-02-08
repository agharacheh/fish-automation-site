import os
from flask import (
    Flask, render_template, request, redirect, url_for,
    Response, send_from_directory
)
from flask_babel import Babel, gettext as _, get_locale
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

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
    lang_list = request.args.getlist("lang")
    lang = lang_list[-1] if lang_list else None
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

    def set_query(url, **params):
        u = urlparse(url)
        q = parse_qs(u.query)
        for k, v in params.items():
            q[k] = [v]  # replace
        new_query = urlencode(q, doseq=True)
        return urlunparse((u.scheme, u.netloc, u.path, u.params, new_query, u.fragment))

    def lang_url(endpoint, **values):
        lang_list = request.args.getlist("lang")
        lang = (lang_list[-1] if lang_list else None) or request.cookies.get("lang") or current
        base = url_for(endpoint, **values)
        return set_query(base, lang=lang)

    return {"current_locale": current, "lang_url": lang_url}


@app.route("/setlang/<lang_code>")
def setlang(lang_code):
    if lang_code not in LANGUAGES:
        lang_code = "en"

    target = request.args.get("next") or "/"

    # If target already has ?lang=..., replace it safely
    u = urlparse(target)
    q = parse_qs(u.query)
    q["lang"] = [lang_code]
    new_query = urlencode(q, doseq=True)
    target_fixed = urlunparse((u.scheme, u.netloc, u.path, u.params, new_query, u.fragment))

    resp = redirect(target_fixed)
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
    success = False
    if request.method == "POST":
        # TODO: validate + process form (email later)
        success = True

    return render_template("contact.html", page="contact", success=success)


@app.route("/robots.txt")
def robots():
    return send_from_directory("static", "robots.txt")


# SEO routes (place here)
@app.route("/sitemap.xml")
def sitemap():
    # All public endpoints you want indexed
    endpoints = [
        "index",
        "equipment",
        "commercial",
        "automation",
        "monitoring",
        "rnd",
        "about",
        "contact",
    ]

    languages = ["en", "fa"]
    pages = []

    for lang in languages:
        for ep in endpoints:
            base = url_for(ep, _external=True)
            pages.append(f"{base}?lang={lang}")

    xml = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
    ]

    for page in pages:
        xml.append(
            f"<url>"
            f"<loc>{page}</loc>"
            f"<changefreq>monthly</changefreq>"
            f"<priority>0.8</priority>"
            f"</url>"
        )

    xml.append("</urlset>")
    return Response("\n".join(xml), mimetype="application/xml")


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

