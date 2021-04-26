
# Receptacle - Rule 12-7

**Rule ID:** 12-7  
**Rule Description:** User RMR Receptacle Power in Baseline RMR?  
**Rule Assertion:** Baseline RMR = User RMR  
**Appendix G Section:** Section G3.1-12 Modeling Requirements for the Proposed design  
**Appendix G Section Reference:** None  

**Applicability:** All required data elements exist for B_RMR and U_RMR  
**Applicability Checks:**  

  1. Rule 12-4 = True  

**Manual Check:** None  
**Evaluation Context:** Each Data Element  
**Data Lookup:** None  

## Rule Logic:  

- **Applicability Check 1:** ```if (rule-12-4.status == TRUE):```

- Get the receptacle load of each space in the building segment in the User model: ```for building_segment_user in U_RMR.building.building_segments:```  

  - For each thermal_block in building segment: ```thermal_block_user in building_segment_user.thermal_blocks:```  

  - For each zone in thermal block: ```zone_user in thermal_block_user.zones:```  

  - For each space in thermal zone: ```space_user in zone_user.spaces:```  

    - Get the receptacle load in the space: ```space_receptacle = space.miscellaneous_equipments```  

    - Get the total miscellaneous_equipment in the space: ```space_total_misc_equipment_user = sum( equipment.peak_usage for equipment in space_user.miscellaneous_equipments )```  

    - Get matching space from Baseline RMR: ```space_baseline = match_data_element(B_RMR, spaces, space_user.name)```  

      - Get the total miscellaneous_equipment in the space: ```space_total_misc_equipment_baseline = sum( equipment.peak_usage for equipment in space_baseline.miscellaneous_equipments )```  

    **Rule Assertion:** ```space_total_misc_equipment_user == space_total_misc_equipment_baseline```  
