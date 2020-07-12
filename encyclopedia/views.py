import re
import random

from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from . import util

wiki_entries_directory = "entries/"


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "title": "Home",
        "heading": "All Pages"
    })


def entry_page(request, title):
    entry_contents = util.get_entry(title)
    html_entry_contents = markdown_to_html(entry_contents) if entry_contents else None

    return render(request, "encyclopedia/entry.html", {
        "body_content": html_entry_contents,
        "entry_exists": entry_contents is not None,
        "title": title if entry_contents is not None else "Error"
    })


def search(request):
    query = request.GET['q']
    if util.get_entry(query):
        # query matches a title
        return HttpResponseRedirect(reverse("entry", args=(query,)))
    else:
        # query does not match!
        return render(request, "encyclopedia/index.html", {
            "entries": [entry for entry in util.list_entries() if query.lower() in entry.lower()],
            "title": f'"{query}" search results',
            "heading": f'Search Results for "{query}"'
        })


def new_page(request):
    return render(request, "encyclopedia/new-page.html", {
        'edit_mode': False,
        'edit_page_title': '',
        'edit_page_contents': ''
    })


def save_page(request, title=None):
    if request.method == 'GET':
        return HttpResponseRedirect(reverse("index"))
    else:
        assert (request.method == 'POST')
        entry_content = request.POST['entry-content']
        if not title:
            # We are saving a new page
            title = request.POST['title']
            if title.lower() in [entry.lower() for entry in util.list_entries()]:
                return render(request, "encyclopedia/error.html", {
                    "error_title": "saving page",
                    "error_message": "An entry with that title already exists! Please change the title and try again."
                })

        filename = wiki_entries_directory + title + ".md"
        with open(filename, "w") as f:
            f.write(entry_content)
        return HttpResponseRedirect(reverse("entry", args=(title,)))


def edit_page(request, title):
    entry_contents = util.get_entry(title)
    if entry_contents is None:
        # Somebody came to a url for editing a  page that does not exist
        return HttpResponseRedirect(reverse("index"))

    return render(request, "encyclopedia/new-page.html", {
        'edit_mode': True,
        'edit_page_title': title,
        'edit_page_contents': entry_contents
    })


def markdown_to_html(markdown_string):
    if '\r' in markdown_string:
        markdown_string = markdown_string.replace('\r\n', '\n')
    assert('\r' not in markdown_string)
    unique_marker = 'PROTECTED_CHARS_fwargnmejlgnsjglsibgtnovdrsfeaijler'

    heading_matcher = re.compile(r'^(?P<hash_tags>#{1,6})\s*(?P<heading_title>.*)$', re.MULTILINE)
    heading_substituted = heading_matcher.sub(
        lambda m: rf"{unique_marker}<h{len(m.group('hash_tags'))}>{m.group('heading_title')}{unique_marker}"
                  + rf"</h{len(m.group('hash_tags'))}>", markdown_string)

    bold_matcher = re.compile(r"(\*\*|__)(?P<bolded_content>.+?)\1")
    bold_substituted = bold_matcher.sub(r"<b>\g<bolded_content></b>", heading_substituted)

    list_outside_matcher = re.compile(r"^([-*])\s+.*?(?=\n\n|\n((?!\1)[-*])\s|\Z)", re.MULTILINE | re.DOTALL)
    list_inside_matcher = re.compile(r"^([-*])\s+(?P<list_item>.*?)(?=\n[-*]\s+|\Z)", re.MULTILINE | re.DOTALL)
    list_substituted = list_outside_matcher.sub(lambda m: unique_marker + '<ul>\n'
                                                + list_inside_matcher.sub(unique_marker
                                                                          + r"<li>\g<list_item>"
                                                                          + unique_marker + "</li>", m.group())
                                                + '\n' + unique_marker + '</ul>', bold_substituted)

    link_matcher = re.compile(r"\[(?P<text>((?!\n\n).)*?)\]\((?P<link>((?!\n\n).)*?)\)", re.DOTALL)
    link_substituted = link_matcher.sub(rf'<a href="\g<link>">\g<text></a>', list_substituted)

    paragraph_matcher = re.compile(rf"^(?!{unique_marker}|\n|\Z)(?P<paragraph_text>.*?)(?=(\n\n)|{unique_marker}|\Z)",
                                   re.MULTILINE | re.DOTALL)
    paragraph_substituted = paragraph_matcher.sub(r"<p>\g<paragraph_text></p>", link_substituted)

    html_string = paragraph_substituted.replace(unique_marker, '')
    return html_string


def random_page(request):
    entry_title = random.choice(util.list_entries())
    return HttpResponseRedirect(reverse("entry", args=(entry_title,)))


if __name__ == "__main__":
    print("THIS IS NOT RUNNING")
    with open("entries/HTML.md") as handle:
        markdown_str = handle.read()
    print(markdown_str)
    print(markdown_to_html(markdown_str))
