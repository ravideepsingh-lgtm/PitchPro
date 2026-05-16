import argparse
import json
import math
from pathlib import Path

import pandas as pd


SERVICE_KEYS = ['customers', 'catalog', 'trustseal', 'maximiser', 'star', 'leader', 'exporter', 'plPlus']
TURNOVER_KEYS = ['0 - 40L', '40L - 1.5Cr', '1.5Cr - 5Cr', '5Cr - 25Cr', '25Cr - 100Cr', '>100Cr']

CARD_DEFINITIONS = [
    ('dlp', 'Location', 'preferred_location', [('Global', 'eq', 'Global'), ('India', 'eq', 'India'), ('Local', 'eq', 'Local'), ('Foreign', 'eq', 'Foreign')]),
    ('blDau', 'BL Active', 'bl_active_days_30', [('4-7', 'range', (4, 7)), ('8-12', 'range', (8, 12)), ('>=13', 'gte', 13)]),
    ('engagement', 'BL Engaged', 'bl_usage_percent', [('60-70%', 'range', (60, 70)), ('70-80%', 'range', (70, 80)), ('> 80%', 'gt', 80)]),
    ('majorCities', 'Major Cities', 'major_cities', [('4-6', 'range', (4, 6)), ('7-9', 'range', (7, 9)), ('> 10', 'gt', 10)]),
    ('rank', 'A Rank', 'rank_a_mcat', [('4-6', 'range', (4, 6)), ('7-9', 'range', (7, 9)), ('> 10', 'gt', 10)]),
    ('callSuccess', 'Call Success', 'call_success_percent', [('70-80%', 'range', (70, 80)), ('80-90%', 'range', (80, 90)), ('> 90%', 'gt', 90)]),
]

TRUST_DEFINITIONS = [('GST', 'gst'), ('IEC', 'iec'), ('TAN', 'tan')]


def clean_text(value):
    if pd.isna(value):
        return ''

    text = str(value).strip()
    return '' if text.lower() == 'nan' else text


def number(value):
    text = clean_text(value).replace('%', '').replace(',', '')
    if not text:
        return math.nan

    try:
        return float(text)
    except ValueError:
        return math.nan


def yes_no(value):
    return 'Yes' if number(value) == 1 else 'No'


def fmt_number(value):
    numeric_value = number(value)
    if math.isnan(numeric_value):
        return '-'

    if numeric_value.is_integer():
        return str(int(numeric_value))

    return f'{numeric_value:.1f}'


def fmt_percent(value):
    numeric_value = number(value)
    if math.isnan(numeric_value):
        return '-'

    if numeric_value.is_integer():
        return f'{int(numeric_value)}%'

    return f'{numeric_value:.1f}%'


def turnover_bucket(value):
    return {
        '0 - 40 L': '0 - 40L',
        '40 L - 1.5 Cr': '40L - 1.5Cr',
        '1.5 - 5 Cr': '1.5Cr - 5Cr',
        '5 - 25 Cr': '5Cr - 25Cr',
        '25 - 100 Cr': '25Cr - 100Cr',
        '100 - 500 Cr': '>100Cr',
        '> 500 Cr': '>100Cr',
    }.get(clean_text(value), '')


def service_key(value):
    return {
        'Catalog': 'catalog',
        'TrustSEAL': 'trustseal',
        'Maximiser': 'maximiser',
        'Star': 'star',
        'Leader': 'leader',
        'Exporter': 'exporter',
        'Featured Leader': 'plPlus',
        'Industry Leader': 'plPlus',
    }.get(clean_text(value), '')


def category_mask(segment, card_key, column, kind, rule):
    if column not in segment.columns:
        return pd.Series([False] * len(segment), index=segment.index)

    if kind == 'eq':
        mask = segment[column].map(clean_text).str.lower() == str(rule).lower()
    else:
        values = segment[column].map(number)

        if kind == 'range':
            low, high = rule
            mask = (values >= low) & (values <= high)
        elif kind == 'gte':
            mask = values >= rule
        elif kind == 'gt':
            mask = values > rule
        else:
            mask = pd.Series([False] * len(segment), index=segment.index)

    if card_key == 'callSuccess':
        mask = mask & (segment['success_call'].map(number) >= 10)

    return mask


def pct(count, total):
    if not total:
        return '0%'

    value = (count / total) * 100
    if value == 0:
        return '0%'

    if value < 1:
        return f'{value:.1f}%'

    return f'{round(value)}%'


