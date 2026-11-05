# Stage 6 - Clustering the dangerous URLs

Data: 127,256 potentially dangerous URLs from the train split.
2 constant features removed, 34 features used. Labels, URL text and domain are not used as features.

## Choosing k

Features scaled with StandardScaler. K-means with n_init=10 and seed=42, k from 2 to 8. Silhouette is computed on the same random sample of 2,000 rows for every k, and the k with the highest silhouette is used.
Chosen: **k=7**, silhouette=0.2923.

| k | Inertia | Silhouette | Smallest cluster | Largest cluster |
|---|---:|---:|---:|---:|
| 2 | 3913159.0 | 0.1620 | 41802 | 85454 |
| 3 | 3581522.4 | 0.1988 | 2951 | 82537 |
| 4 | 3308138.3 | 0.2446 | 2951 | 76486 |
| 5 | 3054857.4 | 0.2561 | 1986 | 53774 |
| 6 | 2860147.5 | 0.2840 | 1069 | 51140 |
| 7 | 2651904.7 | 0.2923 | 53 | 47106 |
| 8 | 2411111.7 | 0.2858 | 53 | 51454 |

## Clusters

Differences are in standard deviations from the mean of all selected URLs.

### Cluster 0 - 40,662 URLs (31.95%)

Short URLs written without http(s):// (parse_issue_count is mostly just missing_scheme).

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_scheme | 0.0000 | 0.6700 | -1.42 |
| parse_issue_count | 1.0000 | 0.3305 | +1.42 |
| special_character_count | 4.4115 | 10.5268 | -0.86 |
| url_length | 31.2154 | 63.3123 | -0.70 |
| query_parameter_count | 0.0397 | 1.0809 | -0.52 |

URLs closest to the centre:

```text
"www.sulekhab2b.com/vastrakala/"
"s1.zetaboards.com/ShadowsideRPG/"
"home.earthlink.net/~sturges47/"
```

### Cluster 1 - 26,369 URLs (20.72%)

Long URLs with many query parameters, often CMS-style pages.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| query_parameter_count | 4.5379 | 1.0809 | +1.72 |
| query_length | 77.8015 | 18.7317 | +1.49 |
| special_character_count | 19.9750 | 10.5268 | +1.32 |
| url_length | 119.4955 | 63.3123 | +1.23 |
| has_scheme | 0.9989 | 0.6700 | +0.70 |

URLs closest to the centre:

```text
"http://www.cootecsan.com/index.php?option=com_content&view=article&id=121:beneficios-adicionales&catid=55&Itemid=141"
"http://www.tmftabriz.com/index.php?option=com_content&view=article&id=161:azaran600&catid=1:latest-news&Itemid=67"
"http://www.meridianranch.com/index.php?option=com_content&view=article&id=121:creekview-grill&catid=7:recreation&Itemid=190"
```

### Cluster 2 - 53 URLs (0.04%)

Odd text: lots of control/Unicode characters and parse issues, probably broken data or encoding.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_control_character | 1.0000 | 0.0004 | +48.53 |
| has_unknown_tld | 0.6604 | 0.0003 | +37.71 |
| non_ascii_count | 47.8302 | 0.0457 | +29.07 |
| parse_ok | 0.7736 | 0.9999 | -21.58 |
| has_unicode | 1.0000 | 0.0029 | +18.57 |

URLs closest to the centre:

```text
"\u00f6\u00c2\u0087\u00e7\u00bc\u00d2\u00e9\u00af\u00bf\u0084\u00caZ\u0089\u00ad\u0017\u00b0Vr\u00b3\u00d1\u0099\u00cf\u009f/_n\bDaG\u00b3\u00aa\\a\u00ed\u00be\u008dVor\u009d\u0012\u00a48\t\u00b2\u00f6\u00c6\u00c7\u0093\u0089\u00c7\u00d3\u00ce\u00f0\u00b7\u0088l\u00c24k\u00a3f\u0099\u00ad\u00db\u00b9\u0093\u0081G;\u00a4\u00da\u00c3J\u00f2\u00a4\u00b0\u00074Ta\u008b\u00bao\u00af\u0095\u0007\u0083\u0098"
"\u00dc\u008d\u00d7\u00e9\u00cc\u0089\u00c9uTEq<\u00b8\u000e\u00ab\u0003\u00cfn\u00d3u\u00cfB\u0003JI\u00aaW\u00d9n\"\u00c7h\u00834\t\u0094\u0086\u0011+Q\u008d\u0096j\"\u00e4*\u00b4J\u00f1.\tT|J\u00f6\u00e4\u00c6\u00b0!nq\u00c4\u008c\u00ad\u0099\u00de\u009f\u00ff\u00832\u00e1\u0081\u001d\u00ba\u00bbsr\u0004\u001d\u00f2N\u00fa\u0017Z\u0018b\u009d\u00dc\u009a\u0098\u00a4\u00d2y\u0007\u001aS\u00d5Q\u00b5"
"\u00e0\u0095G\u00c4\u00afnLC\"\u0016\u00e0\fH\u0092\u00d9\u009d\u00e9\u00ef\u00f8\u00b3\u00ae\u001c\u0015\u00d8\u00ab\u00b77 A\u00df$\u00ef\u00a1u\u00a1\u00c6-\u00d9\u0099\u00a9\u009b\u00cd\u00a6\u0094}\u00a5=U\u001bR\u00c9\u008c$6\u00e9\u0014\u00b3s\u0014"
```

