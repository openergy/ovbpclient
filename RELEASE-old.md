# Releases

(p): patch, (m): minor, (M): major

## next

## 3.6.1
* p: on get_series_data, warn the user when the series are cut by the server 
(it outputs a maximum of 1.000.000 points per requests)

## 3.6.0
* m: possibility to update gates
* m: waiting for cleaner inputs available in create importer

## 3.5.0
* m: possibility to deactivate all resources
* m: get_unticleaner_config becomes configure_unitcleaner (external_name as input only)
* m: To retrieve a resource, no need to precise model anymore
* m: Within a project, get_gate, get_importer, get_cleaner, get_analysis available

## 3.4.0
* m: added check_last_files() for a project 

## 3.3.1
* p: possibity to clear unitcleaner configuration

## 3.3.0
* m: data_scan added for generators and projects
* p: get_full_list added to get more than 200 elements in request answer

## 3.2.0
* m: new project configuration features

## 3.1.6
* p: pip pytables/tables bug fix

## 3.1.5
* p: updated requirements and changed CI configuration

## 3.1.4
* p: compatibility with async series io

## 3.1.3
* p: default_resample_rule changed to default_resample_rules

## 3.1.2
* p: cleaner configurator debug

## 3.1.1
* p: cleaner: iter_importer_series debug
* p: deprecated methods removed

## 3.1.0
* m: oplatform v2 interface implemented

## 3.0.1
* p: works even if os adds hidden files in directories

## 3.0.0
* M: python 3.6
* m: local db added

## 2.1.0
* m: iter_unitcleaners and iter_importer_series added
* p: empty values of excel unitcleaners are now managed properly

## 2.0.2
* (m) pandas requirements were loosened

## 2.0.1
* (p): multiclean_config_model.xlsx added to MANIFEST.in

## 2.0.0
* (m): platform_to_excel added
* (M): cleaner batch_configure renamed to excel_to_platform
* (M): importer client kwarg removed
* (m): requests list_iter_all added
* (m): client management changed
* (m): util get_series_info added

## 1.0.0
* (m): list_iter_series created
* (M): first official release

## 0.3.0
* (m): client simplified
* (m): get_series_info added to api

## 0.2.0
* first referenced version
