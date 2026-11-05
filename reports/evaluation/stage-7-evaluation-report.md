# Stage 7 - Final evaluation

Random Forest (100 trees), threshold 0.5, trained on the train split only.
Positive = phishing/malware/defacement, negative = benign.

## Test results

Test URLs: 126,949.

| Metric | Value |
|---|---:|
| accuracy | 0.917888 |
| precision | 0.852199 |
| recall | 0.915521 |
| f1 | 0.882726 |
| true_negative | 77,294 |
| false_positive | 6,804 |
| false_negative | 3,620 |
| true_positive | 39,231 |

## By original label

| Type | URLs | Correct | FN | FP | Correct rate |
|---|---:|---:|---:|---:|---:|
| benign | 84098 | 77294 | 0 | 6804 | 0.9191 |
| phishing | 18757 | 15635 | 3122 | 0 | 0.8336 |
| malware | 3643 | 3274 | 369 | 0 | 0.8987 |
| defacement | 20451 | 20322 | 129 | 0 | 0.9937 |

## Errors compared with correct predictions

| Group | n | Median URL length | Has scheme | HTTPS | IP host | Suspicious term |
|---|---:|---:|---:|---:|---:|---:|
| TN | 77294 | 47.0 | 0.0666 | 0.0065 | 0.0000 | 0.0431 |
| FP | 6804 | 38.0 | 0.1096 | 0.0078 | 0.0000 | 0.0025 |
| TP | 39231 | 52.0 | 0.7084 | 0.0319 | 0.0592 | 0.0357 |
| FN | 3620 | 45.0 | 0.1387 | 0.0041 | 0.0000 | 0.0077 |

## Example errors

Up to 5 per error type and label, taken in URL-id order.

- FP, type=benign, p=0.5779, length=30, scheme=0, suspicious_term=0

```text
"music.yahoo.com/claudia-brant/"
```

- FP, type=benign, p=0.8247, length=24, scheme=0, suspicious_term=0

```text
"sjsj.3owl.com/scott.html"
```

- FP, type=benign, p=0.8040, length=22, scheme=0, suspicious_term=0

```text
"mszq.narod.ru/list.htm"
```

- FP, type=benign, p=0.5241, length=54, scheme=0, suspicious_term=0

```text
"wiki.aeriagames.com/lastchaos/index.php?title=Guardian"
```

- FP, type=benign, p=0.7040, length=27, scheme=0, suspicious_term=0

```text
"music.yahoo.com/april-wine/"
```

- FN, type=phishing, p=0.3917, length=34, scheme=0, suspicious_term=0

```text
"www.freewebs.com/swampfootrecords/"
```

- FN, type=phishing, p=0.4356, length=40, scheme=0, suspicious_term=0

```text
"www.freebsd.org/doc/en/articles/nanobsd/"
```

- FN, type=phishing, p=0.4757, length=62, scheme=0, suspicious_term=0

```text
"www.outerarm.demon.co.uk/graphics/graphics_povray_objects.html"
```

- FN, type=phishing, p=0.1156, length=55, scheme=0, suspicious_term=0

```text
"globetrotter-games.com/index.htm?E&amp;game/eDetect.htm"
```

- FN, type=phishing, p=0.3159, length=36, scheme=0, suspicious_term=0

```text
"groups.yahoo.com/group/gem-announce/"
```

- FN, type=malware, p=0.0852, length=46, scheme=0, suspicious_term=0

```text
"almazdental.ru/wp-includes/pomo/panel/gate.php"
```

- FN, type=malware, p=0.1735, length=90, scheme=1, suspicious_term=0

```text
"http://9779.info/%E6%A0%91%E5%8F%B6%E7%B2%98%E8%B4%B4%E7%94%BB%E6%95%99%E6%A1%88%E7%94%BB/"
```

- FN, type=malware, p=0.2140, length=96, scheme=1, suspicious_term=0

```text
"http://9779.info/%E5%B0%8F%E7%8F%AD%E5%B9%BC%E5%84%BF%E5%89%AA%E7%BA%B8%E8%B4%B4%E7%94%BB/2.html"
```

- FN, type=malware, p=0.1744, length=84, scheme=1, suspicious_term=0

```text
"http://9779.info/%E8%B1%86%E5%AD%90%E7%B2%98%E8%B4%B4%E7%94%BB%20%E6%B1%BD%E8%BD%A6/"
```

- FN, type=malware, p=0.1670, length=90, scheme=1, suspicious_term=0

```text
"http://9779.info/%E6%A0%91%E5%8F%B6%E5%B0%8F%E5%A5%B3%E5%AD%A9%E7%B2%98%E8%B4%B4%E7%94%BB/"
```

- FN, type=defacement, p=0.2092, length=120, scheme=1, suspicious_term=0

```text
"http://slaviacapital.com/tlacove-spravy-eng/slavia-capital-sold-heating-firm-energy-snina-to-grafobal-group-energy/print"
```

- FN, type=defacement, p=0.4188, length=88, scheme=1, suspicious_term=0

```text
"http://slaviacapital.com/tlacove-spravy/jaroslav-zidek-novou-tvarou-restauracie-albrecht"
```

- FN, type=defacement, p=0.0730, length=119, scheme=1, suspicious_term=0

```text
"http://caprobi.com/eventos-seminarios/10-congreso-internacional-de-propietarios-de-inmuebles-14-de-abril-del-2011-.html"
```

- FN, type=defacement, p=0.4218, length=86, scheme=1, suspicious_term=0

```text
"http://slaviacapital.com/tlacove-spravy/slavia-capital-predala-teplaren-energy-snina-2"
```

- FN, type=defacement, p=0.3768, length=101, scheme=1, suspicious_term=0

```text
"http://copremon.com.br/fique-por-dentro/487-cooperativas-de-credito-movimentam-r-4275-mi-em-2012.html"
```

## Limitations

- Labels come from the dataset and were not checked by visiting the URLs.
- The split keeps domains apart but is not a split by time.
- The probabilities are not calibrated.