### Cluster 3 - 5,730 URLs (4.50%)

Words like login/signin/verify and brand names in different parts of the URL.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_suspicious_term | 0.7576 | 0.0344 | +3.97 |
| suspicious_term_count | 0.8993 | 0.0408 | +3.71 |
| brand_token_count | 0.3447 | 0.0179 | +2.44 |
| brand_in_path_or_query | 0.1743 | 0.0080 | +1.87 |
| brand_in_subdomain | 0.1667 | 0.0075 | +1.84 |

URLs closest to the centre:

```text
"http://web196.login-4.loginserver.ch/Joomla25/templates/atomic/zyqhjnnl.php?id=1836636"
"http://53.com-id9533371.thoughtoholics.net/en/signin.php?sslchannel=true"
"http://53.com-id3105365.thoughtoholics.net/en/signin.php?sslchannel=true"
```

### Cluster 4 - 4,386 URLs (3.45%)

IP-address hosts with no normal domain name or TLD.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_ip_host | 1.0000 | 0.0577 | +4.04 |
| tld_length | 0.0000 | 2.8999 | -2.19 |
| subdomain_count | 0.0000 | 0.7193 | -0.92 |
| dot_count | 3.6689 | 2.6928 | +0.84 |
| has_scheme | 0.9993 | 0.6700 | +0.70 |

URLs closest to the centre:

```text
"http://45.95.168.207/bins/jKira.m68k"
"http://185.53.88.182/AB4g5/kiga.mpsl"
"http://185.53.88.182/AB4g5/kiga.mips"
```

### Cluster 5 - 47,106 URLs (37.02%)

Normal-looking URLs with a scheme, several path segments and few query parameters.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_scheme | 0.9941 | 0.6700 | +0.69 |
| parse_issue_count | 0.0059 | 0.3305 | -0.69 |
| path_length | 30.8032 | 20.8434 | +0.47 |
| query_parameter_count | 0.2537 | 1.0809 | -0.41 |
| path_segment_count | 2.3973 | 1.8177 | +0.40 |

URLs closest to the centre:

```text
"http://www.niobestudio.com/index.php/visita-virtual-360"
"http://www.aims4claims.com/about-aims/success-stories.html"
"http://www.aims4claims.com/about-aims/aims-management.html"
```

### Cluster 6 - 2,950 URLs (2.32%)

Mostly IP-address hosts with non-standard ports.

| Feature | Cluster mean | Overall mean | Difference / SD |
|---|---:|---:|---:|
| has_nonstandard_port | 1.0000 | 0.0232 | +6.49 |
| has_explicit_port | 1.0000 | 0.0233 | +6.47 |
| has_ip_host | 0.9892 | 0.0577 | +3.99 |
| tld_length | 0.0325 | 2.8999 | -2.17 |
| dot_count | 3.9810 | 2.6928 | +1.10 |

URLs closest to the centre:

```text
"http://112.27.88.109:41610/Mozi.m"
"http://36.105.56.188:49541/Mozi.m"
"http://111.43.223.33:44254/Mozi.m"
```

## Stability and limitations

Adjusted Rand index between seed 42 and seeds 43/44: {'43': 0.9774936697767315, '44': 0.6015675091420426}.
Sample points per cluster in the silhouette sample: {'0': 639, '1': 425, '2': 1, '3': 102, '4': 53, '5': 736, '6': 44}. Very small clusters barely appear in the sample.
- K-means puts every URL in some cluster, even unusual ones.
- Big domains contribute many URLs, so a cluster is not the same as one campaign.
- Only the dangerous URLs of the train split are clustered; the classifier is not changed.
