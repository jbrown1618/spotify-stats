import re

from data.repository import DataRepository


label_delimeter = re.compile(r'[,\/;]')
repository = DataRepository()

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
    "DISTRIBUTED THROUGH",
    "UNDER EXCLUSIVE LICENCE TO"
]

prefix_regexes = [
    re.compile(r"^\d{4}\s") # Year
]

all_standardized_by_all_labels = {}
most_common_by_standardized = {}


def standardize_record_labels():
    global all_standardized_by_all_labels
    global most_common_by_standardized
    labels_by_standardized = {}
    standardized_by_label = {}
    count_by_label = {}

    albums = repository.album_labels()

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

    for standardized, labels in labels_by_standardized.items():
        largest_count = 0
        most_common = None

        for label in labels:
            count = count_by_label[label]
            if count > largest_count or (count == largest_count and label < most_common):
                largest_count = count
                most_common = label

        most_common_by_standardized[standardized] = most_common

    standardized_labels_data = []
    for uri, all_labels in zip([uri for uri in albums["album_uri"]], [all_labels for all_labels in albums["album_label"]]):
        if all_labels.startswith('Republic Records - '):
            all_labels = 'Republic Records'
        
        if all_labels not in all_standardized_by_all_labels:
            continue
        
        standardized_labels = all_standardized_by_all_labels[all_labels]
        labels = [most_common_by_standardized[standardized] for standardized in standardized_labels]
        for label in labels:
            standardized_labels_data.append({
                "album_uri": uri,
                "album_standardized_label": label
            })
        
    repository.replace_standardized_labels(standardized_labels_data)


def split(record_labels_str: str):
    return [rl.strip() for rl in label_delimeter.split(record_labels_str)]


def standardize(record_label: str):
    record_label = record_label.strip().upper()
    record_label = strip_prefixes(record_label)
    record_label = strip_suffixes(record_label)
    return record_label


def strip_prefixes(record_label: str):
    changed = False

    for prefix_re in prefix_regexes:
        subbed = prefix_re.sub('', record_label)
        if subbed != record_label:
            record_label = subbed
            changed = True

    for prefix in prefixes:
        if record_label.startswith(prefix):
            record_label = record_label[len(prefix):].strip()
            changed = True

    # Recurse if we have made changes
    return strip_prefixes(record_label) if changed else record_label


def strip_suffixes(record_label: str):
    for suffix in suffixes:
        if record_label.endswith(suffix):
            return strip_suffixes(record_label[0:len(record_label) - len(suffix)].strip())
    return record_label


if __name__ == '__main__':
    standardize_record_labels()