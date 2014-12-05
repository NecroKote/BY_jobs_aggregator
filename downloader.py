# -*- coding: utf-8 -*-
import os
from codecs import open

from parsers import jobs_tut_by, jobs_dev_by, text_cleanup
from utils.network import JobsTutBySearchBuilder, DevBySearchBuilder, download
from utils.postprocess import postprocess_remove_russian_vacancies

# Stage 1 Download and save IndexData
# constants
pages_to_load = 50
data_directory = os.path.relpath('data')
data_file = os.path.join(data_directory, 'data.cvs')


def stage1():
    '''
    Download and save header information
    '''
    # Jobs Tut By
    jtb = JobsTutBySearchBuilder().Init() \
        .AddFilter("area", "1002") \
        .AddFilter("specialization", "1.221")
    # Job Dev by
    jdb = DevBySearchBuilder().Init() \
        .AddFilter("city","4429")

    working_module = jobs_tut_by
    #working_module = jobs_dev_by
    search_starter = jtb
    #search_starter = jdb
    search_builder = JobsTutBySearchBuilder
    #search_builder = DevBySearchBuilder

    if not os.path.isdir(data_directory):
        os.mkdir(data_directory)

    # Retrieve, Parse, Store
    parser = working_module.IndexParser()
    with open(data_file, 'w+', encoding='utf-8') as w:

        ret_data = []
        # 1-100 pages
        for page in xrange(1, pages_to_load + 1):
            # form query
            paged_query = search_builder() \
                .CopyInit(url_builder=search_starter) \
                .AddFilter("page", str(page))

            # print "Page: %d (%s)" % (page, paged_query.Build())
            print "Page: %d (%s)" % (page,paged_query.Build())

            # Get data
            data = download(paged_query.Build())

            if data:
                results = parser.do_parse(data)
                if results and len(results) > 0:
                    ret_data += results
                else:
                    print "No more props expected"
                    break

        print "RAW results", len(ret_data)
        ret_data = postprocess_remove_russian_vacancies(ret_data)
        print "Cleaned results", len(ret_data)

        # Write data
        for record in ret_data:
            w.write("%s|%s|%s|%s|%s\r\n" % (
                    record['url'],
                    record['company'],
                    record['title'],
                    record['salary'],
                    record['currency']
                    )
                    )

        w.flush()

# Stage 2 Download, Parse and Index vacancies
from whoosh.fields import Schema, ID, TEXT, STORED
from whoosh.index import create_in, open_dir
from whoosh.query import Term

index_directory = os.path.relpath('index')
index_file = os.path.join(index_directory, 'data.index')


def stage2():
    # Define Scheme
    vacancy_scheme = Schema(url=ID(stored=True),
                            company=STORED,
                            title=TEXT(stored=True),
                            salary=STORED,
                            content=TEXT(stored=False),
                            body=STORED )
    # Open Index directory
    if not os.path.exists(index_directory):
        os.mkdir(index_directory)
        ix = create_in(index_directory, vacancy_scheme)
    else:
        ix = open_dir(index_directory)

    writer = ix.writer()
    searcher = ix.searcher()

    with open(data_file, 'r', encoding='utf-8') as f:
        for line in f.readlines():
            line = line[:-2]

            url, company, title, cash, currency = line.split('|')

            test = searcher.search(Term("url",url))
            if len(test)==0:

                print url
                print "-- loading"
                data = download(url)
                if not data:
                    print "E - failed to load data"
                    continue

                print "-- indexing"
                # data = data.decode('utf-8')

                # if data:
                #     with open('test.txt', 'w', encoding='utf-8') as w:
                #         w.write(data)

                if 'jobs.tut.by' in url:
                    print 'jobs.tut.by'
                    parser = jobs_tut_by.VacancyParser()
                elif 'jobs.dev.by' in url:
                    print 'jobs.dev.by'
                    parser = jobs_dev_by.VacancyParser()
                else:
                    print 'No parser for url %s' % url
                    continue
                # with open('test.txt', 'r', encoding='utf-8') as r:
                #     data = r.read()
                #     # data = data.encode('utf-8')
                #vacancy = parser.do_parse(data.encode('utf-8'))

                vacancy = parser.do_parse(data)


                # with open('C:\\test.txt', 'w+', encoding='utf-8') as w:
                #     w.write(vacancy)



                # Write data to it
                writer.add_document(url=url,
                                    company=company,
                                    title=title,
                                    salary="%s %s" % (cash,currency) if cash else "",
                                    content=text_cleanup(vacancy),
                                    body=vacancy
                                    )

    writer.commit()


# Search throu indexed vacancies
from whoosh.qparser import QueryParser
import sys

def stage3():
    ix = open_dir(index_directory)
    if not ix:
        print "No index"
        return

    parser = QueryParser("content", ix.schema)
    with ix.searcher() as searcher:

        try:
            while True:
                search_phrase = raw_input('Search phrase: ')
                if not search_phrase: continue

                search_phrase = search_phrase.decode(sys.stdin.encoding)

                myquery = parser.parse(search_phrase)
                results = searcher.search(myquery)

                if results:
                    for result in results:
                        print "%s - %s (%s)" % (result['url'],result['title'], result['company'])

                else:
                    print "No matching results"

                print "\r\n"

        except KeyboardInterrupt:
            print "\nBae..."
            return

if __name__ == '__main__':
    #stage1()
    #stage2()
    stage3()
