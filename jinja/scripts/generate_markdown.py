"""
This script takes one or more YAML configuration files and generates a publication-ready
markdown files designed for jupyter-book. It specializes in building pages with
plotly charts, including dataset "At a Glance" pages.

Place a .yaml file for each page you'd like to create in the ./jinja/pages/ directory.
Fill out that YAML file with the following fields:
    template: String. Path to a jinja template file, e.g., ./jinja/templates/at_a_glance_template.md.j2
    output: String. Path to an output file, e.g., "./01_at_a_glance.md"
    description: String. Markdown text to appear at the top of the page. This must follow whichever version of markdown is used by jupyter-book.
    total_records: String. Number of records in the dataset. This is used by the at_a_glance_template.md.j2 template and will be ignored otherwise.
    total_size: String. Numerical size of dataset (e.g., "2.1"). This is used by the at_a_glance_template.md.j2 template and will be ignored otherwise.
    total_size_unit: String. Unit of size (e.g., "GB"). This is used by the at_a_glance_template.md.j2 template and will be ignored otherwise.
    has_metadata: Boolean. Whether this dataset has metadata. This is used by the at_a_glance_template.md.j2 template and will be ignored otherwise.
    has_images: like has_metadata
    has_transcriptions: like has_metadata
    has_audio: like has_metadata
    has_video: like has_metadata
    has_webarchives: like has_metadata
    is_dehydrated: Boolean. Whether this dataset has URL pointers to images/transcripts/audio/video/web archives for download, but does not itself contain those media files.
    dehydrated_types: String. List of the types of dehydrated content, e.g., "images" or "images and audio". This will appear on the "At a Glance" page in the label: "Points to [dehydrated_types]" if `is_dehydrated` is True.
    charts: A nested list of charts you'd like to appear on your page. Your template must include "{{ charts }}" for this to be used. Example list:
    - title: "How many documents are in each Campaign?"
        type: bar_horizontal
        chart_data: ./jinja/data/btp-agg-bar-h-document-count-by-campaign.csv
        height: 1200
    - title: "How many terms do documents contain?"
        type: bar_vertical
        chart_data: ./jinja/data/btp_agg_vbar_terms_per_doc.csv
        height: 380


For charts to appear in your output markdown files, you must:
1. Populate the "charts" list in the YAML file for each page.  Each chart is a dictionary with:
    - title - the title of the chart
    - type - the type of chart. this is a controlled list that currently only allows "bar_horizontal" or "bar_vertical"
    - chart_data - path to the CSV file with data for the chart
    - height - height, in pixels, of the figure
2. Your Jinja template(s) much include "{{ charts }}" in the place you would like the charts to appear
3. For each chart, place a CSV file in the ./jinja/data/ directory. The YAML file should point each
    chart to its corresponding data file. The columns in the file should be:
    - Column 1: y-axis, or categories for a pie chart
    - Column 2: x-axis, or numbers for a pie chart
    - Column 3: Optional, this will be text used when hovering rather than the default.

"""

import os

import plac
import yaml
from jinja2 import Environment, FileSystemLoader

from plotlyfig import make_bar


def make_chart_title(title: str) -> str:
    """
    Generate markdown title, e.g.:

    ### My title

    """
    if title is not None:
        title_html = f"\n\n### {title}\n\n"
        return title_html


def make_chart_subtitle(subtitle: str) -> str:
    """
    Generate markdown title, e.g.:

    My subtitle

    """
    if subtitle is not None:
        subtitle_html = f"\n\n{subtitle}\n\n"
        return subtitle_html
    else:
        return ""


