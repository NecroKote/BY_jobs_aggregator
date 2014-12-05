def postprocess_remove_russian_vacancies(data):
    for item in data:
        if item['currency'] and item['currency'] == 'RUR':
            data.remove(item)
    return data
