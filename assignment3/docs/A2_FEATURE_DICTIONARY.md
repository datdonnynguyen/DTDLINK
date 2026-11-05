# DTDLINK Stage 3 feature dictionary

## Purpose and scope

This document defines the Stage 3 contract that converts one URL string into a
stable numeric feature vector. The implementation is in
`src/dtdlink_ml/url_parser.py` and `src/dtdlink_ml/feature_extraction.py`.

The extractor analyses text locally. It does not open the URL, resolve DNS,
refresh the Public Suffix List, or use `type`/`target` to calculate a feature.
Every boolean is stored as `0` or `1`. Counts and lengths are non-negative
integers.

## Parser output (metadata, not model features)

The parser preserves `raw_url`, trims edge whitespace only in `analysis_url`,
and returns scheme, user-info, username, password, host, port, path, query,
fragment, registrable domain, subdomain and TLD. It also returns:

- `has_scheme`: whether an explicit scheme was supplied;
- `host_is_ip`: whether the parsed host is an IPv4 or IPv6 address;
- `parse_ok`: whether a web host was obtained without a fatal parse problem;
- `issues`: stable issue codes such as `missing_scheme`, `invalid_port`,
  `missing_host`, `unsupported_scheme` and `control_character`.

Missing schemes are recoverable. For example, `example.com/login` is analysed
as a host plus path while the original text and `missing_scheme` issue remain.
The public-suffix parser uses the installed offline snapshot with caching and
network refresh disabled.

## Non-model columns in the processed CSV

| Column | Purpose |
|---|---|
| `url` | Original URL text retained for audit, grouping and error analysis. |
| `type` | Original source label retained for later subgroup evaluation. |
| `target` | Approved binary label; copied only, never read by feature calculations. |
| `registrable_domain` | Domain grouping key for the Stage 4 leakage-safe split. |
| `tld` | Parsed public suffix retained for later training-only transformations. |
| `parse_issues` | Pipe-separated parser issue codes for audit and diagnostics. |

These six columns must not all be passed directly to a numeric model. Stage 4
will select `FEATURE_NAMES` as model inputs and use the metadata for splitting,
analysis and labels.

## Numeric feature schema

The order below is fixed by `FEATURE_NAMES`. Changing a name, definition or
order requires updating tests, this dictionary and saved-model metadata.

| # | Feature | Type | Calculation and interpretation | Important limitation |
|---:|---|---|---|---|
| 1 | `url_length` | Count | Characters in the trimmed analysis URL. | Length alone does not imply danger. |
| 2 | `host_length` | Count | Characters in the parsed host. | Zero when no host can be recovered. |
| 3 | `path_length` | Count | Characters in the parsed path. | Encoded text remains encoded. |
| 4 | `query_length` | Count | Characters after `?` and before `#`. | Does not judge query semantics. |
| 5 | `fragment_length` | Count | Characters after `#`. | Fragments normally are not sent to the server but can mislead users. |
| 6 | `tld_length` | Count | Characters in the offline public suffix. | Zero for IPs and suffixes absent from the snapshot. |
| 7 | `dot_count` | Count | Number of `.` characters in the URL. | Includes dots outside the host. |
| 8 | `hyphen_count` | Count | Number of `-` characters in the URL. | A hyphen is common in legitimate URLs too. |
| 9 | `digit_count` | Count | Number of Unicode digit characters. | Counts digits in every URL component. |
| 10 | `special_character_count` | Count | Characters for which `isalnum()` is false. | Includes normal URL separators as well as unusual symbols. |
| 11 | `subdomain_count` | Count | Non-empty labels before the registrable domain. | Depends on the bundled Public Suffix List snapshot. |
| 12 | `path_segment_count` | Count | Non-empty path pieces separated by `/`. | Repeated slashes produce no empty segment count. |
| 13 | `query_parameter_count` | Count | Parameters parsed from the query, including blank values. | A malformed query can produce zero. |
| 14 | `suspicious_term_count` | Count | Number of distinct configured security terms present as tokens. | Hand-maintained vocabulary; context is not understood. |
| 15 | `brand_token_count` | Count | Number of distinct configured brand tokens anywhere in the URL. | The list is deliberately small and cannot cover every brand. |
| 16 | `non_ascii_count` | Count | Characters with code point above 127. | Non-ASCII is not inherently suspicious. |
| 17 | `parse_issue_count` | Count | Number of parser issue codes. | Recoverable issues such as missing scheme are included. |
| 18 | `has_scheme` | Boolean | `1` when the input explicitly supplies a scheme. | Missing scheme is common in the course dataset. |
| 19 | `uses_https` | Boolean | `1` when the parsed scheme is `https`. | HTTPS does not guarantee a trustworthy site. |
| 20 | `has_explicit_port` | Boolean | `1` when a valid port is written explicitly. | Invalid ports are reflected by parse features instead. |
| 21 | `has_nonstandard_port` | Boolean | `1` when port differs from HTTP 80 or HTTPS 443. | Non-standard ports have legitimate uses. |
| 22 | `has_ip_host` | Boolean | `1` when host is valid IPv4 or IPv6. | Private/test IPs and public IPs are not distinguished here. |
| 23 | `has_at_symbol` | Boolean | `1` when raw URL text contains `@`. | `@` may be legitimate user-info; parser identifies the host after it. |
| 24 | `has_userinfo` | Boolean | `1` when the authority contains text before its last `@`. | Does not expose a password as a feature value. |
| 25 | `has_suspicious_term` | Boolean | `1` when at least one configured security term is present. | Same vocabulary limitation as the count. |
| 26 | `brand_in_subdomain` | Boolean | `1` when an exact brand token appears before the registrable domain. | Requires successful public-suffix parsing. |
| 27 | `brand_in_userinfo` | Boolean | `1` when an exact brand token appears before `@`. | Useful for misleading forms such as `paypal.com@example.net`. |
| 28 | `brand_in_path_or_query` | Boolean | `1` when an exact brand token appears in path or query. | Marketing/referral URLs can legitimately contain brands. |
| 29 | `has_unicode` | Boolean | `1` when any URL character is non-ASCII. | Internationalised domains are legitimate. |
| 30 | `has_confusable_unicode` | Boolean | `1` for a documented subset of common Greek/Cyrillic look-alikes. | Conservative heuristic, not a complete Unicode UTS #39 implementation. |
| 31 | `has_percent_encoding` | Boolean | `1` when `%` is followed by two hexadecimal digits. | Percent encoding is normal in many URLs. |
| 32 | `has_encoded_separator` | Boolean | `1` for encoded `/`, `:`, `@` or backslash. | These encodings can be legitimate. |
| 33 | `has_control_character` | Boolean | `1` for ASCII control characters in analysis text. | Input is retained for audit rather than silently deleted. |
| 34 | `host_has_punycode` | Boolean | `1` when a host label starts with `xn--`. | Punycode supports legitimate internationalised domains. |
| 35 | `has_unknown_tld` | Boolean | `1` for a non-IP host with no suffix in the offline snapshot. | Means “not recognised by this snapshot”, not “malicious”. |
| 36 | `parse_ok` | Boolean | `1` when a host is recovered without a fatal issue. | It is parser health, not a safety verdict. |