def make_chart(chart_yaml: dict, chart_num: int) -> str:
    """
    This function is run on each chart listed in a given page's YAML file.
    Based on the chart type specified there, it constructs the HTML for a plotly chart
    and title markdown.

    Returns markdown (including HTML) for the plotly chart, to be inserted into a jinja
    template.

    Inputs:
    chart_yaml (dict) - Dictionary of configurations for a given chart, from a
        page's YAML file. Needs to include 'type'. In the YAML file, this might look like:
            - title: "What are the top 20 words?"
                subtitle: "Excluding [stop words](https://github.com/explosion/spaCy/blob/master/spacy/lang/en/stop_words.py)"
                type: bar_horizontal
                chart_data: ./jinja/data/btp_agg_bar_h_top_20_terms.csv
                width:
                height: 780

    chart_num (i) - Integer, used to construct a unique html ID for the containing div
    """
    if chart_yaml.get("type") == "bar_horizontal":
        chart_html = make_bar(chart_yaml, chart_num, orientation="h")
    elif chart_yaml.get("type") == "bar_vertical":
        chart_html = make_bar(chart_yaml, chart_num, orientation="v")
    else:
        raise ValueError(
            f"Chart type ({chart_yaml.get('type')}) is not an allowed type. Chart: {chart_yaml.get('title')}"
        )
    chart_title = chart_yaml.get("title")
    chart_html_accssbl = chart_accssblty_wrapper(chart_html, chart_title)
    aria_label = chart_yaml.get("aria-label", "")
    accssblty_link = make_accssblty_lnk(
        chart_yaml.get("chart_data"), aria_label, chart_title
    )
    title_md = make_chart_title(chart_title)
    subtitle_md = make_chart_subtitle(chart_yaml.get("subtitle"))
    return title_md + subtitle_md + accssblty_link + chart_html_accssbl


def chart_accssblty_wrapper(chart_html, title):
    """
    Wraps the output of plotlyfig in a div designed for screenreaders.
    """
    aria_describedby = title.lower().replace(" ", "-").replace("?", "")
    return (
        '<div class="chart-accessibility-wrapper" aria-hidden="true" role="figure" '
        f'aria-label="Chart titled {title}" aria-describedby="{aria_describedby}">'
        f"{chart_html}</div>"
    )


def make_accssblty_lnk(url, aria_label, title):
    """
    Creates a hyper link to a chart's CSV file, for the purposes of accessibility.
    """
    id = title.lower().replace(" ", "-").replace("?", "")
    return f'<p class="chart-data"><a id={id} href={url} aria-label="{aria_label}">chart data (CSV)</a></p>'


def populate_template(template, page_yaml: dict, charts_md: str) -> str:
    """
    Function to add text, metadata, and charts from a page's YAML file into
    a jinja template.

    Inputs
    template (jinja2.environment.Template) - Jinja temmplate
    page_yaml (dict) - Dictionary of configurations for the page, pulled from
        a YAML file
    charts_md (str) - Markdown string for all charts and their titles. Can
        contain HTML. Should confirm to markdown flavor used by jupyter-book.

    """
    output_md = template.render(**page_yaml, charts_html=charts_md)
    return output_md


def generate_page(yaml_path):
    # Load YAML file
    with open(yaml_path) as f:
        page_settings = yaml.safe_load(f)

    # Confirm that selected keys are in the YAML file
    template_path = page_settings.get("template")
    if template_path is None:
        raise ValueError(f"{yaml_path} is missing the 'template' field.")

    output = page_settings.get("output")
    if output is None:
        raise ValueError(f"{yaml_path} is missing the 'target' field.")

    # Setup Jinja2 environment pointing to templates file
    env = Environment(loader=FileSystemLoader("."))
    template_path = env.get_template(template_path)

    # Generate the list of charts to make (if applicable)
    charts = page_settings.get("charts", [])

    # Make charts
    charts_list = []
    for i, chart_config in enumerate(charts):
        chart_md = make_chart(chart_config, i)
        charts_list.append(chart_md)

    # Append "Chart" header to Markdown
    if len(charts) > 0:
        charts_md_str = "\n## Charts \n\n"
    else:
        charts_md_str = ""
    for chart in charts_list:
        charts_md_str = charts_md_str + chart

    # Insert content into template
    output_md = populate_template(template_path, page_settings, charts_md_str)

    # Save output
    with open(output, "w") as f:
        f.write(output_md)


def generate_pages(
    yaml_dir: ("Path to directory with YAML files", "option", "y") = r"jinja/pages/",
):
    for filename in os.listdir(yaml_dir):
        if filename.endswith((".yaml", ".yml")):
            yaml_path = os.path.join(yaml_dir, filename)
            generate_page(yaml_path)


if __name__ == "__main__":
    plac.call(generate_pages)
