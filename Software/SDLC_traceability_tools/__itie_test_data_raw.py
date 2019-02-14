_test_data_raw = """*+Background+*
See issue #4205.

*+URS4218.1+* When the buzzer sounds, it should also support 3rd-party alarm notification systems.

*+FRS4218.1+* When the buzzer sounds, the Alarm Contacts Relay will switch on. It will be off when the buzzer is not sounding.

*+SDS4218.1+* The FPGA needs to write to the Alarm Contacts Relay, which is ModD/DO28

*+SDS4218.2+* The logic for determining whether the Alarm Contacts Relay should be On or Off should be on the FPGA itself; On if the 'BuzzerOn (Cycles)' input is greater than 0, and Off otherwise.

*+Release Notes+*
* When the buzzer sounds, the Alarm Contacts Relay will switch on. It will be off when the buzzer is not sounding. With the appropriate hardware modifications, this will allow a third-party alarm notification system to detect when an Audible alarm has been triggered."""



_test_data_raw2 = """*+Background:+*
Agitation refers to the mixing of vessel contents using a vertical wheel impeller. 

*+URS3646+* 
* *+URS3646.1:+* The system will control agitation using automatic and manual control, and be able to turn agitation off. 
** Point 1
** Point 2
* *+URS3646.2:+* Automatic control will use speed as a set point to control PV. 
* *+URS3646.3:+* Manual control will provide a constant controller output regardless of PV. 
* *+URS3646.4:+* The system will use appropriate constraints to coerce outputs within appropriate operating limits. 
* *+URS3646.5:+* The system will detect agitation speed PV based on actual agitation speed as detected by a hardware sensor.
* *+URS3646.6:+* The system will report agitation speed PV in units of revolutions per minute (RPM)
* *+URS3646.7:+* The system will provide a standard UI allowing an operator access to system controls
* *+URS3646.8:+* The system will attempt to detect and recover from failures or abnormal operation. 

*+FRS3646+* Agitation Control [URS3646]
* Note: All system variables in the following items will be located under the category "Agitation" unless specified otherwise. 
* *FRS3646.1:* Controller output will be determined by whether the bioreactor is configured as an AirDrive or MagDrive system. [URS3646.1]
** *FRS3646.1.1:* (AirDrive) The controller will output a Main Gas flow rate request. Ref FRS3654. [URS3646.1]
** *FRS3646.1.2:* (MagDrive) the controller will output motor duty as a percentage of full scale. [URS3646.1]
** Note: For both configurations, output modules will be used as necessary to translate requests into electronic signals. 
* *FRS3646.2:* Agitation speed (a.k.a "RPM") will be detected based on a hardware sensor and used as the Process Value (PV). [URS3646.5]
** *FRS3646.2.1:* RPM detection will use a Hall Effect sensor to detect the passing of sensor magnets on the mixing impeller. [URS3646.5]
** *FRS3646.2.2:* The time between magnets passing will be used to infer the agitation speed based on the number of magnets. [URS3646.6]
** *FRS3646.2.3:* The number of magnets on the impeller will be configurable via System Variable "Number of Magnets". [URS3646.5]
** *FRS3646.2.4:* The number of intervals to average will be configurable via System Variable "Samples to Average". [URS3646.5]
** *FRS3646.2.5:* A measured PV will be coerced to 0 if the raw value is less than System Variable "Minimum (RPM)". [URS3646.6]
** Note: the magnets on the impeller will be assumed to be evenly spaced. 
* *FRS3646.3:* HMI [URS3646.7]
** *FRS3646.3.1:* Users will be able to select one of three modes: Auto, Manual, or Off. [URS3646.7]
** *FRS3646.3.2:* The current PV, SP, and mode will be displayed to the user with appropriate units. [URS3646.7]
** *FRS3646.3.3:* Interlock or broken status will be displayed to the user. [URS3646.7]
* *FRS3646.4:* Auto Mode Control [URS3646.2]
** Note: Tuning is beyond the scope of this FRS. Understanding of a PID controller is required to understand PID requirements. 
** *FRS3646.4.1:* Users will be able to select a Set Point (SP) as an RPM target. [URS3646.2]
** *FRS3646.4.2:* A standard PID controller will be used to seek SP based on the current PV. [URS3646.2]
** *FRS3646.4.3:* The PID Controller will use the following System Variables for standard PID input parameters, under the Agitation category: [URS3646.2]
*** *FRS3646.4.3.1:* (MagDrive) P-Gain: "P Gain (%/RPM)" [URS3646.2]
*** *FRS3646.4.3.2:* (AirDrive) P-Gain: "P Gain (LPM/RPM)" [URS3646.2]
*** *FRS3646.4.3.3:* I-Time: "I Time (min)" [URS3646.2]
*** *FRS3646.4.3.4:* D-Time: "D Time (min)" [URS3646.2]
*** *FRS3646.4.3.5:* α: "Alpha" [URS3646.2]
*** *FRS3646.4.3.6:* β: "Beta" [URS3646.2]
*** *FRS3646.4.3.7:* γ: "Gamma" [URS3646.2]
*** *FRS3646.4.3.8:* Linearity: "Linearity" [URS3646.2]
** *FRS3646.4.4:* (AirDrive) Output will not be greater than System Variable "Gas Auto Max (LPM)". [URS3646.2]
** *FRS3646.4.5:* (AirDrive) Output will not be less than System Variable "Gas Auto Min (LPM)" [URS3646.2]
** *FRS3646.4.6:* (AirDrive) When PV is 0, the controller will not output more than System Variable "Gas Auto Max Startup (LPM)", unless this would violate the "Gas Auto Max (LPM)" or "Gas Auto Min (LPM)" settings. [URS3646.2]
** *FRS3646.4.7:* (MagDrive) Output will not be greater than System Variable "Power Auto Max (%)". [URS3646.2]
** *FRS3646.4.8:* (MagDrive) Output will not be less than System Variable "Power Auto Min (%)". [URS3646.2]
** *FRS3646.4.9:* (MagDrive) When PV is 0, the controller will not output more than System Variable "Auto Max Startup (%)", unless this would violate the "Power Auto Max (%)" or "Power Auto Min (%)" settings. [URS3646.2]
** *FRS3646.4.10:* Pulse and Lookup Modes [URS3646.2]
*** *FRS3646.4.10.1:* The controller will automatically transition from Auto Mode to Pulse Mode when the following conditions are met: [URS3646.2]
**** *FRS3646.4.10.1.1:* Output is nonzero [URS3646.2]
**** *FRS3646.4.10.1.2:* PV has been 0 for longer than the time specified by System Variable "Pulse Mode Timeout". [URS3646.8]
**** *FRS3646.4.10.1.3:* PV has been 0 for less than the time specified by System Variable "Lookup Mode Timeout". [URS3646.2]
*** *FRS3646.4.10.2:* While in pulse mode, output will alternate between zero and maximum allowed output every few seconds. [URS3646.2]
*** *FRS3646.4.10.3:* The controller will automatically transition from Pulse Mode or Auto Mode to Lookup Mode when the following conditions are met: [URS3646.8]
**** *FRS3646.4.10.3.1:* Output is nonzero [URS3646.8]
**** *FRS3646.4.10.3.2:* PV has been 0 for longer than the time specified by System Variable "Lookup Mode Timeout". [URS3646.8]
*** *FRS3646.4.10.4:* (AirDrive) While in lookup mode, the system will output as SP * (System Variable "Lookup Factor (LPM/RPM)"). [URS3646.8]
*** *FRS3646.4.10.5:* (MagDrive) While in lookup mode, the system will output as SP * (System Variable "Lookup Factor (%/RPM)"). [URS3646.8]
*** Note: If lookup timeout is equal or less than the pulse timeout, then the system will never enter pulse mode. 
* *FRS3646.5:* Manual Mode Control [URS3646.3]
** *FRS3646.5.1:* (AirDrive) Users will be able to select a gas flow rate in LPM as a target. [URS3646.3]
** *FRS3646.5.2:* (MagDrive) Users will be able to select a power output in % as a target. [URS3646.3]
** *FRS3646.5.3:* The system will output the user's request when not limited by interlocks, settings, or other specified circumstances. [URS3646.3]
** *FRS3646.5.4:* (AirDrive) Output will not be greater than System Variable "Gas Manual Max (LPM)". [URS3646.4]
** *FRS3646.5.5:* (MagDrive) Output will not be greater than System Variable "Power Manual Max (%)". [URS3646.5]
* *FRS3646.6:* Off Mode Control [URS3646.4]
** *FRS3646.6.1:* (AirDrive) The controller will output no Main Gas request. [URS3646.4,URS3646.6]
** *FRS3646.6.2:* (MagDrive) The controller will output no power request. [URS3646.4, URS3646.5]
** *+FRS3646.7.1+* I'm a test item

*+SDS3646+*
* *+SDS3646.1:+* I'm an item [FRS3646.6.2]
* *+SDS3646.2:+* I'm another item [FRS3646.7.1]"""