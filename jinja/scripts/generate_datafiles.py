"""
This script creates CSV data files to make Plotly charts, for aggregated
By the People Comprehensive Transcription Data Package. It uses the dataset's aggregated CSV
as input, with each row a transcribed document
"""

import ast
import re
from itertools import chain

import numpy as np
import pandas as pd
import plac
import spacy


def count_unique(tokens):
    unique_tokens = [token.lower() for token in tokens]
    return len(set(unique_tokens))


def count_unique_column(series: pd.Series):
    term_counter = len(set(chain.from_iterable(series)))
    return term_counter


def lemmanize_text(text, nlp):
    """Return a list of lemma roots, lower case"""
    doc = nlp(text)
    lemmas = [
        token.lemma_ for token in doc if not token.is_punct and not token.is_space
    ]

    # drop digit+comma-only lemmas (e.g., "4,555") 371
    lemmas = [lemma for lemma in lemmas if not re.match(r"^[\d,]+$", lemma)]

    # drop lemmas with no letters (e.g., "°")
    lemmas = [lemma for lemma in lemmas if not re.match(r"^[^a-zA-Z]+$", lemma)]

    # strip punctuation (e.g., "J."" -> "J")
    lemmas = [re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", lemma) for lemma in lemmas]

    # strip [] (e.g., "pro[u]t" -> "prout")
    lemmas = [re.sub(r"[\[\]]", "", lemma) for lemma in lemmas]

    # lowercase
    lemmas = [lemma.lower() for lemma in lemmas]

    return lemmas


def get_term_counts(input_df):
    df = input_df.copy()
    print("Cleaning newlines and blanks ...")
    df["Transcription"] = df["Transcription"].fillna("")
    df["Transcription"] = df["Transcription"].str.replace(r"[\r\n]+", " ", regex=True)
    df["Transcription"] = df["Transcription"].str.replace(r"[\r]+", " ", regex=True)
    df["Transcription"] = df["Transcription"].str.replace(r"[\n]+", " ", regex=True)
    print("Using spacy model to get words ...")
    nlp = spacy.load("en_core_web_sm")
    df["words"] = df["Transcription"].apply(
        lambda x: lemmanize_text(x, nlp)
    )  # not deduped
    print(
        "Creating 'terms' column with normalized word lists (no stop words, non-words, and lowercased) . . ."
    )
    apostrophe_endings = [
        "s",  # is, has (he's, she's)
        "t",  # not (can't, won't)
        "ve",  # have (I've, you've)
        "ll",  # will (I'll, you'll)
        "d",  # had or would (I'd, she'd)
        "re",  # are (you're, they're)
        "m",  # am (I'm)
    ]
    stopwords = nlp.Defaults.stop_words
    has_digits = re.compile(r"\d").search

    # Terms excludes stop words and words with digits
    df["terms"] = df["words"].apply(
        lambda doc: [
            word.lower().strip()
            for word in doc
            if (
                (word.lower() not in stopwords)
                & (has_digits(word) is None)
                & (word.lower() not in apostrophe_endings)
            )
        ]
    )

    df["doc_word_count"] = df["words"].str.len()
    df["doc_term_count"] = df["terms"].str.len()
    df["doc_term_count_unique"] = df["terms"].apply(count_unique)
    df["doc_word_count_unique"] = df["words"].apply(count_unique)
    return df


def mk_btp_agg_bar_h_top_20_terms(enhanced_df):
    term_counts = enhanced_df["terms"].explode().value_counts().to_frame().reset_index()
    output_df = term_counts.sort_values("count", ascending=False)[0:20].sort_values(
        "count", ascending=True
    )
    output_df.to_csv("btp_agg_bar_h_top_20_terms.csv", index=False)
    print("Saved btp_agg_bar_h_top_20_terms.csv")


def mk_btp_agg_vbar_words_per_doc(enhanced_df):
    max_count = enhanced_df["doc_term_count"].max()
    ceiling = int(np.ceil(max_count / 100)) * 100
    bins = [0, 1] + list(range(100, ceiling + 100, 100))
    labels = ["0", "1-99"] + [f"{i}-{i + 99}" for i in range(100, ceiling, 100)]
    enhanced_df["Word Count"] = pd.cut(
        enhanced_df["doc_word_count"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )
    range_counts = (
        enhanced_df["Word Count"]
        .value_counts(sort=False)
        .to_frame("Number of Pages (Assets)")
        .reset_index()
    )
    range_counts = range_counts[["Number of Pages (Assets)", "Word Count"]]

    range_counts.to_csv("btp_agg_vbar_words_per_doc.csv", index=False)
    print("Saved btp_agg_vbar_words_per_doc.csv")


def mk_btp_agg_bar_h_document_count_by_campaign(enhanced_df):
    output_df = (
        enhanced_df["Campaign"]
        .value_counts()
        .sort_values(ascending=True)
        .to_frame()
        .reset_index()
    )
    output_df.to_csv("btp_agg_bar_h_document_count_by_campaign.csv", index=False)
    print("Saved btp_agg_bar_h_document_count_by_campaign.csv")


def mk_btp_agg_bar_h_word_count_by_campaign(enhanced_df):
    results = []
    for campaign in enhanced_df["Campaign"].unique():
        campaign_df = enhanced_df[enhanced_df["Campaign"] == campaign].copy()
        campaign_unique_word_count = count_unique_column(campaign_df["words"])
        results.append({
            "Campaign": campaign,
            "campaign_unique_word_count": campaign_unique_word_count,
        })
    # output_df = (
    #     enhanced_df.groupby("Campaign")["doc_word_count_unique"].sum().reset_index()
    # )
    output_df = pd.DataFrame(results)
    output_df = output_df.sort_values("campaign_unique_word_count", ascending=True)
    output_df.to_csv("btp_agg_bar_h_word_count_by_campaign.csv", index=False)
    print("Saved btp_agg_bar_h_word_count_by_campaign.csv")


def mk_btp_agg_image_formats(enhanced_df):
    jpeg = len(enhanced_df[enhanced_df["DownloadUrl"].str.contains("http") == True])
    tiff = len(enhanced_df[enhanced_df["TIFF"].str.contains("http") == True])
    jp2 = len(enhanced_df[enhanced_df["JP2"].str.contains("http") == True])

    results = [
        {"Images Available": "JPEG", "count": jpeg},
        {"Images Available": "TIFF", "count": tiff},
        {"Images Available": "JP2", "count": jp2},
    ]
    output_df = pd.DataFrame(results)
    output_df = output_df.sort_values("count", ascending=True)
    output_df.to_csv("btp_agg_image_formats.csv", index=False)
    print("Saved btp_agg_image_formats.csv")


def mk_btp_agg_top_count_list(df, column: str, n: int, output: str):
    """
    Creates a CSV of the counts for top n values in a given column of
    enhanced_df

    enhanced_df - cleaned/enhanced BTP dataframe
    column - dataframe column, which contains lists
    n - number of top values (e.g., top 20 values)
    output - file path of output CSV
    """
    tmp = df.copy()
    tmp[column] = tmp[column].fillna("[]")
    tmp[column] = tmp[column].apply(ast.literal_eval)
    output_df = tmp.explode(column).value_counts(column).head(n).reset_index()
    output_df = output_df.sort_values("count", ascending=True)
    output_df.to_csv(output, index=False)
    print(f"Saved {output}")


def main(
    csv: (
        "File path to aggregated CSV dataset file",
        "option",
        "c",
    ),
):
    df = pd.read_csv(csv, dtype=str)
    print("CSV read")

    mk_btp_agg_top_count_list(
        df, "ContributorNames", 20, "btp_agg_top_contributors.csv"
    )
    mk_btp_agg_top_count_list(df, "OriginalFormat", 20, "btp_agg_original_format.csv")
    mk_btp_agg_image_formats(df)
    mk_btp_agg_bar_h_document_count_by_campaign(df)

    enhanced_df = get_term_counts(df)
    # mk_btp_agg_bar_h_top_20_terms(enhanced_df)
    mk_btp_agg_vbar_words_per_doc(enhanced_df)
    mk_btp_agg_bar_h_word_count_by_campaign(enhanced_df)
    # enhanced_df.to_csv("all_data.csv")


if __name__ == "__main__":
    plac.call(main)