## Fixed vocabularies

Suspicious terms:
`account`, `auth`, `confirm`, `credential`, `login`, `password`, `secure`,
`signin`, `update`, `verify`, `wallet`.

Brand tokens:
`adobe`, `amazon`, `apple`, `facebook`, `google`, `instagram`, `linkedin`,
`microsoft`, `netflix`, `office`, `outlook`, `paypal`, `whatsapp`.

Terms are matched as decoded lowercase alphanumeric tokens, not arbitrary
substrings. Therefore `apple.example.com` matches `apple`, while
`pineapple.example.com` does not.

## Assignment 1 signals and Stage 3 implementation

| Committed signal | Stage 3 field(s) |
|---|---|
| URL/address length | `url_length` plus component lengths |
| Host is an IP address | `has_ip_host` |
| Subdomain count | `subdomain_count` |
| Brand name in subdomain | `brand_in_subdomain`; user-info and path/query variants are also retained |
| Look-alike/confusable characters | `has_unicode`, `non_ascii_count`, `has_confusable_unicode`, `host_has_punycode` |
| Unusual TLD | Parsed `tld` metadata and `has_unknown_tld`; frequency-based rarity is deferred as described below |
| `@` in URL | `has_at_symbol`, `has_userinfo`, `brand_in_userinfo` |

## Fit-dependent TLD feature — deliberately deferred

“How rare is this TLD in the dataset?” cannot be calculated safely from all
641,113 rows before splitting. That would let validation/test distribution
information enter model preparation. Stage 3 therefore retains the parsed
`tld` but does not calculate full-dataset TLD frequency.

After the domain-aware split in Stage 4, a TLD frequency/rarity mapping may be
fitted on training rows only, stored with the final pipeline, and applied to
validation, test and new URLs. Unknown values must receive a documented
fallback. This preserves the Assignment 1 idea without data leakage.

## Example

Input:

```text
https://paypal.com@security-check.example.net:8443/login/verify?account=123&next=%2Fhome#step2
```

Important parser result:

```text
userinfo            = paypal.com
host                = security-check.example.net
registrable_domain  = example.net
subdomain           = security-check
tld                 = net
port                = 8443
```

Selected features:

```text
url_length              = 94
host_length             = 26
path_length             = 13
query_length            = 24
subdomain_count         = 1
has_at_symbol           = 1
has_userinfo             = 1
brand_in_userinfo        = 1
has_ip_host              = 0
has_nonstandard_port     = 1
has_percent_encoding     = 1
parse_ok                 = 1
```

No individual signal proves that the URL is dangerous. Later models learn how
combinations of signals relate to the approved target.
