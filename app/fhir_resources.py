from jinja2 import Template

related_person_fhir_template = Template('''
{
	"resourceType": "RelatedPerson",
	"id": "related-person-01",
	"patient": {
		"reference": "#patient-01"
	},
	"relationship": {
		"coding": [
			{
				"system": "{{ args['sdm_code_system'] }}",
				"code": "{{ args['sdm_code'] }}"
			}
		]
	},
	"name": [
		{
			"family": "{{ args['sdm_family_name'] }}",
			"given": {{ args['sdm_given_names'] }}
		}
	]
}
''')

patient_fhir_template = Template('''
{
	"resourceType": "Patient",
	"id": "patient-01",
	"identifier": [
		{
			"system": "[id-system-global-base]/ca-on-patient-hcn",
			"value": "{{ args['patient_hcn'] }}"
		}
	],
	"name": [
		{
			"family": "{{ args['patient_family_name'] }}",
			"given": {{ args['patient_given_names'] }}
		}
	],
	"gender": "male",
	"birthDate": "1926-02-24"
}
''')

practitioner_fhir_template = Template('''
{
	"resourceType": "Practitioner",
	"id": "practitioner-01",
	"identifier": [
		{
			"system": "[id-system-global-base]/ca-on-provider-upi",
			"value": "{{ args['provider_upi'] }}"
		}
	],
	"name": [
		{
			"family": "{{ args['provider_family_name'] }}",
			"given": {{ args['provider_given_names'] }}
		}
	],
	"telecom": [
		{
			"system": "phone",
			"value": "555-555-5555",
			"use": "work"
		}
	]
}
''')

organization_fhir_template = Template('''
{
	"resourceType": "Organization",
	"id": "organization-01",
	"identifier": [
		{
			"system": "[id-system-global-base]/ca-on-provider-upi",
			"value": "{{ args['org_upi'] }}"
		}
	],
	"name": "{{ args['org_name'] }}"
}
''')

consent_fhir_template = Template('''
{
	"resourceType": "Consent",
	"id": "example-ca-on-consent-profile-consent",
	"meta": {
		"lastUpdated": "2016-02-23T20:13:58-05:00"
	},
	"text": {
		"status": "additional",
		"div": "<div xmlns='http://www.w3.org/1999/xhtml'><p>%Some xhtml content%</p></div>"
	},
	"status": "active",
	"category": {
		"coding": [
			{
				"system": "http://hl7.org/fhir/v3/ActCode",
				"code": "INFA",
				"display": "information access"
			}
		]
	},
	"patient": {
		"reference": "patient-01"
	},
	"dateTime": "{{ args['submitted_date'] }}",
	{% if 'ECSDM' in args['override_type'] %}
	"consentingParty": [
		{
			"reference": "#related-person-1"
		}
	],
	{% endif %}
	"organization": [
		{
			"reference": "#organization-01"
		}
	],
	"policy": [
		{
			"authority": "http://ontario.ca"
		}
	],
	"except": [
		{
			"type": "permit",
			"actor": [
				{
					"role": {
						"coding": [
							{
								"system": "http://hl7.org/fhir/v3/ParticipationType",
								"code": "IRCP",
								"display": "information recipient"
							}
						]
					},
					"reference": {
						"reference": "#practitioner-01"
					}
				}
			],
			"action": [
				{
					"coding": [
						{
							"system": "http://hl7.org/fhir/consentaction",
							"code": "access",
							"display": "Access"
						}
					]
				}
			],
			"purpose": [
				{
					"system": "http://hl7.org/fhir/v3/ActReason",
					"code": "{{ args['override_purpose_code'] }}",
					"display": "{{ args['override_purpose_display']}}"
				}
			],
			"class": [
				{
					"system": "urn:ietf:rfc:3986",
					"code": "https://ehealthontario.ca/API/FHIR/Medications",
					"display": "Ontario Medications"
				}
			]
		}
	]
}
''')