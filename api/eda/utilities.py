from flask import render_template, session

from sateda.dbconnector.mongo import MongoDB

extra = {}
extra["plotType"] = ["Line", "Scatter"]
extra["posMode"] = ["XYZ", "ENU"]
extra["clockType"] = ["Site", "Satellite"]
extra["stateField"] = ["x", "dx", "P"]
extra["preprocess"] = ["None", "Fit", "Detrend"]
extra['degree'] = ["0", "1", "2"]

def init_page(template: str) -> str:
    """
    init Generate the empty page

    :return str: HTML Code
    """
    content = []
    return render_template(template, content=content, extra=extra, exlcude=0)