def lead_record(row):
    glid = clean_text(row.get('glusr_usr_id'))

    return {
        'glid': glid or '-',
        'company': clean_text(row.get('company')) or '-',
        'city': clean_text(row.get('city')) or '-',
        'vintage': clean_text(row.get('vintage')) or '-',
        'location': clean_text(row.get('preferred_location')) or '-',
        'blActive': fmt_number(row.get('bl_active_days_30')),
        'blConsumed': fmt_percent(row.get('bl_usage_percent')),
        'majorCities': fmt_number(row.get('major_cities')),
        'aRank': fmt_number(row.get('rank_a_mcat')),
        'callSuccess': fmt_percent(row.get('call_success_percent')),
        'gst': yes_no(row.get('gst')),
        'iec': yes_no(row.get('iec')),
        'tan': yes_no(row.get('tan')),
    }


def sample_leads(segment, mask):
    columns = [
        'glusr_usr_id',
        'company',
        'city',
        'vintage',
        'preferred_location',
        'bl_active_days_30',
        'bl_usage_percent',
        'major_cities',
        'rank_a_mcat',
        'call_success_percent',
        'gst',
        'iec',
        'tan',
    ]
    sampled = segment.loc[mask, columns].drop_duplicates(subset=['glusr_usr_id']).head(12)
    return [lead_record(row) for _, row in sampled.iterrows()]


def build_client_segment_data(csv_path):
    df = pd.read_csv(csv_path, dtype=str)

    for column in [
        'glusr_usr_id',
        'company',
        'city',
        'Turnover',
        'preferred_location',
        'vintage',
        'highest_service',
        'rank_a_mcat',
        'gst',
        'tan',
        'iec',
        'bl_usage_percent',
        'success_call',
        'call_success_percent',
        'bl_active_days_30',
        'major_cities',
    ]:
        if column not in df.columns:
            df[column] = ''

    df['_turnoverKey'] = df['Turnover'].map(turnover_bucket)
    df['_serviceKey'] = df['highest_service'].map(service_key)
    df['_glid'] = df['glusr_usr_id'].map(clean_text)

    result = {}
    valid_base = df[df['_turnoverKey'].isin(TURNOVER_KEYS)].copy()

    for service in SERVICE_KEYS:
        service_df = valid_base if service == 'customers' else valid_base[valid_base['_serviceKey'] == service]
        segments = [('all', service_df)] + [
            (turnover, service_df[service_df['_turnoverKey'] == turnover]) for turnover in TURNOVER_KEYS
        ]

        for turnover, segment in segments:
            total = int(segment['_glid'].replace('', pd.NA).nunique())
            payload = {'total': total, 'trust': [], 'cards': [], 'leads': {}}

            for label, column in TRUST_DEFINITIONS:
                mask = segment[column].map(number) == 1
                count = int(segment.loc[mask, '_glid'].replace('', pd.NA).nunique())
                data_key = f'trust|{label}'
                payload['trust'].append({'label': label, 'value': pct(count, total), 'count': count, 'dataKey': data_key})
                payload['leads'][data_key] = sample_leads(segment, mask)

            for card_key, title, column, rows in CARD_DEFINITIONS:
                card_rows = []

                for label, kind, rule in rows:
                    mask = category_mask(segment, card_key, column, kind, rule)
                    count = int(segment.loc[mask, '_glid'].replace('', pd.NA).nunique())
                    data_key = f'{card_key}|{label}'
                    card_rows.append({'label': label, 'value': pct(count, total), 'count': count, 'dataKey': data_key})
                    payload['leads'][data_key] = sample_leads(segment, mask)

                payload['cards'].append({'key': card_key, 'title': title, 'rows': card_rows})

            result[f'{service}|{turnover}'] = payload

    return result


def write_module(data, output_path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    source = '// Generated from Paid Clients 20260515.xlsb / Client Base.\n'
    source += '// Run `npm run refresh:data` when the workbook changes.\n'
    source += 'export const clientSegmentData = '
    source += json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    source += ';\n\n'
    source += "export function getSegmentKey(serviceKey, turnoverKey) {\n  return `${serviceKey}|${turnoverKey ?? 'all'}`;\n}\n\n"
    source += 'export function getClientSegment(selectedCard) {\n  return clientSegmentData[getSegmentKey(selectedCard.serviceKey, selectedCard.turnoverKey)] ?? null;\n}\n\n'
    source += 'export function getClientSegmentLeads(selectedCard, dataKey) {\n  return getClientSegment(selectedCard)?.leads?.[dataKey] ?? [];\n}\n'
    output_path.write_text(source, encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--csv', required=True)
    parser.add_argument('--out', required=True)
    args = parser.parse_args()

    output_path = Path(args.out)
    data = build_client_segment_data(args.csv)
    write_module(data, output_path)
    print(f'Generated {output_path} ({len(data)} segments)')


if __name__ == '__main__':
    main()
