import scrapy
from scrapy.crawler import CrawlerProcess
import pandas as pd
from os.path import exists

all_certificate = pd.DataFrame(dict())
all_program = pd.DataFrame(dict())
all_pg = pd.DataFrame(dict())

class SpiderClassName(scrapy.Spider):
    name = "spider_name"

    def start_requests(self):

        file_link = exists('edureka_courses_links.csv')
        if file_link:
            d = pd.read_csv('edureka_courses_links.csv', index_col=0)
            urls = list(d['links'])
            for url in urls:
                yield scrapy.Request(url=url, callback=self.parse)
        else:
            print('please run scrap_link_edureka.py first')

    def parse(self, response):

        title = response.css('h1::text')[0].extract().strip()

        t = title.lower()

        if (t.startswith('post') or 'advanced' in t or t.startswith('pg')) and 'training' not in t:
            self.pg_courses(response, title)
        elif (t.endswith('program') or t.endswith('program course')) and 'internship' not in t:
             self.program(response, title)
        else:
            self.certificate(response, title)

    def certificate(self, response, t):
        global all_certificate
        certi = dict()
        text_under_name = response.css('div.blurb_bx div::text').extract()
        if not text_under_name:
            text_under_name = response.css('div.blurb_bx::text').extract()
            if not text_under_name:
                text_under_name = response.css('div.blurb_bx *::text').extract()
            if not text_under_name:
                text_under_name = response.css('div.videoinfo_para__24X7g div::text').extract()

                if not text_under_name:
                    text_under_name = response.css('div.videoinfo_para__24X7g::text').extract()

        certi['title'] = t
        if text_under_name:
            certi['text_under_name'] = text_under_name[0].strip()

        rating = response.css('span.cour_reviewicons').css('i.yellow').extract()
        if len(rating) == 0:
            rating = response.css('span.title_review__1ZmaN a span::text').extract()
            if rating:
                certi['rating'] = rating[0]
        else:
            certi['rating'] = len(rating)

        student_learner = response.css('span.lrner_cnt span::text').extract()
        if len(student_learner) == 0:
            student_learner = response.css('span.title_learnerscount__l2vDH::text').extract()
        if student_learner:
            certi['student_learner'] = student_learner[0]

        rev = response.css('div.videoinfo_four_bx_point_vew__W9ARl div::text').extract()
        if rev:
            for i in range(0, 8, 2):
                certi[str(rev[i + 1]).strip()] =  rev[0]


        image = response.css('div.clp-video-panel-box img::attr(src)').extract()
        if not image:
            image = response.css('div.videoinfo_video_section__2TBL7 img::attr(src)').extract()
        if image:
            certi['image_link'] = image[0]

        # Why should you take
        wst = response.css('div.take_the_course_bx span::text').extract()
        if not wst:
            wst = response.css('div.whylearning_box_view_card__3LE_i span::text').extract()
        if wst:
            certi['Why_should_you_take'] = str(wst)

        syllabus = response.css('section#Curriculum').css('div.clp-section_accord_bx')
        lesson = {}
        if syllabus:
            for s in syllabus:
                title = s.css('div.panel-heading h3::text').extract_first()
                mod = s.css('div.panel-body ul *::text').extract()
                lesson[title] = mod
        else:
            syllabus = response.css('section#curriculum').css('div.accordion div.curriculumaccordion_accordion_card__oRlNZ')
            for s in syllabus:
                title = s.css('h3::text').extract_first()
                mod = s.css('div.card-body ul *::text').extract()
                lesson[title] = mod

        certi['syllabus'] = str(lesson)
        certi = pd.DataFrame(certi, index=[0])
        all_certificate = pd.concat([all_certificate,certi],ignore_index=True)

    def program(self, response, t):
        global all_program
        pro = dict()
        text_under_name = response.css('div.mlp_desc_nw::text').extract()
        if not text_under_name:
            text_under_name = response.css('div.mlp_desc_nw div::text').extract()

        pro['title'] = t
        pro['text_under_name'] = text_under_name[0].strip()

        info = response.css('div.mast_count span::text').extract()
        course = info[0].strip()
        hours = info[1].strip()
        if len(info) > 2:
            ass_project = info[2].strip()
            pro['assessment_project'] = ass_project
        pro['course'] = course
        pro['hours'] = hours


        #Allumni_review
        allumni = response.css('div.Allumni_review')
        names = allumni.css('p.name::text').extract()
        subtitle = allumni.css('p.subtitle::text').extract()
        user_review = allumni.css('p.user_view::text').extract()
        pro['allumni_names'] = str(names)
        pro['allumni_subtitle'] = str(subtitle)
        pro['allumni_user_review'] = str(user_review)

        program_fees = response.css('span.after_discount::text').extract()
        pro['program_fees'] = program_fees[0]

        syllabus = response.css('div.top_info_sub_course')

        title_sy = syllabus.css('h3.title::text').extract()
        read_info = syllabus.css('div.read_less_info p::text').extract()
        weeks = syllabus.css('div.course_week_ps ul')
        week_data = []
        for w in weeks:
            week_data.append(w.css('li::text').extract())

        pro['syllabus_title'] = str(title_sy)
        pro['syllabus_read_info'] = str(read_info)
        pro['syllabus_weeks'] = str(week_data)

        box = response.css('div.job_outlook_info').css('div.box_item')

        if box:
            carrer_op = ''.join(box[0].css('p *::text').extract()).strip()
            salary_trend = ''.join(box[1].css('p *::text').extract()).strip()
            if len(box)>2:
                growth = ''.join(box[2].css('p *::text').extract()).strip()
                pro['growth'] = str(growth)
            pro['carrer_pportunities'] = str(carrer_op)
            pro['salary_trend'] = str(salary_trend)


        pro = pd.DataFrame(pro, index=[0])
        all_program = pd.concat([all_program, pro], ignore_index=True)


    def pg_courses(self, response, t):
        global all_pg
        pg = dict()

        text_under_name = response.css('span.desktop::text').extract()
        if text_under_name:
            pg['text_under_name'] = text_under_name[0].strip()
        else:
            text_under_name = response.css('div.sub_box *::text').extract()
            pg['text_under_name'] = '.'.join(text_under_name).strip()
        pg['title'] = t


        image = response.css('div.logo_pgp img::attr(src)').extract_first()
        pg['image_link'] = image

        info = response.css('section.Future_pgp').css('div.card-body')
        if info:
            average_salary = ''.join(info[0].css('*::text').extract()).strip()
            growth = ''.join(info[1].css('*::text').extract()).strip()
            jobs = ''.join(info[2].css('*::text').extract())

        else:
            info = response.css('section.why_box').css('div.why_bx')
            average_salary = ''.join(info[0].css('*::text').extract()).strip()
            growth = ''.join(info[1].css('*::text').extract()).strip()
            jobs = ''.join(info[2].css('*::text').extract())

        pg['average_salary']  = average_salary
        pg['growth'] = growth
        pg['jobs'] = jobs

        about = response.css('div.about_pgp_info *::text').extract()
        pg['about'] = str(about)

        apply = response.css('div.list_apply *::text').extract()
        pg['apply']  = str(apply)

        lesson = dict()
        syllabus = response.css('div.curriculum_accordion').css('div.card')
        if syllabus:
            for s in syllabus:
                title = s.css('div.card-header h2 button::text').extract_first().strip()
                mod = s.css('div.module_info li::text').extract()
                lesson[title]=mod

        else:
            syllabus = response.css('div#accordion').css('div.panel')
            for s in syllabus:
                title = s.css('div.panel-heading div.panel-title::text').extract_first().strip()
                mod = s.css('div.panel-body p::text').extract()
                lesson[title] = mod

        pg['syllabus'] = str(lesson)
        pg = pd.DataFrame(pg, index=[0])
        all_pg = pd.concat([all_pg, pg], ignore_index=True)


if __name__ == "__main__":

    process = CrawlerProcess()

    process.crawl(SpiderClassName)

    process.start()
    all_certificate.to_csv('edureka_certificate.csv')
    all_program.to_csv('edureka_program.csv')
    all_pg.to_csv('edureka_postg.csv')
    print('scrapped all links ')

