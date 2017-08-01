# The MIT License (MIT)
# Copyright (c) 2014-2017 University of Bristol
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

from flask import Flask, send_file, render_template
from flask_bower import Bower
import pandas as pd
from StringIO import StringIO
import seaborn as sns
import base64
from bokeh.embed import components
from bokeh.resources import INLINE
from bokeh.util.string import encode_utf8
from bokeh.charts import Bar
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


app = Flask(__name__)
Bower(app)

app.config.update(
    DEBUG=True,
    TEMPLATES_AUTO_RELOAD=True
)

# Load the data into pandas
df = pd.read_csv("mn-budget-detail-2014.csv")
df = df.sort_values('amount', ascending=False)
sizes = df.groupby('category').size()


# Turn off cache
@app.after_request
def apply_caching(response):
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response


@app.route("/")
def index():
    bar = Bar(df, 'category', filename="bar.html", title="MN Capital Budget - 2014", legend=False)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    script, div = components(bar)
    html = render_template(
        'index.html',
        plot_script=script,
        plot_div=div,
        js_resources=js_resources,
        css_resources=css_resources
    )
    return encode_utf8(html)


@app.route('/figures/seaborn.png')
def test():

    img = StringIO()
    sns.set_style("dark")

    # fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    bar_plot = sns.barplot(y=sizes.index.values, x=sizes.values,
                           palette="muted", order=sizes.index.values.tolist())
    # plt.xticks(rotation=45)
    fig = bar_plot.get_figure()
    fig.tight_layout()

    fig.savefig(img, format='png')
    img.seek(0)

    return send_file(img, mimetype='image/png')


@app.route("/data")
def get_data():
    return df.to_json(orient='records')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
