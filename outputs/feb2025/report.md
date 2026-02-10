# Feb 2025 Snippet Report (TikTok vs X)

Window: 2025-02-13 to 2025-03-02 (election on 2025-02-23, Germany)

Normalization: shares within platform (total SoRs)

## RQ1: Moderation profiles (category and decision ground)

Top categories by share (per platform):

| platform_name   | category                                                            |    count |     share |
|:----------------|:--------------------------------------------------------------------|---------:|----------:|
| TikTok          | STATEMENT_CATEGORY_ILLEGAL_OR_HARMFUL_SPEECH                        | 52794251 | 0.482459  |
| TikTok          | STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE                        | 40580132 | 0.370841  |
| X               | STATEMENT_CATEGORY_PORNOGRAPHY_OR_SEXUALIZED_CONTENT                |    15207 | 0.298569  |
| X               | STATEMENT_CATEGORY_SCAMS_AND_FRAUD                                  |    12726 | 0.249858  |
| X               | STATEMENT_CATEGORY_SCOPE_OF_PLATFORM_SERVICE                        |     9955 | 0.195453  |
| X               | STATEMENT_CATEGORY_PROTECTION_OF_MINORS                             |     5549 | 0.108947  |
| TikTok          | STATEMENT_CATEGORY_NEGATIVE_EFFECTS_ON_CIVIC_DISCOURSE_OR_ELECTIONS |  6629817 | 0.0605865 |
| X               | STATEMENT_CATEGORY_VIOLENCE                                         |     2899 | 0.0569179 |
| TikTok          | STATEMENT_CATEGORY_VIOLENCE                                         |  4883518 | 0.0446279 |
| TikTok          | STATEMENT_CATEGORY_SCAMS_AND_FRAUD                                  |  1610669 | 0.0147191 |

Top decision grounds by share (per platform):

| platform_name   | decision_ground                      |     count |       share |
|:----------------|:-------------------------------------|----------:|------------:|
| X               | DECISION_GROUND_ILLEGAL_CONTENT      |     50933 | 1           |
| TikTok          | DECISION_GROUND_INCOMPATIBLE_CONTENT | 109419304 | 0.999926    |
| TikTok          | DECISION_GROUND_ILLEGAL_CONTENT      |      8078 | 7.38206e-05 |

## RQ2: Event dynamics around election

Pre vs post daily counts (mean, std, cv, pct change):

| platform_name   |           mean |        std |     min |     max | period   |        cv |   pct_change_post_vs_pre |
|:----------------|---------------:|-----------:|--------:|--------:|:---------|----------:|-------------------------:|
| TikTok          |    5.81177e+06 | 761720     | 4084292 | 6588889 | pre      | 0.131065  |                0.0992737 |
| X               | 2449.7         |    530.459 |    2022 |    3758 | pre      | 0.21654   |                0.456272  |
| TikTok          |    6.38873e+06 | 170557     | 6216863 | 6587615 | post     | 0.0266965 |                0.0992737 |
| X               | 3567.43        |   1150.02  |    2402 |    5808 | post     | 0.322366  |                0.456272  |

## RQ3: Automation reliance

Automated decision shares:

| automated_decision               |     count |       share | platform_name   |
|:---------------------------------|----------:|------------:|:----------------|
| AUTOMATED_DECISION_FULLY         | 105021438 | 0.959736    | TikTok          |
| AUTOMATED_DECISION_NOT_AUTOMATED |   4405944 | 0.0402636   | TikTok          |
| AUTOMATED_DECISION_NOT_AUTOMATED |     50930 | 0.999941    | X               |
| AUTOMATED_DECISION_FULLY         |         3 | 5.89009e-05 | X               |

Automated detection shares:

| automated_detection   |     count |     share | platform_name   |
|:----------------------|----------:|----------:|:----------------|
| Yes                   | 108027346 | 0.987206  | TikTok          |
| No                    |   1400036 | 0.0127942 | TikTok          |
| No                    |     50933 | 1         | X               |
