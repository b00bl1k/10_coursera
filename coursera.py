import json
import random
import sys
from datetime import datetime
from bs4 import BeautifulSoup
from openpyxl import Workbook
import requests

COURSES_MAX = 20


def fetch_page(url):
    try:
        return requests.get(url).text
    except requests.RequestException:
        return None


def get_ld_by_type(ld, datatype):
    return list(filter(lambda course: course["@type"] == datatype, ld))[0]


def get_courses_list(max_size=20):
    courses_url = "https://www.coursera.org/sitemap~www~courses.xml"
    page_text = fetch_page(courses_url)
    if page_text:
        xml_doc = BeautifulSoup(page_text, "xml")
        urls = [url.loc.text for url in xml_doc.find_all('url')]
        random.shuffle(urls)
        return urls[:max_size]


def get_course_start_date(linked_data):
    try:
        start_date = linked_data["hasCourseInstance"]["startDate"]
        return datetime.strptime(start_date, "%Y-%m-%d")
    except KeyError:
        return None


def get_course_end_date(linked_data):
    try:
        end_date = linked_data["hasCourseInstance"]["endDate"]
        return datetime.strptime(end_date, "%Y-%m-%d")
    except KeyError:
        return None


def get_product_avg_rating(linked_data):
    try:
        return linked_data["aggregateRating"]["ratingValue"]
    except KeyError:
        return None


def get_course_info(page_content):
    page = BeautifulSoup(page_content, 'html.parser')
    script_tag = page.find("script", type="application/ld+json")
    linked_data = json.loads(script_tag.contents[0])
    course_linked_data = get_ld_by_type(linked_data["@graph"], "Course")
    product_linked_data = get_ld_by_type(linked_data["@graph"], "Product")

    title = course_linked_data["name"]
    lang = course_linked_data["inLanguage"]
    start_date = get_course_start_date(course_linked_data)
    end_date = get_course_end_date(course_linked_data)
    if start_date and end_date:
        weeks = round((end_date - start_date).days / 7)
    else:
        weeks = None
    avg_rating = get_product_avg_rating(product_linked_data)

    return {
        "title": title,
        "lang": lang,
        "start_date": start_date,
        "weeks": weeks,
        "avg_rating": avg_rating
    }


def output_courses_info_to_xlsx(courses, filepath):
    workbook = Workbook()
    worksheet = workbook.active
    worksheet.append([
        "Title",
        "Language",
        "Start Date",
        "Weeks",
        "Average rating"
    ])
    for course in courses:
        worksheet.append([
            course["title"],
            course["lang"],
            course["start_date"],
            course["weeks"],
            course["avg_rating"]
        ])
    workbook.save(filepath)


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python coursera.py <output>")
    else:
        filepath = sys.argv[1]
    courses_urls = get_courses_list(COURSES_MAX)
    courses_info = []
    for course_url in courses_urls:
        course_page = fetch_page(course_url)
        course_info = get_course_info(course_page)
        courses_info.append(course_info)
        output_courses_info_to_xlsx(courses_info, filepath)


if __name__ == "__main__":
    main()
