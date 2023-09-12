# Monthly Enrollment report 
Report to plot monthly enrollments by site and surgery


## Version History
| Version   | Date | Description |
| ------ | ------ | ------ |
| 0.0.1 | 2022 | Original verion |
| 0.0.2 | 9/12/2023 | Conversion to Datastore model |


## Data Transformation Description
1. Report uses the data api for consented subjects
2. 'Enrolled' subjects are defined as all consented subjects who have not withdrawn early from the program 
3. Records for each site and surgery are rolled up on a monthly basis based on the orginal consent date
4. Actual enrollments are compared to expected enrollments that are defined according to the following table

### Enrollment Expectations
| MCC | Surgery   | Start  | Expected at Start | Additional Monthly | 
| ------ | ------ | ------ | ------ | ------ |
| 1 | TKA | 2/22 | 280 | 30 |
| 1 | Thoracic | 6/22 | 10 | 10 |
| 2 | Thoracic | 2/22 | 70 | 30 |
| 2 | TKA | 6/22 | 10 | 10 |
