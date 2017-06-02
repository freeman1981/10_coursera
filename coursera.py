import argparse
import requests
from lxml import etree
from collections import namedtuple
from bs4 import BeautifulSoup
from openpyxl import Workbook
import random


CourseData = namedtuple('CourseData', 'title,language,resent_date,count_weeks,rating')


def get_courses_urls_list(output_list_size):
    url = 'https://www.coursera.org/sitemap~www~courses.xml'
    response = requests.get(url)
    tree = etree.fromstring(response.content)
    all_courses_urls_list = tree.xpath(
        '//ns:url/ns:loc/text()', namespaces={'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'})
    return random.sample(all_courses_urls_list, output_list_size)


def get_course_info(course_slug):
    response = requests.get(course_slug)
    soup = BeautifulSoup(response.content, 'lxml')
    basic_info_table = soup.find(
        'table',
        attrs={
            'class': 'basic-info-table bt3-table bt3-table-striped bt3-table-bordered bt3-table-responsive'
        }
    )
    table_body = basic_info_table.next
    rating_node = soup.find('div', attrs={'class': 'ratings-text bt3-hidden-xs'})
    return CourseData(
        title=soup.find('h1', attrs={'class': 'title display-3-text'}).text,
        language=soup.find('div', attrs={'class': 'rc-Language'}).text,
        resent_date=soup.find(
            'div', attrs={'class': 'startdate rc-StartDateString caption-text'}).find('span').text,
        count_weeks=_get_text_from_basic_info_table(table_body, 'Commitment'),
        rating=rating_node.text if rating_node is not None else '',
    )


def _get_text_from_basic_info_table(table_element, row_name):
    # Не совсем понятно как иметь обратную связь с Евгением,
    # Илью нашел для прямых сообщений)
    # - непонятно как можно здесь использовать list comprehension
    for row in table_element.find_all('tr'):
        if row.find_all('td')[0].text == row_name:
            return row.find_all('td')[-1].text
    else:
        return ''


def output_courses_info_to_xlsx(file_path, curses_urls_list, class_namedtuple):
    work_book = Workbook()
    work_sheet = work_book.active
    work_sheet.append(class_namedtuple._fields)
    for course_url in curses_urls_list:
        course_info = get_course_info(course_url)
        work_sheet.append(course_info)
    work_book.save(file_path)


def get_args():
    parser = argparse.ArgumentParser(description='Get info from coursera')
    parser.add_argument('path', type=str, help='Path to file. It is better to use xlsx extention.')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    file_path = args.path
    size = 20
    courses_urls_list = get_courses_urls_list(size)
    output_courses_info_to_xlsx(file_path, courses_urls_list, CourseData)
