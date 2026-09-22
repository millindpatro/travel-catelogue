"""
Travel Catalogue - Flask application entry point.

Routes:
    GET  /                      list + filter destinations
    GET  /add                   show "add destination" form
    POST /add                   create a new destination
    GET  /destination/<id>      detail view, with translate widget
    GET  /destination/<id>/translate?lang=xx   translate description
    POST /destination/<id>/delete   remove a destination
"""

import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from werkzeug.exceptions import HTTPException

from config import Config
import storage
import blob_storage
import translator

app = Flask(__name__)
app.config.from_object(Config)


def validate_destination_form(form) -> tuple[dict, list[str]]:
    """
    Validates raw form input for a new destination.
    Returns (cleaned_data, list_of_errors). Never raises - invalid input is
    always handled gracefully and reported back to the user.
    """
    errors = []
    name = (form.get("name") or "").strip()
    country = (form.get("country") or "").strip()
    city = (form.get("city") or "").strip()
    category = (form.get("category") or "").strip()
    description = (form.get("description") or "").strip()
    price_raw = (form.get("price") or "").strip()

    if not name:
        errors.append("Destination name is required.")
    if not country:
        errors.append("Country is required.")
    if category not in Config.CATEGORIES:
        errors.append("Please choose a valid category.")

    price = None
    if not price_raw:
        errors.append("Price is required.")
    else:
        try:
            price = float(price_raw)
            if price < 0:
                errors.append("Price cannot be negative.")
        except ValueError:
            errors.append("Price must be a number.")

    cleaned = {
        "name": name,
        "country": country,
        "city": city,
        "category": category,
        "description": description,
        "price": price if price is not None else 0,
    }
    return cleaned, errors


@app.route("/")
def index():
    filters = {
        "country": request.args.get("country", ""),
        "category": request.args.get("category", ""),
        "max_price": request.args.get("max_price", ""),
    }
    try:
        destinations = storage.list_destinations(filters)
        error = None
    except Exception as exc:  # Azure Table not reachable / misconfigured, etc.
        destinations = []
        error = f"Could not load destinations right now: {exc}"

    return render_template(
        "index.html",
        destinations=destinations,
        filters=filters,
        categories=Config.CATEGORIES,
        error=error,
    )


@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "GET":
        return render_template("add.html", categories=Config.CATEGORIES, form={})

    cleaned, errors = validate_destination_form(request.form)

    image_url = ""
    image_file = request.files.get("image")
    if image_file and image_file.filename:
        try:
            image_url = blob_storage.upload_image(image_file)
        except ValueError as exc:
            errors.append(str(exc))
        except Exception as exc:
            errors.append(f"Image upload failed: {exc}")

    if errors:
        for e in errors:
            flash(e, "error")
        return render_template("add.html", categories=Config.CATEGORIES, form=request.form)

    cleaned["image_url"] = image_url
    try:
        storage.add_destination(cleaned)
    except Exception as exc:
        flash(f"Could not save destination: {exc}", "error")
        return render_template("add.html", categories=Config.CATEGORIES, form=request.form)

    flash(f'"{cleaned["name"]}" was added to the catalogue.', "success")
    return redirect(url_for("index"))


@app.route("/destination/<row_key>")
def detail(row_key):
    destination = storage.get_destination(row_key)
    if destination is None:
        flash("That destination could not be found.", "error")
        return redirect(url_for("index"))
    return render_template(
        "detail.html", destination=destination, languages=Config.LANGUAGES
    )


@app.route("/destination/<row_key>/translate")
def translate_description(row_key):
    destination = storage.get_destination(row_key)
    if destination is None:
        flash("That destination could not be found.", "error")
        return redirect(url_for("index"))

    lang = request.args.get("lang", "")
    translated_text = None
    if lang:
        try:
            translated_text = translator.translate_text(
                destination.get("description", ""), lang
            )
        except Exception as exc:
            flash(f"Translation failed: {exc}", "error")

    return render_template(
        "detail.html",
        destination=destination,
        languages=Config.LANGUAGES,
        translated_text=translated_text,
        selected_lang=lang,
    )


@app.route("/destination/<row_key>/delete", methods=["POST"])
def delete(row_key):
    storage.delete_destination(row_key)
    flash("Destination removed.", "success")
    return redirect(url_for("index"))


@app.errorhandler(404)
def not_found(_e):
    return render_template("error.html", message="Page not found."), 404


@app.errorhandler(HTTPException)
def handle_http_exception(e):
    return render_template("error.html", message=e.description), e.code


@app.errorhandler(Exception)
def handle_unexpected_error(e):
    # Never leak a raw stack trace to the user - fail gracefully instead.
    return render_template("error.html", message="Something went wrong. Please try again."), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=False)
