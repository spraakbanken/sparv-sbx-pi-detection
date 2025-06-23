# sparv-sbx-pi-detection  

A plugin for [Sparv](https://spraakbanken.gu.se/sparv/) for detecting personal information in Swedish texts, especially learner essays (_note: performs noticeably worse on other domains, but the models used for annotation will likely be updated in the future)_.  

## Install

1. Install [Sparv](https://spraakbanken.gu.se/sparv/):  
```
pipx install sparv
sparv setup
```

2. Clone this plugin's repository:  
```
git clone https://github.com/spraakbanken/sparv-sbx-pi-detection
```

3. Inject the plugin into Sparv:  
```
pipx inject sparv /YOUR/PATH/TO/THE/PLUGIN/sparv-sbx-pi-detection
```

Alternatively to 2 & 3:
```
pipx inject sparv https://github.com/spraakbanken/sparv-sbx-pi-detection/archive/main.zip
```

_In case you need to uninstall the plugin:_  
```
pipx runpip sparv uninstall sparv-sbx-pi-detection
```

## Usage

In your `config.yaml` file for corpus configuration, you can now specify `sbx_pi_detection.pi` as a token annotation alongside one of the 6 annotation types (`basic, basic_iob, general, general_iob, detailed, detailed_iob`). The differences are described in [this publication](https://aclanthology.org/2025.nodalida-1.70/). Effectively, you need to include the following elements in your corpus configuration (substituting `general` for the annotation level you want):  

```
export:
  annotations:
    - <token>
    - <token>:sbx_pi_detection.pi
sbx_pi_detection:
  annotation_level: general
```

See also the [example corpus config file](https://github.com/spraakbanken/sparv-sbx-pi-detection/blob/main/sbx_pi_detection/testkorpus/config.yaml).

## Models

All of the models used in this plugin are classifiers based on [KB-BERT](https://huggingface.co/KB/bert-base-swedish-cased). They can be found [here](https://huggingface.co/collections/Turtilla/pi-detection-and-labeling-6822fbc8fbccfc2527c019ba). See [this publication](https://aclanthology.org/2025.nodalida-1.70/) for training details.  

See the webpage of the [Mormor Karl project](https://mormor-karl.github.io/) for more information on the work we do on automatic pseudonymization of research data.

## Citing

If you use this plugin e.g. in a publication, please cite it as:

[Språkbanken Text. sbx-swe-pi_detection-sparv [Analysis]. Språkbanken Text. https://doi.org/10.23695/6wp0-ds77](https://spraakbanken.gu.se/en/analyses/sbx-swe-pi_detection-sparv)

And

Maria Irena Szawerna, Simon Dobnik, Ricardo Muñoz Sánchez, and Elena Volodina. 2025. [The Devil’s in the Details: the Detailedness of Classes Influences Personal Information Detection and Labeling](https://aclanthology.org/2025.nodalida-1.70/). In _Proceedings of the Joint 25th Nordic Conference on Computational Linguistics and 11th Baltic Conference on Human Language Technologies (NoDaLiDa/Baltic-HLT 2025)_, pages 697–708, Tallinn, Estonia. University of Tartu Library.



