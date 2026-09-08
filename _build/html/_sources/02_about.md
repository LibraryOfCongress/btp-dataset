## About the Data

### I. About this Dataset

Version 1 | Data last updated 2026-08-28

The **By the People Comprehensive Transcription Data Package** provides access to over 425,000 Library of Congress digital pages transcribed by public volunteers, through the Library of Congress’s [By the People](https://crowd.loc.gov/) crowdsourced transcription program. The dataset combines full text transcriptions from contributors, tags from contributors, selected metadata fields from Library of Congress staff, and URL pointers to download images as [IIIF](https://www.loc.gov/apis/micro-services/image-services/) JPEG, JP2, or TIFF. Pages range in formats including letters, books, reports, pamphlets, journals, sketchbooks, field notes, audio logs, organizational records, notated music, and other documents and manuscript materials. This dataset is aggregated from the transcriptions of all By the People [completed transcription campaigns](https://crowd.loc.gov/campaigns/completed/) that have been fully processed and made available for individual download as [ZIP packages in the Selected Datasets online collection](https://www.loc.gov/collections/selected-datasets/?fa=contributor:by+the+people+(program)).

The Library of Congress thanks all By the People contributors for sharing their time and knowledge with us to make this dataset possible. 


### II. What's included?

The data package is available in CSV, JSON, and Parquet formats. 

See a file list on {doc}`03_download`.

### III. Data fields

The CSV, JSON, and Parquet files contain the following fields. See {doc}`01_at_a_glance` for an example record. 

Each row of the CSV and each entry in the JSON and Parquet represent one transcribed "Asset" from By the People. 

:::{table} Data fields (CSV, JSON, and Parquet data files)

| Field         | Description | Included in Selected Datasets source dataset? |
|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----|
| Campaign         | This is the highest hierarchical level in the arrangement of collections on By the People (example:  "Susan B. Anthony Papers").  It often maps to a Library collection, but may also be part of a collection or combine multiple collections. This field displays the campaign’s title. | Yes |
| Project          | This is the second-highest hierarchical level of collections on By the People. Projects may map to an existing subset of a digital collection, such as an archival series, or may be a grouping of related items uniquely organized for By the People. This field displays the project’s title. | Yes |
| Item             | This is the third-highest hierarchical level of collections on By the People, typically representing a folder, letter, document, or diary. This field displays the item title. | Yes |
| ItemId           | This is the identifier for the item (see above for definition). This numerical identifier is consistent across the By the People website and in loc\.gov. The item and metadata are usually located on the Library’s website at  https://www.loc.gov/item/[ItemID]/ | Yes |
| Asset            | This is the identifier for the individual asset image. It is also referred to colloquially as the “page” by By the People contributors and Community Managers. This identifier is used on the By the People site and on loc\.gov. | Yes |
| AssetId          | Another identifier for an individual asset image, used by By the People internal databases. | Yes |
| AssetStatus      | This indicates the status of the asset in the peer review workflow – Not Started, In Progress, Needs Review, or Completed. Dataset assets will always be marked as “completed.” | Yes |
| DownloadURL      | This link provides access to the image file for the asset from which the transcription was created. This URL is typically the IIIF JPEG image API. | Yes |
| Transcription    | This is the text created by the By the People contributors, representing the written content of the DownloadURL image and corresponding to the Asset. This field will be blank for assets that contributors marked “Nothing to transcribe”. | Yes |
| Tags             | These are all the tags that have been applied to the asset. If there is more than one tag, the tags are delimited by a semicolon and space. | Yes |
| DatasetId        | The unique identifier of the source dataset,  from the Selected Datasets online collection. For example, if the DatasetId is "2020446971", this asset came from the dataset at https://loc.gov/item/2020446971. | Yes |
| SourceDatasetFilename        | The exact filename of the CSV within the source dataset, from which this asset's basic metadata was retrieved. This is a public file, generally within the downloadable ZIP file of the source dataset. | Yes |
| RightsAdvisory   | Rights Advisory statement pulled from the Selected Datasets dataset item. | Yes |
| TIFF             | URL to the source asset as a TIFF image file. Blank if there is no TIFF for this asset. | No |
| JPEG             | URL to the source asset as a IIIF JPEG image file. Blank if there is no TIFF for this asset. | No |
| SegmentUrl      | URL to the asset (page) on loc\.gov. Blank if the asset no longer has a public page. | No |
| SubjectHeadings  |Item-level subject headings list pulled from live loc\.gov item pages, formatted as a list of strings like ['value 1', 'value 2', 'value 3']. | No |
| ContributorNames |  Item-level contributors list pulled from live loc\.gov item pages, formatted as a list of strings. | No |
| OriginalFormat   | Original physical format of the item (e.g., "manuscripts", "photos"), formatted as a list of strings. | No |
| CallNumber       | Call number or equivalent (e.g., "series: Series 1. General Correspondence. 1833-1916"), formatted as a list of strings. | No |
| Repository       | Source of the material (e.g., "Manuscript Division" or  "Library of Congress Prints and Photographs Division Washington, D.C. 20540 USA http://hdl.loc.gov/loc.pnp/pp.print"), formatted as a list of strings. | No |
| Notes       | Additional explanatory notes. | No |

:::

### IV. How was the data created?  

By the People transcripts and tags are created by anonymous and registered contributors online. Transcription contributors are instructed to transcribe the text as written, including misspellings and abbreviations. Formatting is generally not preserved with the exception of line breaks. Minimal markup does include “?” for illegible or unclear text, square brackets around deleted text, and square brackets and asterisks around marginalia `([*example*])`. Pages without text have blank transcriptions.

Once a transcription is finished, it must be reviewed by a registered contributor. A transcription may undergo multiple rounds of edits before being completed. Finally, transcriptions are spot-checked by Library of Congress subject matter experts.

After a transcription [campaign](https://crowd.loc.gov/campaigns/completed/) is completed, the transcriptions are processed and made publicly available in two formats:

1. The transcripts are added into the online collections on the Library's website (loc\.gov) to enhance search and accessibility. For example, By the People transcript are available on [this sample page](https://www.loc.gov/resource/rbc0001.2019hazard80347/?sp=2&st=text&r=-0.439,-0.094,1.877,1.877,0).  
2. The campaign transcripts are packaged into a CSV file and made available as a dataset in the [Selected Datasets] Collection(https://www.loc.gov/collections/selected-datasets/?fa=contributor:by+the+people+%28program%29). 

In order to construct this aggregated dataset, all By the People datasets in the Selected Datasets Collection are then combined into a single CSV. Each row of that CSV represents one page (or "asset"). Each page's original Item record is queried in order to confirm the current IIIF JPEG URL, TIFF image URL (if applicable), and harvest additional descriptive  from the source Item record. 

For each source dataset, a JSON file and a Parquet file are also generated from the aggregated CSV. These files have the same data that can be found in the CSV. The JSON and Parquet files are named using the `SourceDatasetFilename` field, to match the filenames of the source datasets from the Selected Datasets Collection. 


### V. Source material  

#### Historical background
The historical background of source materials varies by campaign. Contextual information can be found in the individual READMEs associated with each campaign, in the Selected Datasets Collection. Completed campaigns are described on the By the People's [Completed Campaigns](https://crowd.loc.gov/campaigns/completed/) page. 

#### Original format of source material  

Original formats vary. The most common format is handwritten manuscripts, and other formats include books, reports, pamphlets, journals, sketchbooks, field notes, audio logs, organizational records, and notated music.


#### Digitization  

Digitization processes and quality vary. Most materials were digitized far in advance of being transcribed through By the People, some using older digitization techniques than others, including digitization from microfilm.  

### VI. Rights and use

#### Transcriptions and Tags
`Transcription` and `Tags` fields in the CSV, JSON, and Parquet data files: The tags and transcribed text in this dataset were created by volunteers and can be used in many different ways. For certain campaigns, some of the contents of these fields may be subject to copyright protection. Each campaign has a rights statement, which can be found in the `RightsAdvisory` field of the CSV, JSON, and Parquet data files. 

#### Metadata
All other fields in the CSV, JSON, and Parquet data files are U.S. government works not subject to copyright in the United States and have no known copyright restrictions. These fields are in the Public Domain.

### VII. Contact  

For more info, contact the By the People team on their [Ask a Librarian](https://ask.loc.gov/crowd) page. For technical support, contact the [Computational Data Services](https://ask.loc.gov/dataservices) team.


