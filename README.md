# CAN-NPI: A Curated Open Dataset of Canadian Non-Pharmaceutical Interventions in Response to the Global COVID-19 Pandemic



[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Non-pharmaceutical interventions (NPIs) have been the primary tool used by governments and organizations to mitigate the spread of the ongoing pandemic of COVID-19. Natural experiments are currently being conducted on the impact of these interventions, but most of these occur at the subnational level - data not available in early global datasets. We describe the rapid development of the first comprehensive, labelled dataset of NPIs implemented at federal, provincial/territorial and municipal  levels in Canada to guide COVID-19 research. For each intervention, we provide: a) information on timing to aid in longitudinal evaluation, b) location to allow for robust spatial analyses, and c) classification based on intervention type and target population, including classification aligned with a previously developed measure of government response stringency. 

This initial dataset release spans January 1st to May 18th, 2020; further data updates to continue for the duration of the pandemic. This novel dataset enables robust, inter-jurisdictional comparisons of pandemic response, can serve as a model for other jurisdictions and can be linked with other information about case counts, transmission dynamics, health care utilization, mobility data and economic indicators to derive important insights regarding NPI impact. 

Here we show the count of recorded interventions by time in the dataset:

![Dataset Intervention Count](doc/img/intervention-count.png)

## Get the Data

You can use this direct link to get the data, which is stored in CSV format in this repository.

| Name  | Content | Rows | Size |  Link |
| --- | --- | --- | --- | --- |
| `npi_canada.csv` | All Canadian NPIs | 3,308 | 12 MB | [Download](https://raw.githubusercontent.com/jajsmith/COVID19NonPharmaceuticalInterventions/master/npi_canada.csv) |

Alternatively you can clone this GitHub repository, where the dataset is named `npi_canada.csv`. The repository also contains notebooks for visualizations and demonstrations with the data.

```
git clone git@github.com:jajsmith/COVID19NonPharmaceuticalInterventions.git
```


## Access and Details

The codebook and additional details can be found at https://docs.google.com/spreadsheets/d/1NSRyeY7XUjwUO8KICJCsOd2YKwuYaSAuM_yEnXMUbOY/edit?usp=sharing

**Time Period:** January 1, 2020 to May 18, 2020.


## Methods and Citations

If you find CAN-NPI helpful and use it in a scientific publication, we would appreciate you referencing the following paper:

CAN-NPI: A Curated Open Dataset of Canadian Non-Pharmaceutical Interventions in Response to the Global COVID-19 Pandemic. Liam G McCoy, Jonathan Smith, Kavya Anchuri, Isha Berry, Joanna Pineda, Vinyas Harish, Andrew T Lam, Seung Eun Yi, Sophie Hu, Canadian Open Data Working Group: Non-Pharmaceutical Interventions, Benjamin Fine. [medRxiv:10.1101:2020.04.17.20068560](https://www.medrxiv.org/content/10.1101/2020.04.17.20068460v1)


## Interested in Contributing?

If you have a correction or addition, please open a github issue.

Join the team or contact us at [howsmyflattening.ca](https://howsmyflattening.ca/#/home)

