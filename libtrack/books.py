from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from werkzeug.exceptions import abort
from libtrack.auth import login_required
from libtrack.db import get_db
import requests
from csv import DictReader

bp = Blueprint("books", __name__)

languages_dict = {}
with open("libtrack/data/iso-639-3_Name_Index.tab", encoding="utf-8") as f:
    reader = DictReader(f, delimiter="\t", fieldnames=["id", "name", "junk"])
    for line in reader:
        languages_dict[line["id"]] = line["name"]


@bp.route("/")
def index():
    db = get_db()
    books = db.execute("SELECT *" " FROM book b" " ORDER BY created DESC").fetchall()
    return render_template("books/index.html", books=books)


def get_book_data(isbn):
    book_url = f"https://openlibrary.org/isbn/{isbn}.json"
    api_data = requests.get(book_url).json()
    author_key = api_data["authors"][0]["key"]
    author_url = f"https://openlibrary.org/{author_key}.json"
    author_data = requests.get(author_url).json()

    book_data = {}
    book_data["isbn"] = isbn
    book_data["title"] = api_data["title"]
    book_data["publisher"] = api_data["publishers"][0]
    book_data["publish_year"] = api_data["publish_date"]
    book_data["book_lang"] = languages_dict[
        api_data["languages"][0]["key"].split("/")[-1]
    ]
    book_data["page_count"] = api_data["pagination"]
    book_data["author"] = author_data["name"]

    return book_data


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    if request.method == "POST":
        print(request.form)
        book_data = get_book_data(request.form["isbn"])
        isbn = book_data["isbn"]
        title = book_data["title"]
        author = book_data["author"]
        publisher = book_data["publisher"]
        publish_year = book_data["publish_year"]
        book_lang = book_data["book_lang"]
        purchase_loc = request.form["purchase_loc"]
        purchase_date = request.form["purchase_date"]
        book_loc = request.form["book_loc"]
        page_count = book_data["page_count"]
        error = None

        if not isbn:
            error = "ISBN is required."
        if not author:
            error = "API ERROR"
        if not title:
            error = "API ERROR"
        if not book_loc:
            error = "Book location is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO book (isbn, title, author, publisher, publish_year, book_lang, purchase_loc, purchase_date, book_loc, page_count, owner_id)"
                " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    isbn,
                    title,
                    author,
                    publisher,
                    publish_year,
                    book_lang,
                    purchase_loc,
                    purchase_date,
                    book_loc,
                    page_count,
                    g.user["id"],
                ),
            )
            db.commit()
            return redirect(url_for("books.index"))

    return render_template("books/create.html")


def get_book(id):
    book = (
        get_db()
        .execute(
            "SELECT b.id, isbn, title, author, publisher, publish_year, book_lang, purchase_loc, purchase_date, book_loc, page_count, owner_id"
            " FROM book b"
            " WHERE b.id = ?",
            (id,),
        )
        .fetchone()
    )

    if book is None:
        abort(404, f"book id {id} does not exist.")

    return book


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    book = get_book(id)

    if request.method == "POST":
        isbn = request.form["isbn"]
        title = request.form["title"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        publish_year = request.form["publish_year"]
        book_lang = request.form["book_lang"]
        purchase_loc = request.form["purchase_loc"]
        purchase_date = request.form["purchase_date"]
        book_loc = request.form["book_loc"]
        page_count = request.form["page_count"]
        owner_id = request.form["owner_id"]

        error = None
        if not isbn:
            error = "ISBN is required."
        if not author:
            error = "API ERROR"
        if not title:
            error = "API ERROR"
        if not book_loc:
            error = "Book location is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE book SET isbn = ?, title = ?, author = ?, publisher = ?, publish_year = ?, book_lang = ?, purchase_loc = ?, purchase_date = ?, book_loc = ?, page_count = ?, owner_id = ?"
                " WHERE id = ?",
                (
                    isbn,
                    title,
                    author,
                    publisher,
                    publish_year,
                    book_lang,
                    purchase_loc,
                    purchase_date,
                    book_loc,
                    page_count,
                    owner_id,
                    id,
                ),
            )
            db.commit()
            return redirect(url_for("books.index"))

    return render_template("books/update.html", book=book)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    get_book(id)
    db = get_db()
    db.execute("DELETE FROM book WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("books.index"))
