import pandas as pd
import re

suffixes = [
    "RECORDS",
    "LABEL",
    "LABELS",
    "MUSIC",
    "LIMITED",
    "*",
    ",",
    ".",
    "LLC", 
    "INC",
    "LTD"
]

prefixes = [
    "DISTRIBUTED BY",
    "UNDER EXCLUSIVE LICENCE TO"
]

def standardize_record_labels(albums: pd.DataFrame):
    labels_by_standardized = {}
    standardized_by_label = {}
    count_by_label = {}
    all_standardized_by_all_labels = {}

    for record_labels_str in albums["album_label"]:
        if record_labels_str.startswith('Republic Records - '):
            # Special case - this label seems to create special sublabels for various artists
            record_labels_str = "Republic Records"

        record_labels = split(record_labels_str)
        for record_label in record_labels:
            if record_label in count_by_label:
                count_by_label[record_label] = count_by_label[record_label] + 1
            else:
                count_by_label[record_label] = 1

            standardized = standardize(record_label)
            if standardized == '':
                continue

            standardized_by_label[record_label] = standardized

            if standardized in labels_by_standardized:
                labels_by_standardized[standardized].add(record_label)
            else:
                labels_by_standardized[standardized] = {record_label}

            if record_labels_str in all_standardized_by_all_labels:
                all_standardized_by_all_labels[record_labels_str].add(standardized)
            else:
                all_standardized_by_all_labels[record_labels_str] = {standardized}

    most_common_by_standardized = {}

    for standardized, labels in labels_by_standardized.items():
        largest_count = 0
        most_common = None

        for label in labels:
            count = count_by_label[label]
            if count > largest_count:
                largest_count = count
                most_common = label

        most_common_by_standardized[standardized] = most_common

    standardized_labels_data = []
    for uri, all_labels in zip([uri for uri in albums["album_uri"]], [all_labels for all_labels in albums["album_label"]]):
        if all_labels.startswith('Republic Records - '):
            all_labels = 'Republic Records'
        
        standardized_labels = all_standardized_by_all_labels[all_labels]
        labels = [most_common_by_standardized[standardized] for standardized in standardized_labels]
        for label in labels:
            standardized_labels_data.append({
                "album_uri": uri,
                "album_standardized_label": label
            })
        
    return pd.DataFrame(standardized_labels_data)


def split(record_labels_str: str):
    delimeter = r'[,\/]'
    return [rl.strip() for rl in re.split(delimeter, record_labels_str)]


def standardize(record_label: str):
    record_label = record_label.strip().upper()
    record_label = strip_prefixes(record_label)
    record_label = strip_suffixes(record_label)
    return record_label



def strip_prefixes(record_label: str):
    for prefix in prefixes:
        if record_label.startswith(prefix):
            return strip_prefixes(record_label[len(prefix):].strip())
    return record_label


def strip_suffixes(record_label: str):
    for suffix in suffixes:
        if record_label.endswith(suffix):
            return strip_suffixes(record_label[0:len(record_label) - len(suffix)].strip())
    return record_label
