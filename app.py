import os
from flask import send_from_directory
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_babel import Babel, gettext as _, get_locale

app = Flask(__name__)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev-secret-key")




BASE_DIR = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"pdf", "png", "jpg", "jpeg", "dwg", "dxf"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

LANGUAGES = ["en", "fa"]



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

    # Detect current path safely:
    current_path = request.args.get("next") or request.path

    # If coming from homepage button OR another page:
    # Use HTTP Referer if available
    ref = request.headers.get("Referer")
    if ref:
        from urllib.parse import urlparse
        parsed = urlparse(ref)
        current_path = parsed.path

    # Build new URL with ?lang=
    target = f"{current_path}?lang={lang_code}"

    # Prepare response
    resp = redirect(target)
    resp.set_cookie("lang", lang_code, max_age=60*60*24*30)

    return resp

@app.route("/")
def index():
    return render_template("index.html", page="home")

@app.route("/process")
def process():
    return render_template("process.html", page="process")


@app.route("/automation")
def automation():
    return render_template("automation.html", page="automation")


@app.route("/monitoring")
def monitoring():
    return render_template("monitoring.html", page="monitoring")


@app.route("/contact")
def contact():
    success = request.args.get("success")
    return render_template(
        "contact.html",
        page="contact",
        success=success
    )

@app.route("/contact/submit", methods=["POST"])
def contact_submit():
    name = request.form.get("name")
    email = request.form.get("email")
    message = request.form.get("message")

    print("New Contact Message:")
    print("Name:", name)
    print("Email:", email)
    print("Message:", message)

    # Preserve current language safely
    lang = request.args.get("lang") or request.cookies.get("lang") or "en"

    return redirect(url_for("contact", lang=lang, success=1))


@app.route("/process-diagram")
def process_diagram():
    return render_template("process_diagram.html", page="diagram")


@app.route("/scada")
def scada():
    return render_template("scada.html", page="scada")


@app.route("/upload-drawings", methods=["GET", "POST"])
def upload_drawings():
    message = None

    if request.method == "POST":
        file = request.files.get("drawing")

        if not file or file.filename == "":
            message = _("No file selected.")
        elif allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            message = _("File uploaded successfully.")
        else:
            message = _("Invalid file type.")

    files = [
    f for f in os.listdir(app.config["UPLOAD_FOLDER"])
    if os.path.isfile(os.path.join(app.config["UPLOAD_FOLDER"], f))
    ]

    # files = sorted(os.listdir(app.config["UPLOAD_FOLDER"]))

    return render_template(
        "upload_drawings.html",
        message=message,
        files=files
    )

@app.route("/delete/<filename>", methods=["POST"])
def delete_file(filename):
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(_("File deleted successfully."), "success")
    else:
        flash(_("File not found."), "error")

    return redirect(url_for("upload_drawings", lang=get_locale()))



@app.route("/download/<filename>")
def download_file(filename):
    return send_from_directory(
        app.config["UPLOAD_FOLDER"],
        filename,
        as_attachment=True
    )


# if __name__ == "__main__":
#     app.run(debug=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

