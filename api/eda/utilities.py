from flask import render_template, session

from sateda.dbconnector.mongo import MongoDB

extra = {}
extra['plotType'] = ["Scatter", "Line"]
extra['posMode'] = ["XYZ", "NEU"]


def init_page(template: str) -> str:
    """
    init Generate the empty page 

    :return str: HTML Code
    """
    connect_db_ip = session["mongo_ip"]
    db_name = session["mongo_db"]
    db_port = session["mongo_port"]
    print(connect_db_ip, db_name)
    with MongoDB(url=connect_db_ip, port=db_port, data_base=db_name) as client:
        client.get_content()
        content = client.mongo_content
    return render_template(template, content=content, extra=extra, exlcude=0)