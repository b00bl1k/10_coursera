import json
from bs4 import BeautifulSoup
import requests


def fetch_page(url):
    try:
        return requests.get(url).text
    except requests.RequestException:
        return None


def get_courses_list(max_size=20):
    courses_url = "https://www.coursera.org/sitemap~www~courses.xml"
    page_text = fetch_page(courses_url)
    if page_text:
        xml_doc = BeautifulSoup(page_text, "xml")
        urls = [url.loc.text for url in xml_doc.find_all('url')]
        return urls[:max_size]


def get_course_info(page_content):
    page = BeautifulSoup(page_content, 'html.parser')
    script_tag = page.find("script", type="application/ld+json")
    if script_tag:
        linked_data = json.loads(script_tag.contents[0])
        course_linked_data = list(filter(
            lambda course: course["@type"] == "Course",
            linked_data["@graph"]
        ))[0]
    else:
        course_linked_data = None

    name = course_linked_data["name"]
    lang = course_linked_data["inLanguage"]
    start_date = course_linked_data["hasCourseInstance"]["startDate"]
    end_date = course_linked_data["hasCourseInstance"]["endDate"]


def output_courses_info_to_xlsx(filepath):
    pass


def main():
    courses_urls = get_courses_list(20)
    for course_url in courses_urls:
        course_page = fetch_page(course_url)
        get_course_info(course_page)


if __name__ == "__main__":
    main()
