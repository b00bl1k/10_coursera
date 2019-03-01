from bs4 import BeautifulSoup
import requests


def get_courses_list(max_size=20):
    courses_url = "https://www.coursera.org/sitemap~www~courses.xml"
    try:
        response = requests.get(courses_url)
    except requests.RequestException:
        return None
    xml_doc = BeautifulSoup(response.text, "xml")
    urls = [url.loc.text for url in xml_doc.find_all('url')]
    return urls[:max_size]


def get_course_info(course_url):
    pass


def output_courses_info_to_xlsx(filepath):
    pass


def main():
    courses_urls = get_courses_list()


if __name__ == "__main__":
    main()
