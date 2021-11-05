"""
Contains a dct with regular expressions (regexes). It is imported by
the parser.py script to find vars in the raw text of the press-release.
Each key-value pair represents:
{
    # regex description
    regex_name : <raw regex> # raw string with future regular expression
}
Actual regular expression would be build by:
(import re)
the_regex = re.compile(<raw regex>, re.DOTALL)
value = the_regex.findall[0]
The '|' symbol is used to present a number of distinct variants of
a regex:
<variant 1> | <variant 2> | <variant 3>
In this case output of <<the_regex.findall[0]>> would be a tuple. So
parser.py has a <<choose_value>> static method to deal with
('', '<value>', '') tuple to fetch a <value> from it.
RUSSIAN SUMMARY:
В файле приводится словарь с регулярными выражениями. С его помощью скрипт
parser.py ищет нужные переменные в тексте релиза.
"""

regexes = dict(

    # новые случаи COVID-19 в России за сутки
    russia_new_cases=r'\s{0,3}'.join((
        r'случа\w+\s{0,3}\w{0,5}\s{0,3}коронавирусной инфекции',
        r'\(?COVID\W19\)?\s{0,3}\W?\s{0,3}(\d+\s?\d+)',
        r'в\s{0,3}\d+\s{0,3}рег'
    )),

    # прирост новых случаев в России за сутки в %
    russia_current_pace=r'\s{0,3}'.join((
        r'\(?(\+.+%)\)?\s{0,3}коронавирусной инфекции',
        r'в\s{0,3}\d+'
    )),

    # число смертей в России за сутки
    russia_new_deaths='|'.join((
        # 1
        r'За последние сутки умер\w{0,2} {0,3}(\d+\s?\d+) {0,3}челове',
        # 2
        r'Умер\w{0,2} за последние сутки {0,3}(\d+\s?\d+) {0,3}челове',
        # 3
        r'\s{0,3}'.join((
          r'За последние сутки подтвержден\w?',
          r'(\d+\s?\d+) {0,3}летальн\w+ случа'
        )),
        # 4
        r'\s{0,3}'.join((
          r'За последние сутки подтвержден\w?',
          r'(\d+\s?\d+) {0,3}смерт'
        ))
    )),

    # число выздоровевших в России за сутки
    russia_new_recovered='|'.join((
        # 1
        r'\s{0,3}'.join((
            r'За \w{0,10}\s?сутки выписан\w?',
            r'(\d+\s?\d+)\s{0,3}челов'
        )),
        # 2
        r'\s{0,3}'.join((
            r'За \w{0,10}\s?сутки выписан\w?',
            r'по выздоровлени\w?',
            r'(\d+\s?\d+)\s{0,3}челов'
        ))
    )),

    # общая сумма случаев COVID-19 в России за все время
    russia_total_cases='|'.join((
        # 1
        r'\s{0,3}'.join((
            r'Российской Федерации нарастающим итогом зарегистрирован\w{0,1}',
            r'(\d+\s?\d+\s?\d+)\s{0,3}случа'
        )),
        # 2
        r'\s{0,3}'.join((
            r'России нарастающим итогом зарегистрирован\w{0,1}',
            r'(\d+\s?\d+\s?\d+)\s{0,3}случа'
        ))
    )),

    # число новых случаев в Москве за сутки
    moscow_new_cases='|'.join((
        # 1
        r'.*'.join((
          r'Распределение по субъектам',
          r'Москва\s+\W?\s{0,3}(\d+\s?\d+) {0,6}[\n\r]',
          r'В Российской Федерации нарастающ'
        )),
        # 2
        r'.*'.join((
          r'Распределение по субъектам',
          r'Москва\s+\W?\s{0,3}(\d+\s?\d+) {0,6}[\n\r]',
          r'В России нарастающ'
        ))
    )),


    # число смертей в Москве за сутки
    moscow_new_deaths='|'.join((
        # 1
        r'.*'.join((
            r'За последние сутки умер\w{0,2} {1,3}\d+\s?\d{0,3} {0,3}человек',
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'Умер\w* за весь период'
        )),
        # 2
        r'.*'.join((
            r'За последние сутки умер\w{0,2} {1,3}\d+\s?\d{0,3} {0,3}человек',
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период умер'
        )),
        # 3
        r'.*'.join((
            r''.join((
                r'Умер\w{0,2} за последние сутки\w{0,2}',
                r' {1,3}\d+\s?\d+ {0,3}человек'
            )),
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период умер'
        )),
        # 4
        r'.*'.join((
            r''.join((
                r'Умер\w{0,2} за последние сутки\w{0,2}',
                r' {1,3}\d+\s?\d+ {0,3}человек'
            )),
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'Умер\w{0,2} за весь период'
        )),
        # 5
        r'.*'.join((
            r'\s{0,3}'.join((
                r'За последние сутки подтвержден\w{0,1}',
                r'\d+\s?\d+ {0,3}летальн\w+ случа'
            )),
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период по России умер'
            )),
        # 6
        r'.*'.join((
            r'\s{0,3}'.join((
                r'За последние сутки подтвержден\w{0,1}',
                r'\d+\s?\d+ {0,3}смерт\w{1,2}'
            )),
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период по России умер'
            ))
    )),

    # число выздоровевших в Москве за сутки
    moscow_new_recovered='|'.join((
        # 1
        r'.*'.join((
            r'За последние сутки выписан\w*.*человек\w?',
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период выписан'
            )),
        # 2
        r'.*'.join((
            r'За последние сутки выписан\w*.*человек\w?',
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'Выписан\w* за весь'
            )),
        # 3
        r'.*'.join((
            r'За прошедшие сутки выписан\w?\s{0,3}по выздоровлени\w?.*человек',
            r'Москва\s+\W?\s?(\d+\s?\d+)',
            r'За весь период выписан'
            ))
        )),

    # "золотая цитата"
    golden_cite=r'(За последние сутки в.*без клинических проявлений)\.?\s',

    # общее число смертей от COVID-19 в России за все время
    russia_total_deaths='|'.join((
        # 1
        r'За весь период умер\w{0,2}\s{0,4}(\d+\s?\d+)\s{0,4}челов',
        # 2
        r'Умер\w{0,2} за весь период\s{0,4}(\d+\s?\d+)\s{0,4}челов',
        # 3
        r'За весь период по России умер\w{0,2}\s{0,4}(\d+\s?\d+)\s+челов'
    )),

    # общее число выздоровевших в России за все время
    russia_total_recovered='|'.join((
        # 1
        r'За весь период выписан\w?\s+(\d+\s?\d+\s?\d+)',
        # 2
        r'\s{0,3}'.join((
            r'За весь период выписан\w? по выздоровлени\w?',
            r'по России\s{0,3}\W?',
            r'(\d+\s?\d+\s?\d+)'
        ))
    ))
)
