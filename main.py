

sites = ['jobs.tut.by', 'jobs.dev.by']
query = MetaQueryBuilder().init()\
            .AddFilter("city", "Minsk")\
            .AddFilter("level", "junior")\
            .AddFilter("salary", "500")\

for site_controler in init_data_sources(sites):
    # Get pages, parse items, store in memory
    site_controler.get_list(query, pages=100)
    # Parse and index each vacancy
    site_controler.get_details(index_storage)

